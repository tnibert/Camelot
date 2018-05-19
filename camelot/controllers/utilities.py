from django.contrib.auth.models import User

def get_profile_from_uid(id):
    return User.objects.get(id=id).profile

def get_profid_from_username(username):
    return User.objects.get(username__iexact=username)

class AlreadyExistsException(Exception):
    pass

class PermissionException(Exception):
    pass

class AddSelfException(Exception):
    pass