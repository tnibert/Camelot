from .genericcontroller import genericcontroller
from .utilities import get_profile_from_uid, PermissionException
from .friendcontroller import are_friends

class profilecontroller(genericcontroller):

    def return_profile_data(self, uid):
        """

        :param uid: user id of profile to show
        :return: dict of name and description
        """
        profile = get_profile_from_uid(uid)

        friendstatus = None     # default if not logged in

        if self.uprofile:
            # check friendship
            if are_friends(self.uprofile, profile):
                friendstatus = "friends"
            # check pending
            elif are_friends(self.uprofile, profile, confirmed=False):
                friendstatus = "pending"
            # default not friends
            else:
                friendstatus = "not friends"

        # we will want to have a separate display name later
        return {"uid": profile.user.id, "friendstatus": friendstatus, "name": profile.user.username, "description": profile.description}
