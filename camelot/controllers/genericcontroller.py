from .utilities import *

class genericcontroller:

    def __init__(self, uid):
        # get the current user profile
        # we might want to just pass in the request session for this, but maybe not
        self.uprofile = get_profile_from_uid(uid)

    # may not belong here, but let's just drop it here for a sec
    def validate_permission(self):
        """
        check if the user has permission to access the material
        :return: boolean specifying if permission is granted
        """
        return True

    # maybe we do this... it's basically the same process in all of the controllers
    # we should wrap it though
    #def _create(self, themodel, **kwargs):
    #    try:
    #        # check if the name already exists for the current user
    #        try:
    #            themodel.objects.get(owner=self.uprofile, **kwargs)
    #        # if not, it's a go
    #        except themodel.DoesNotExist:
    #            # may want to check length of name here
    #            newitem = themodel(**kwargs)
    #            newitem.save()
    #            return newitem
    #        raise AlreadyExistsException("Needs unique name")
    #    except:
    #        raise