from ..models import Album, Photo
from django.utils import timezone
from django.contrib.auth.models import User
from os import makedirs

# we'll probably want to move this function to a different file
def get_profile_from_uid(id):
    return User.objects.get(id=id).profile

class AlreadyExistsException(Exception):
    pass

class albumcontroller:
    """
    Class for accessing albums for a given user
    This will make life easier in the long run
    All of this will need user permission checks at some point - in view layer
    All of this will need exception catching in view layer as well

    Get a better handle on what objects are returned by the ORM and add docstrings to everything
    """

    def create_album(self, name, description):
        try:
            # check if the name already exists for the current user
            try:
                Album.objects.get(owner=self.uprofile, name=name)
            # if not, it's a go
            except Album.DoesNotExist:
                newalbum = Album(name=name, description=description, pub_date=timezone.now(), owner=self.uprofile)
                newalbum.save()
                return newalbum
            raise AlreadyExistsException("Album needs unique name")    # may want to make this exception less general
        except:
            raise

    def return_albums(self):
        try:
            albums = Album.objects.filter(owner=self.uprofile)
            # returns a queryset..
            return albums
        except:
            raise

    def __init__(self, uid):
        self.uprofile = get_profile_from_uid(uid)
        # potentially set a current album variable and just change it when user clicks album
        # rather than passing in every time, but maybe not
        
    def return_album(self, owner, name):
        # we could also reference this by primary key, depending on what we can get easiest from the front end
        try:
            album = Album.objects.get(owner=owner, name=name)
            return album
        except:
            raise

    def add_photo_to_album(self, album, description, fi):
        # this could be done in something like celery
        # we should probably change this so the image is stored in the database itself

        # add file to database
        newphoto = Photo(description=description, album=album)
        newphoto.save()

        # create filename with primary key
        fname = 'userphotos/{}/{}/{}'.format(self.uprofile.user.id, album.id, newphoto.id)

        # update filename in db now that we have our primary key
        newphoto.filename = fname

        # well now we definitely depend on python 3.2+
        makedirs("/".join(fname.split("/")[:-1]), exist_ok=True)

        # save file in chunks to save memory
        CHUNK_SIZE = 430        # bytes
        with open(fname, 'wb+') as destination:
            chunk = fi.read(CHUNK_SIZE)
            while chunk:  # loop until the chunk is empty (the file is exhausted)
                destination.write(chunk)
                chunk = fi.read(CHUNK_SIZE)  # read the next chunk

        return newphoto

    def get_photos_for_album(self, album):
        """
        :param album: album model object, can feed straight from return_album()
        :return: queryset of photos
        Need to add unit test
        """
        try:
            photos = Photo.objects.filter(album=album)
            return photos
        except:
            raise