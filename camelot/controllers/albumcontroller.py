from ..models import Album
from django.utils import timezone
from django.contrib.auth.models import User

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
        
    def return_album(self, owner, name):
        # currently we can probably have two albums of the same name for a given owner
        # we could also reference this by primary key, depending on what we can get easiest from the front end
        try:
            album = Album.objects.get(owner=owner, name=name)
            return album
        except:
            raise

    def add_photo_to_album(self):
        pass

    def get_photos_for_album(self, album):
        """
        :param album: album model object, can feed straight from return_album()
        :return: queryset of photos
        Probably best to implement this after we have an add photo view
        """
        try:
            pass
        except:
            raise