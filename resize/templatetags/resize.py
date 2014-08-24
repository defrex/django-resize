
from __future__ import absolute_import, print_function, unicode_literals

import logging

from django.core.files.storage import get_storage_class
from django.conf import settings
from django.template import Library
from django.templatetags.static import static

from resize.utils import resize_image

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
        return static(resize_image(
            img_path,
            size,
            storage=get_storage_class(settings.STATICFILES_STORAGE)
        ))
    except:
        logger.error('Resize failed', exc_info=True)
        return ''
