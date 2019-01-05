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
    Note: orientation of 1 is right side up
    If we don't have the exiforientation set in the DB, open the file and check the exif tag,
    update the field.  This let's us avoid a migration.  Maybe it's lazy... meh, it's open source, if you don't like it fix it
    ^^^ that being said I'm still not sure if I'm going to keep it that way or migrate it
    :param photo: django ORM photo model
    :return: css tag name of the rotation
    """
    rotation = ""
    if photo is None:
        return rotation
    if photo.exiforientation is None:
        # if we haven't created our orientation in the db, create it
        try:
            with Image.open(photo.filename) as img:
                if 'exif' in img.info:
                    exif = get_exif(img)
                    #print(exif)
                    try:
                        assert isinstance(exif['Orientation'], int)
                        photo.exiforientation = exif['Orientation']
                    except KeyError:
                        photo.exiforientation = 1

                else:
                    photo.exiforientation = 1

        except FileNotFoundError as e:
            # todo: maybe delete the file from the db?
            photo.exiforientation = 1
        photo.save()

    #print("Checking orientation")
    # these are the class names in the css
    if photo.exiforientation == 6:
        rotation = "rotate90"
    elif photo.exiforientation == 8:
        rotation = "rotate270"
    elif photo.exiforientation == 3:
        rotation = "rotate180"
    #print("Got orientation")
    return rotation


class AlreadyExistsException(Exception):
    pass


class PermissionException(Exception):
    pass


class AddSelfException(Exception):
    pass


class DiskExceededException(Exception):
    pass
