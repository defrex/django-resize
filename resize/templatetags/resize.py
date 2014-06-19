
from __future__ import absolute_import, print_function, unicode_literals

import logging

from django.conf import settings
from django.template import Library
from django.contrib.sites.models import Site
from django.contrib.staticfiles.finders import find as find_file

from resize.utils import resize_image, calc_height, calc_width

try:
    from django_jinja import library
    lib = library.Library()

except ImportError:
    class LibraryStub(object):
        @staticmethod
        def global_function(func):
            return func
    lib = LibraryStub()

logger = logging.getLogger(__name__)

register = Library()


@register.filter
@lib.global_function
def resize(img_file, size=100):
    try:
        return resize_image(img_file, size)
    except:
        logger.error('Resize failed', exc_info=True)
        return ''


@register.filter
@lib.global_function
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
@lib.global_function
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
@lib.global_function
def height(img_file, size=100):
    try:
        return calc_height(img_file, size)
    except:
        logger.error('Calc height failed', exc_info=True)
        return ''


@register.filter
@lib.global_function
def width(img_file, size=100):
    try:
        return calc_width(img_file, size)
    except:
        logger.error('Calc width failed', exc_info=True)
        return ''
