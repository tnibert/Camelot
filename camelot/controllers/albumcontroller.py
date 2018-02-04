from ..models import Album
from django.utils import timezone
from django.contrib.auth.models import User

def create_album(name, description, ownerid):
    try:
        # owner needs to be a profile
        ownerprofile = User.objects.get(id=ownerid).profile  # I wonder if I can just pass in the user from the request directly...
        newalbum = Album(name=name, description=description, pub_date=timezone.now(), owner=ownerprofile)
        newalbum.save()
        return newalbum
    except:
        raise
