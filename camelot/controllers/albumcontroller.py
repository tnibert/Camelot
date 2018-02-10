from ..models import Album
from django.utils import timezone
from django.contrib.auth.models import User

def get_profile_from_uid(id):
    return User.objects.get(id=id).profile

def create_album(name, description, ownerid):
    try:
        # owner needs to be a profile
        ownerprofile = User.objects.get(id=ownerid).profile  # I wonder if I can just pass in the user from the request directly...
        newalbum = Album(name=name, description=description, pub_date=timezone.now(), owner=ownerprofile)
        newalbum.save()
        return newalbum
    except:
        raise

def return_albums(ownerid):
    try:
        ownerprofile = get_profile_from_uid(ownerid)
        albums = Album.objects.filter(owner=ownerid)
        return albums
    except:
        raise
