from ..controllers.utilities import exif_rotate_image
from django.test import TestCase
from PIL import Image


class ImageManipulationTests(TestCase):

    def test_rotation(self):
        with Image.open("camelot/tests/resources/exifrotatedimg.jpg") as img:
            rotatedimg = exif_rotate_image(img)
        # todo: test:
        # no exif present
        # no rotation field in exif
        # exif rotations 1 - 8
