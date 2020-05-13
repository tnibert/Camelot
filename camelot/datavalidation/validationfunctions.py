from django.core.exceptions import ValidationError
from django.template.defaultfilters import filesizeformat
from PIL import Image
from html import escape
from ..constants import MAX_UPLOAD_SIZE

"""
This file contains functions to validate data input to the API

Links:
http://code.activestate.com/recipes/496942/
https://www.owasp.org/index.php/XSS_(Cross_Site_Scripting)_Prevention_Cheat_Sheet
"""


def validate_image_fsize(value):
    """
    Validation function for UploadPhotoForm -> slowly deprecating
    Checks maximum size of file
    :param value:
    :return:
    """
    if value._size > MAX_UPLOAD_SIZE:
        raise ValidationError("Please keep file size under {}. Current file size {}".format(filesizeformat(str(MAX_UPLOAD_SIZE)), filesizeformat(value._size)))


def validate_image(data):
    # todo: add appropriate unit tests
    """
    Validate image
    Check for size
    Check for valid image file
    :param data: bytesio object representing raw image
    :return:
    """
    fsize = data.getbuffer().nbytes
    # note: nbytes is the number of bytes we are taking up

    if fsize > MAX_UPLOAD_SIZE:
        raise ValidationError(
            "Please keep file size under {}. Current file size {}".format(filesizeformat(str(MAX_UPLOAD_SIZE)),
                                                                          filesizeformat(fsize)))
    img = Image.open(data)
    try:
        img.verify()
    except Exception as e:
        print(e)
        raise ValidationError("Invalid image file")


def validate_photo_description(data):
    assert isinstance(data, str)
    validstr = escape(data)
    return validstr
