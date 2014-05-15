
import os
import logging

from django.core.cache import cache
from django.utils import six

from PIL import Image, ExifTags

logger = logging.getLogger(__name__)


def get_file_path(img_file):
    if isinstance(img_file, six.string_types):
        return img_file
    if hasattr(img_file, 'path'):
        return img_file.path
    else:
        return img_file.name


def get_thumb_name(img_file, size):
    # CAUTION: changing this number will force a re-render of all images
    resize_version = 1

    filename = get_file_path(img_file)
    filehead, filetail = os.path.split(filename)
    thumb_dir = '%s_thumbs' % filetail
    thumb_name = '%s/v%i_at_%s.jpg' % (thumb_dir, resize_version, str(size))
    thumb_filename = os.path.join(filehead, thumb_name)

    return thumb_name, thumb_filename


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

    elif target_w >= cur_w or target_h >= cur_h:
        return int(cur_w), int(cur_h)

    elif cur_w <= target_w and cur_h <= target_h:
        return int(cur_w), int(cur_h)

    elif cur_w < target_w and cur_h > target_h:
        return int(target_w), int(cur_h)

    elif cur_w > target_w and cur_h < target_h:
        return int(cur_w), int(target_h)

    elif target_h is None:
        return scale_w()

    elif target_w is None:
        return scale_h()

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
    except IOError:
        pass

    return {}


def get_current_size(img_file):
    img = Image.open(get_file_path(img_file))

    w, h = img.size

    exif = get_exif(img)

    for orientation in ExifTags.TAGS.keys():
        if ExifTags.TAGS[orientation] == 'Orientation':
            break

    if orientation in exif and exif[orientation] >= 5:
        h, w = w, h

    return w, h


def resize_image(img_file, size=100):
    '''
    This template tag resizes images.

    It will resize the image once, saving the result to desk. Subsiquest calls
    for the same resize will then result in returning the old image, so that
    the resizing action is cached.

    The size argument can be in one of two forms: width or widthxheight. "auto"
    is an acceptable value for either. Some examples:

    {{ img|resize:50 }} - this will set with width to 50, with the height scaled
    accordingly.

    {{ img|resize:'auto' }} - this won't resize the image at all

    {{ img|resize:'50x50' }} - the width and height will be 50px, causing the
    image to be letterboxed (never stretched).

    {{ img|resize:'autox50' }} - this will set the height and scale the width

    '''
    if img_file is None: return ''

    thumb_name, thumb_filename = get_thumb_name(img_file, size)

    # if the image wasn't already resized, resize it
    if not os.path.exists(thumb_filename):
        img = Image.open(get_file_path(img_file))

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
        box = ((target_size[0] - int(img.size[0])) / 2,
               (target_size[1] - int(img.size[1])) / 2)
        bg.paste(img, box)
        img = bg

        if img.mode != 'RGB': img = img.convert('RGB')

        path = os.path.split(thumb_filename)[0]
        if not os.path.isdir(path): os.mkdir(path)

        img.save(thumb_filename, 'JPEG', quality=90)

    if hasattr(img_file, 'url'):
        urlhead, urltail = os.path.split(img_file.url)
        return '%s/%s' % (urlhead, thumb_name)

    else:
        return thumb_name


def get_new_size(img_file, input_size):
    "calculates the new size for the image, based on the desired size argument"
    thumb_name, thumb_filename = get_thumb_name(img_file, input_size)
    cache_key = 'thumb_size_%s' % thumb_filename
    sizes = cache.get(cache_key, {})
    if input_size in sizes and not input_size == 698:
        return sizes[input_size]

    target_size = parse_size(input_size)

    img = Image.open(get_file_path(img_file))
    current_w, current_h = img.size

    exif = get_exif(img)
    for orientation in ExifTags.TAGS.keys():
        if ExifTags.TAGS[orientation] == 'Orientation':
            break
    if orientation in exif and exif[orientation] >= 5:
        current_h, current_w = current_w, current_h

    scaled_w, scaled_h = get_scaled_down_size((current_w, current_h), target_size)
    target_w, target_h = target_size

    if target_w is not None and target_h is not None:
        result = target_w, target_h

    elif target_w is None and target_h is not None:
        result = scaled_w, target_h

    elif target_h is None and target_w is not None:
        result = target_w, scaled_h

    else:
        result = scaled_w, scaled_h

    sizes[input_size] = result
    cache.set(cache_key, sizes)

    return result


def calc_height(img_file, size=100):
    return get_new_size(img_file, size)[1]


def calc_width(img_file, size=100):
    return get_new_size(img_file, size)[0]
