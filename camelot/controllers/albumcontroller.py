from ..models import Album
from django.utils import timezone
from django.contrib.auth.models import User

# we'll probably want to move this function to a different file, probably usermgmt
def get_profile_from_uid(id):
    return User.objects.get(id=id).profile

class albumcontroller:
    """
    Class for accessing albums for a given user
    This will make life easier in the long run
    """

    def create_album(self, name, description):
        try:
            newalbum = Album(name=name, description=description, pub_date=timezone.now(), owner=self.uprofile)
            newalbum.save()
            return newalbum
        except:
            raise

    def return_albums(self):
        try:
            albums = Album.objects.filter(owner=self.uprofile)
            return albums
        except:
            raise

    def __init__(self, uid):
        self.uprofile = get_profile_from_uid(uid)
        
