
import os
from PIL import Image
from shutil import rmtree

from django.test import TestCase
from django.core.files.images import ImageFile

from resize.utils import calc_height, calc_width, resize_image


class ResizeTest(TestCase):
    filename = 'test.jpg'  # 1000w x 1481h

    def get_image(self, filename=None):
        filename = filename or self.filename
        filename = 'test_images/%s' % filename
        return open(os.path.join(os.path.dirname(__file__), filename))

    def get_resize(self, size, filename=None):
        filename = filename or self.filename
        filename = 'test_images/%s' % filename
        return Image.open(os.path.join(
            os.path.dirname(__file__),
            '%s_thumbs/v1_at_%s.jpg' % (filename, str(size))
        ))

    def tearDown(self):
        path = os.path.join(os.path.dirname(__file__), 'test_images')
        for item in os.listdir(path):
            item = os.path.join(path, item)
            if os.path.isdir(item):
                rmtree(item)

    def test_resize(self):
        f = self.get_image()
        size = 100

        resize_image(f, size=size)

        img = self.get_resize(size)
        self.assertEqual(img.size[0], 100)
        self.assertEqual(img.size[1], 148)

    def test_resize_imagefile(self):
        f = ImageFile(self.get_image())
        size = 100

        resize_image(f, size=size)

        img = self.get_resize(size)
        self.assertEqual(img.size[0], 100)
        self.assertEqual(img.size[1], 148)

    def test_resize_larger(self):
        f = self.get_image()
        size = '2000x2000'

        resize_image(f, size=size)

        img = self.get_resize(size)
        self.assertEqual(img.size[0], 2000)
        self.assertEqual(img.size[1], 2000)

    def test_resize_hauto(self):
        f = self.get_image()
        size = '100xauto'

        resize_image(f, size=size)

        img = self.get_resize(size)
        self.assertEqual(img.size[0], 100)
        self.assertEqual(img.size[1], 148)

    def test_resize_wauto(self):
        f = self.get_image()
        size = 'autox100'

        resize_image(f, size=size)

        img = self.get_resize(size)
        self.assertEqual(img.size[0], 67)
        self.assertEqual(img.size[1], 100)

    def test_calc_height(self):
        f = self.get_image()
        size = '100xauto'

        height = calc_height(f, size)

        self.assertEqual(height, 148)

    def test_calc_width(self):
        f = self.get_image()
        size = 'autox100'

        width = calc_width(f, size)

        self.assertEqual(width, 67)

    def test_exif_rotation(self):
        f1 = self.get_image('exif1.jpg')
        resize_image(f1, size=100)
        img1 = self.get_resize(100, 'exif1.jpg')
        self.assertTrue(img1.size[0] < img1.size[1])

    def test_resize_letterbox(self):
        f = self.get_image()
        size = '100x100'

        resize_image(f, size=size)

        img = self.get_resize(size)
        self.assertEqual(img.size[0], 100)
        self.assertEqual(img.size[1], 100)

    def test_resize_crop(self):
        f = self.get_image()
        size = '100x100'

        resize_image(f, size=size)

        img = self.get_resize(size)
        self.assertEqual(img.size[0], 100)
        self.assertEqual(img.size[1], 100)
