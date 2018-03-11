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