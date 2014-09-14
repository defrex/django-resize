
from __future__ import print_function, unicode_literals
from optparse import make_option
import os

from django.core.management.base import BaseCommand

from resize.utils import resize_image


class Command(BaseCommand):
    args = '<image_path>'
    help = 'Resizes an image.'
    option_list = BaseCommand.option_list + (
        make_option('-r', '--resolution',
            dest='resolution',
            action='store',
            default='144x144',
            help='The resolution to resize to',
        ),
    )

    def handle(self, *args, **options):
        for image_path in args:
            with open(os.path.abspath(image_path)) as image_file:
                resize_image(image_file, options['resolution'])
