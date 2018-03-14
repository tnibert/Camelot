from .genericcontroller import genericcontroller
from .utilities import get_profile_from_uid, PermissionException

class profilecontroller(genericcontroller):

    def return_profile_data(self, uid):
        """

        :param uid: user id of profile to show
        :return: dict of name and description
        """
        profile = get_profile_from_uid(uid)
        # we will want to have a separate display name later
        return {"name": profile.user.username, "description": profile.description}
