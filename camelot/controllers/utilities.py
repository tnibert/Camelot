from django.contrib.auth.models import User
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


class AlreadyExistsException(Exception):
    pass


class PermissionException(Exception):
    pass


class AddSelfException(Exception):
    pass