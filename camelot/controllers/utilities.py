from django.contrib.auth.models import User
from PIL.ExifTags import TAGS


def get_profile_from_uid(id):
    return User.objects.get(id=id).profile


def get_profid_from_username(username):
    return User.objects.get(username__iexact=username)


# todo: migrate existing front end rotated images
def exif_rotate_image(img):
    """
    Rotate an image according to its exif tag
    For reference: http://sylvana.net/jpegcrop/exif_orientation.html
    :param img: the image to check and rotate
    :return: the image rotated as per exif information
    """
    if 'exif' in img.info:
        # exif orientations are values 1 - 8
        # we are only handling the simple rotations
        # no reflections for now
        mapping = {
            3: 180,
            6: 270,
            8: 90
        }

        exif = get_exif(img)
        orientation = exif.get('Orientation')
        if orientation not in mapping.keys():
            return img

        return img.rotate(mapping[orientation], expand=True)

    else:
        return img


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
    This previously got the rotation of an image from exif tags or db.  Now it returns an empty string
    because we will not rotate the image on the front end anymore.

    Note: orientation of 1 is right side up
    If we don't have the exiforientation set in the DB, open the file and check the exif tag,
    update the field.  This let's us avoid a migration.

    todo: Remove this function, calls to it, and css rotations

    :param photo: django ORM photo model
    :return: css tag name of the rotation
    """
    return ""


class AlreadyExistsException(Exception):
    pass


class PermissionException(Exception):
    pass


class AddSelfException(Exception):
    pass


class DiskExceededException(Exception):
    pass
