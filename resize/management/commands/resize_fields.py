
from __future__ import print_function, unicode_literals

from django.core.management.base import BaseCommand
from django.apps import apps
from optparse import make_option

from resize.fields import ResizedImageField
from resize.utils import resize_image


class Command(BaseCommand):
    help = 'Ensures that all ResizedImageFields are available in all required resolutions.'
    option_list = BaseCommand.option_list + (
        make_option('--fail-loud',
            action='store_true',
            dest='fails',
            default=False,
            help='Fail on IOErrors',
        ),
    )

    def handle(self, *args, **options):
        print('Looking for resized fields')

        for Model in apps.get_models():
            print('  {}.{}'.format(Model._meta.app_label, Model._meta.model_name))

            resized_fields = []
            for field in Model._meta.fields:
                if isinstance(field, ResizedImageField):
                    resized_fields.append(field)

            for field in resized_fields:
                print('    ', field.name)
                images = (
                    Model
                    .objects
                    .filter(**{'{}__isnull'.format(field.name): False})
                    .exclude(**{field.name: ''})
                    .values_list(field.name, flat=True)
                )
                for resolution in field.resolutions:
                    print('      resizing {} images to {}'.format(
                        len(images),
                        resolution,
                    ))
                    for image in images:
                        try:
                            resize_image(field.storage.open(image), resolution)
                        except IOError:
                            print('        Image does not exist', image)
                            if options['fails']:
                                raise

        print('Resizing complete')
