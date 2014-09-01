[![Build Status](https://travis-ci.org/defrex/django-resize.svg)](https://travis-ci.org/defrex/django-resize)

## django-resize

Simple Django Image Resizing

Step 1, use the `ImageField` subclass `resize.fields.ResizedImageField` like so.

    from resize.fields import ResizedImageField

    class MoModel(models.Model):
        image = ResizedImageField(resolutions=('32x32', '100x100'))

The resolutions should be in the form`widthxheight`, where `auto`
is an acceptable value for either. For example `100xauto` `50x20` `autox2000`.

During normal operation, new resolutions of the image will be generated
whenever it's changed. However, if you raw-insert data, or add new resolutions
to the list, you can generate any missing images with a manage command.

    ./manage.py resize_fields

In your templates, a templatetag is provided to use the correct resolution like so.

    <img src="{{ my_model.image|resize:'32x32' }}">

or in Jinja (via [django-jinja](http://django-jinja.readthedocs.org/en/latest/))

    <img src=""{{ resize(my_model.image, '32x32') }}">
