
import logging

from django.conf import settings
from django.template import Library
from django.contrib.sites.models import Site
from django.contrib.staticfiles.finders import find as find_file

from resize.utils import resize_image, get_new_size, calc_height, calc_width

logger = logging.getLogger(__name__)

register = Library()


@register.filter
def resize(img_file, size=100):
    try:
        return resize_image(img_file, size)
    except:
        logger.error('Resize failed', exc_info=True)
        return ''


@register.filter
def resize_static(img_path, size=100):
    try:
        abs_path = find_file(img_path)
        new_name = resize_image(abs_path, size)
        new_path = img_path.split('/')
        new_path[-1] = new_name
        new_path = '/'.join(new_path)
        url = '{0}{1}'.format(settings.STATIC_URL, new_path)
        return url
    except:
        logger.error('Resize failed', exc_info=True)
        return ''


@register.filter
def resize_absolute(img_file, size=100):
    try:
        path = resize_image(img_file, size=size)
        if path[:4] != 'http':
            path = '%s://%s%s' % (settings.SITE_PROTOCOL, Site.objects.get_current(), path)
        return path
    except:
        logger.error('Resize absolute failed', exc_info=True)
        return ''


@register.filter
def height(img_file, size=100):
    try:
        return calc_height(img_file, size)
    except:
        logger.error('Calc height failed', exc_info=True)
        return ''


@register.filter
def width(img_file, size=100):
    try:
        return calc_width(img_file, size)
    except:
        logger.error('Calc width failed', exc_info=True)
        return ''
