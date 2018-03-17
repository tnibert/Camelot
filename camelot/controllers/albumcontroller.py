from ..models import Album, Photo
from .utilities import *
from .genericcontroller import genericcontroller
from django.utils import timezone
from os import makedirs

class albumcontroller(genericcontroller):
    """
    Class for accessing albums for a given user
    This will make life easier in the long run
    All of this will need user permission checks at some point - in view layer... actually maybe in this layer
    All of this will need exception catching (in view layer? probably not I'm now thinking) as well

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
        """
        This will need to be changed, we can't always return the current user's albums
        :return:
        """
        try:
            albums = Album.objects.filter(owner=self.uprofile)
            # returns a queryset..
            return albums
        except:
            raise
        
    def return_album(self, id):
        """
        This will need to be changed in the same way as the previous method
        :param id:
        :return:
        """
        # we could reference this by primary key, depending on what we can get easiest from the front end
        # by specifying owner we have a bit of a permission mechanism, but that won't work long term (can't access another user's album
        try:
            album = Album.objects.get(owner=self.uprofile, id=id)
            return album
        except:
            raise

    def add_photo_to_album(self, albumid, description, fi):
        """

        :param albumid: id of the album to add to
        :param description: description of the photo
        :param fi: the image file
        :return: reference to the newly created photo object
        """
        # this could be done in something like celery
        album = self.return_album(albumid)

        # add file to database
        newphoto = Photo(description=description, album=album)
        newphoto.save()

        # create filename with primary key
        fname = 'userphotos/{}/{}/{}'.format(self.uprofile.user.id, album.id, newphoto.id)

        # update filename in db now that we have our primary key
        newphoto.filename = fname

        newphoto.save()

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

    def return_photo(self, photoid):
        """
        make unit test
        :param photoid: the id of the photo in the photos table
        :return: a single photo
        """
        try:
            photo = Photo.objects.get(id=photoid)
            return photo
        except:
            raise

    def delete_album(self):
        pass

    def has_permission_to_view(self, album):
        """
        Check if the current user has permission to view the specified album
        :param album: the album who's permissions to check
        :return: boolean
        """
        pass