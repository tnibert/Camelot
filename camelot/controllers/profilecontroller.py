from .genericcontroller import genericcontroller
from .utilities import get_profile_from_uid, PermissionException
from .friendcontroller import are_friends
from .groupcontroller import groupcontroller

class profilecontroller(genericcontroller):

    def return_profile_data(self, uid):
        """

        :param uid: user id of profile to show
        :return: dict of name and description
        """
        profile = get_profile_from_uid(uid)

        friendstatus = None     # default if not logged in

        if self.uprofile:
            # check identity
            if self.uprofile == profile:
                # friendstatus is None
                pass
            # check friendship
            elif are_friends(self.uprofile, profile):
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

    def create_default_groups(self):
        """
        Create Public, All Friends, and Private groups
        :return: True on success
        """
        groupcontrol = groupcontroller(self.uprofile.user.id)
        try:
            # no need to check if groups already exist, groupcontroller creation will do that
            groupcontrol.create("Family")
            groupcontrol.create("Coworkers")
            groupcontrol.create("School Friends")
        except Exception as e:
            raise(e)
        return True

    def set_profile_pic(self, photo):
        """
        Set profile picture of current user
        Must check that photo is a valid profile picture
        A valid profile picture must belong to an owned or contributed album
        :param photo: photo to set as profile picturs
        :return:
        """
        pass