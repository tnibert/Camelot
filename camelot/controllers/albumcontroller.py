from ..models import Album, Photo
from .utilities import *
from .friendcontroller import are_friends
from .genericcontroller import genericcontroller
from .groupcontroller import is_in_group
from ..constants import *
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
                newalbum = Album(name=name, description=description, pub_date=timezone.now(), owner=self.uprofile,
                                 accesstype=ALBUM_ALLFRIENDS)
                newalbum.save()
                return newalbum
            raise AlreadyExistsException("Album needs unique name")    # may want to make this exception less general
        except:
            raise

    def return_albums(self, profile=None):
        """
        Need to verify permissions for albums to return
        :return:
        """
        if profile is None:
            profile = self.uprofile

        try:
            albums = Album.objects.filter(owner=profile)
            # returns a queryset..
            return albums
        except:
            raise
        
    def return_album(self, id):
        """
        Need to verify permissions for album
        :param id:
        :return:
        """
        # we could reference this by primary key, depending on what we can get easiest from the front end
        # by specifying owner we have a bit of a permission mechanism, but that won't work long term (can't access another user's album
        try:
            album = Album.objects.get(id=id)
            return album
        except:
            raise

    def add_photo_to_album(self, albumid, description, fi):
        """
        this could be done in something like celery
        :param albumid: id of the album to add to
        :param description: description of the photo
        :param fi: the image file
        :return: reference to the newly created photo object
        """

        album = self.return_album(albumid)

        # check that user has permission to add to album
        if not ((self.uprofile == album.owner) or (self.uprofile in album.contributors.all())):
            raise PermissionException("User is not album owner or contributor")

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


    def set_accesstype(self, album, type):
        """
        Set access type for an album, only owner can do this
        :param album: album to set
        :return: boolean of success or failure
        """
        if self.uprofile == album.owner and ALBUM_PUBLIC <= type <= ALBUM_PRIVATE:
            album.accesstype = type
            return True
        else:
            return False


    def has_permission_to_view(self, album):
        """
        Check if the current user has permission to view the specified album
        :param album: the album who's permissions to check
        :return: boolean
        Damn this is some overhead...
        """
        # if public, can view
        if album.accesstype == ALBUM_PUBLIC:
            return True

        # owner and contributors can view, checks for ALBUM_PRIVATE access type
        if self.uprofile == album.owner or self.uprofile in album.contributors.all():
            return True

        # this may need to be a bit more fleshed out
        # what if owner wants to show to all friends, but contributor only to a group?
        if album.accesstype == ALBUM_ALLFRIENDS:
            for i in collate_owner_and_contrib(album):
                if are_friends(self.uprofile, i):
                    return True

        elif album.accesstype == ALBUM_GROUPS:
            # check uprofile against all groups
            for group in album.groups.all():
                if is_in_group(group, self.uprofile):
                    return True

        # if we have not returned True, no access
        return False


    def add_contributor_to_album(self, album, contributor):
        """
        Add a contributor to album
        :param album: album to add contributor to
        :param contributor: Profile of user to add as contributor
        :return: False if not friends, True on success
        """
        # check if users are friends?
        if not are_friends(album.owner, contributor):
            return False
        album.contributors.add(contributor)
        return True

    def add_group_to_album(self, album, group):
        """
        Add a friendgroup access to an album
        Prevent adding group to album that is not own or contributor
        :param album:
        :param group:
        :return: boolean indicating success of failure
        """
        # if we don't own the group, no bueno
        if group.owner != self.uprofile:
            return False
        # if we aren't owner or contributor to the album, dame dame desu
        if album.owner != self.uprofile and self.uprofile not in album.contributors.all():
            return False

        album.groups.add(group)
        return True

def collate_owner_and_contrib(album):
    """
    Combine owner and contributors into list
    :param album: album to collate
    :return: list of owner and contributors
    """
    lst = list(album.contributors.all())
    lst.append(album.owner)
    return lst
