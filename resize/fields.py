
from __future__ import unicode_literals, print_function
from django.db.models.fields.files import ImageField, ImageFieldFile
from resize.utils import resize_image, get_thumb_name


class ResizedImageFieldFile(ImageFieldFile):

    def ensure_resolution(self, resolution):
        if not resolution in self.field.resolutions:
            raise ValueError('{} is not a valid resolution, options are: {}'.format(
                resolution,
                self.field.resolutions,
            ))

    def resized(self, resolution):
        self.ensure_resolution(resolution)
        return get_thumb_name(self, resolution)

    def resized_url(self, resolution):
        if resolution == 'autoxauto':
            return self.storage.url(self.name)
        else:
            self.ensure_resolution(resolution)
            thumb_name = get_thumb_name(self.name, resolution)
            return self.storage.url(thumb_name)

    def resized_urls(self):
        return {res: self.resized_url(res) for res in self.field.resolutions}


class ResizedImageField(ImageField):
    attr_class = ResizedImageFieldFile

    def __init__(self, resolutions=None, **kwargs):
        self.resolutions = resolutions or ()
        super(ResizedImageField, self).__init__(**kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super(ResizedImageField, self).deconstruct()
        kwargs['resolutions'] = self.resolutions
        return name, path, args, kwargs

    def pre_save(self, *args, **kwargs):
        file_object = super(ResizedImageField, self).pre_save(*args, **kwargs)

        if file_object:
            for resolution in self.resolutions:
                resize_image(file_object, resolution)

        return file_object

    def value_to_string(self, obj):
        return self.get_prep_value(self._get_val_from_obj(obj))
