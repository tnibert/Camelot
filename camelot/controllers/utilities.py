from django.contrib.auth.models import User
from PIL import Image
from PIL.ExifTags import TAGS


def get_profile_from_uid(id):
    return User.objects.get(id=id).profile


def get_profid_from_username(username):
    return User.objects.get(username__iexact=username)


def get_exif(img):
    """
    Return a dictionary of exif tags for jpeg
    :param img: returned from PIL.Image.open()
    :return: dictionary of exif tags
    """
    ret = {}
    info = img._getexif()
    for tag, value in info.items():
        decoded = TAGS.get(tag, tag)
        ret[decoded] = value
    return ret

def get_rotation(photo):
    """
    Get the rotation of an image from exif tags
    :param photo: django ORM photo model
    :return: css tag name of the rotation
    """
    rotation = ""
    with Image.open(photo.filename) as img:
        if 'exif' in img.info:
            exif = get_exif(img)
            print(exif)
            # these are the class names in the css
            if exif['Orientation'] == 6:
                rotation = "rotate90"
            elif exif['Orientation'] == 8:
                rotation = "rotate270"
            elif exif['Orientation'] == 3:
                rotation = "rotate180"
    return rotation


class AlreadyExistsException(Exception):
    pass


class PermissionException(Exception):
    pass


class AddSelfException(Exception):
    pass