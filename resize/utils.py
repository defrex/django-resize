
from __future__ import print_function
import os
import logging

try:
    from StringIO import StringIO
except ImportError:
    from io import BytesIO as StringIO

from django.core.files.storage import default_storage
from django.core.files.images import ImageFile
from django.utils import six
from django.core.exceptions import SuspiciousFileOperation

from PIL import Image, ExifTags

logger = logging.getLogger(__name__)


def get_file_path(img_file):
    if isinstance(img_file, six.string_types):
        return img_file
    if hasattr(img_file, 'path'):
        return img_file.path
    elif img_file is not None:
        return img_file.name


def get_thumb_name(img_file, size):
    if img_file is None:
        return ''
    filehead, filetail = os.path.split(get_file_path(img_file))
    return os.path.join(
        filehead,
        '{}_thumbs/v1_at_{}.jpg'.format(filetail, str(size)),
    )


def parse_size(size):
    "parses the size argument, returning (width, height)"

    w, h = None, None

    if isinstance(size, int) or size.isdigit():
        w = size

    elif size != 'auto':
        s = size.split('x')
        if s[0].isdigit(): w = int(s[0])
        if s[1].isdigit(): h = int(s[1])

    if w is not None: w = int(w)
    if h is not None: h = int(h)

    return w, h

def lower(a, b):
    if a < b:
        return a
    else:
        return b


def get_scaled_down_size(current_size, target_size):
    """
    Calculates a scaled size for the image. The result will fit on the target's
    smallest side.
    """
    target_w, target_h = target_size
    cur_w, cur_h = current_size

    def scale_w():
        w = lower(target_w, cur_w)
        return int(w), int((float(cur_h) / float(cur_w)) * w)

    def scale_h():
        h = lower(target_h, cur_h)
        return int((float(cur_w) / float(cur_h)) * h), int(h)

    if target_w is None and target_h is None:
        return int(cur_w), int(cur_h)

    elif target_h is None:
        return scale_w()

    elif target_w is None:
        return scale_h()

    elif target_w >= cur_w or target_h >= cur_h:
        return int(cur_w), int(cur_h)

    elif cur_w <= target_w and cur_h <= target_h:
        return int(cur_w), int(cur_h)

    elif cur_w < target_w and cur_h > target_h:
        return int(target_w), int(cur_h)

    elif cur_w > target_w and cur_h < target_h:
        return int(cur_w), int(target_h)

    # tall image
    elif target_h == target_w:
        if cur_h >= cur_w:
            return scale_w()
        else:
            return scale_h()

    elif target_h >= target_w:
        return scale_h()

    # wide image
    elif target_w >= target_h:
        return scale_w()

    raise ValueError('Impossible error: Aron sucks at math. '
                     'target:%s, current:%s' % (str(target_size), str(current_size)))


def get_exif(img):
    "returns the image's exif data as a dict"
    try:
        exif = hasattr(img, '_getexif') and img._getexif()
        if exif:
            exif = exif.items()
            exif = dict(exif)
            return exif
    except (IOError, IndexError):
        pass

    return {}


def resize_image(img_file, size=100, storage=default_storage):
    '''
    The size argument can be in one of two forms: width or widthxheight. "auto"
    is an acceptable value for either. Some examples:

    resize_image(img, 50) - this will set with width to 50, with the height scaled
    accordingly.

    resize_image(img, 'auto') - this won't resize the image at all

    resize_image(img, '50x50') - the width and height will be 50px, causing the
    image to be letterboxed (never stretched).

    resize_image(img, 'autox50') - this will set the height and scale the width

    '''
    if img_file is None:
        return

    if hasattr(img_file, 'storage'):
        storage = img_file.storage

    thumb_filename = get_thumb_name(img_file, size)

    if storage is None:
        exists = os.path.isfile(thumb_filename)
    else:
        exists = storage.exists(thumb_filename)

    # if the image wasn't already resized, resize it
    if not exists:
        img_file.seek(0)
        img = Image.open(img_file)

        exif = get_exif(img)

        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation] == 'Orientation':
                break

        if orientation in exif:
            if exif[orientation] == 3:
                img = img.rotate(180, Image.BICUBIC, True)
            elif exif[orientation] == 6:
                img = img.rotate(270, Image.BICUBIC, True)
            elif exif[orientation] == 8:
                img = img.rotate(90, Image.BICUBIC, True)

        current_size = [float(x) for x in img.size]
        target_size = parse_size(size)
        scaled_size = get_scaled_down_size(current_size, target_size)

        img = img.resize(scaled_size, Image.ANTIALIAS)

        target_size = list(target_size)
        target_size[0] = target_size[0] or img.size[0]
        target_size[1] = target_size[1] or img.size[1]

        # transparent
        # bg = Image.new('RGBA', target_size)
        # bg.putalpha(Image.new('L', target_size, color=0))

        bg = Image.new('RGB', target_size, color=(255, 255, 255))
        box = (int((target_size[0] - int(img.size[0])) / 2),
               int((target_size[1] - int(img.size[1])) / 2))
        bg.paste(img, box)
        img = bg

        if img.mode != 'RGB': img = img.convert('RGB')

        if storage is None:
            thumb_dir = '/'.join(thumb_filename.split('/')[:-1])
            try:
                os.makedirs(thumb_dir)
            except OSError:
                pass
            img.save(thumb_filename, 'JPEG', quality=80)
        else:
            image_io = StringIO()
            img.save(image_io, 'JPEG', quality=80)
            storage.save(thumb_filename, ImageFile(image_io))

    return thumb_filename
