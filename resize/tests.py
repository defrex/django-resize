
import os
from PIL import Image
from shutil import rmtree, copytree

from django.core.files import File
from django.core.files.images import ImageFile
from django.core.management.color import no_style
from django.db import models, connection
from django.test import TestCase
from django.template.loader import render_to_string
from django.conf import settings
from django.core.files.storage import default_storage

from resize.utils import resize_image, get_thumb_name
from resize.fields import ResizedImageField


class ResizedFieldTest(models.Model):
    image = ResizedImageField(
        upload_to='resize/tests',
        resolutions=['100x100', 'autoxauto'],
    )

    @classmethod
    def create_table(cls):
        # Cribbed from Django's management commands.
        raw_sql, refs = connection.creation.sql_create_model(
            cls,
            no_style(),
            [])
        create_sql = u'\n'.join(raw_sql).encode('utf-8')
        cls.delete_table()
        cursor = connection.cursor()
        try:
            cursor.execute(create_sql)
        finally:
            cursor.close()

    @classmethod
    def delete_table(cls):
        cursor = connection.cursor()
        try:
            cursor.execute('DROP TABLE IF EXISTS %s' % cls._meta.db_table)
        except:
            # Catch anything backend-specific here.
            # (E.g., MySQLdb raises a warning if the table didn't exist.)
            pass
        finally:
            cursor.close()


class ResizeTest(TestCase):
    filename = 'test.jpg'  # 1000w x 1481h

    def setUp(self):
        ResizedFieldTest.create_table()

        self.test_image_directory = os.path.join(
            settings.MEDIA_ROOT,
            'resize_test_images',
        )
        copytree(
            os.path.join(os.path.dirname(__file__), 'test_images'),
            self.test_image_directory,
        )

        super(ResizeTest, self).setUp()

    def tearDown(self):
        ResizedFieldTest.delete_table()
        rmtree(self.test_image_directory)
        super(ResizeTest, self).tearDown()

    def get_image_path(self, filename=None):
        filename = filename or self.filename
        return '{}/{}'.format(self.test_image_directory, filename)

    def get_image(self, filename=None):
        return open(self.get_image_path(filename))

    def get_resize(self, size, filename=None):
        filename = filename or self.filename
        filename = '{}/{}'.format(self.test_image_directory, filename)
        return Image.open(get_thumb_name(filename, size))

    def test_resize(self):
        f = self.get_image()
        size = 100

        resize_image(f, size=size, storage=default_storage)

        img = self.get_resize(size)
        self.assertEqual(img.size[0], 100)
        self.assertEqual(img.size[1], 148)

    def test_resize_imagefile(self):
        f = ImageFile(self.get_image())
        size = 100

        resize_image(f, size=size, storage=default_storage)

        img = self.get_resize(size)
        self.assertEqual(img.size[0], 100)
        self.assertEqual(img.size[1], 148)

    def test_resize_larger(self):
        f = self.get_image()
        size = '2000x2000'

        resize_image(f, size=size, storage=default_storage)

        img = self.get_resize(size)
        self.assertEqual(img.size[0], 2000)
        self.assertEqual(img.size[1], 2000)

    def test_resize_hauto(self):
        f = self.get_image()
        size = '100xauto'

        resize_image(f, size=size, storage=default_storage)

        img = self.get_resize(size)
        self.assertEqual(img.size[0], 100)
        self.assertEqual(img.size[1], 148)

    def test_resize_wauto(self):
        f = self.get_image()
        size = 'autox100'

        resize_image(f, size=size, storage=default_storage)

        img = self.get_resize(size)
        self.assertEqual(img.size[0], 67)
        self.assertEqual(img.size[1], 100)

    def test_exif_rotation(self):
        f1 = self.get_image('exif1.jpg')
        resize_image(f1, size=100, storage=default_storage)
        img1 = self.get_resize(100, 'exif1.jpg')
        self.assertTrue(img1.size[0] < img1.size[1])

    def test_resize_letterbox(self):
        f = self.get_image()
        size = '100x100'

        resize_image(f, size=size, storage=default_storage)

        img = self.get_resize(size)
        self.assertEqual(img.size[0], 100)
        self.assertEqual(img.size[1], 100)

    def test_resize_crop(self):
        f = self.get_image()
        size = '100x100'

        resize_image(f, size=size, storage=default_storage)

        img = self.get_resize(size)
        self.assertEqual(img.size[0], 100)
        self.assertEqual(img.size[1], 100)

    def test_django_template(self):
        render_to_string('resize/test.html')

    def test_jinja_template(self):
        render_to_string('resize/test.jinja')

    def test_resized_field(self):
        instance = ResizedFieldTest()
        instance.image.save(self.get_image_path(), File(self.get_image()))
        instance.save()

        instance = ResizedFieldTest.objects.get(pk=instance.pk)
        instance.image.resized('100x100')

        try:
            instance.image.resized('100x101')
            assert False
        except ValueError:
            pass
