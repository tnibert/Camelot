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

    def update_profile_data(self, **kwargs):
        """
        Update data in user profile
        :param kwargs: dict of data to be updated
        :return: reference to the current profile or None if user not logged in
        """
        # TODO: double check that the following will actually check if the user is not logged in, unit test
        if not self.uprofile:
            return None
        desc = kwargs.get('description', self.uprofile.description)
        self.uprofile.description = desc
        self.uprofile.save()
        return self.uprofile
