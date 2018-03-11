from django.contrib.auth.models import User

def get_profile_from_uid(id):
    return User.objects.get(id=id).profile

class AlreadyExistsException(Exception):
    pass