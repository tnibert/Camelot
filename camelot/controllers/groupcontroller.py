from ..models import FriendGroup
from .utilities import *
from .genericcontroller import genericcontroller

class groupcontroller(genericcontroller):

    def create(self, name):
        """
        create a new friend group
        :param name: name of the group
        :return: reference to the newly created group
        """
        # redundant
        try:
            # check if the name already exists for the current user
            try:
                FriendGroup.objects.get(owner=self.uprofile, name=name)
            # if not, it's a go
            except FriendGroup.DoesNotExist:
                # may want to check length of name here
                newgroup = FriendGroup(name=name, owner=self.uprofile)
                newgroup.save()
                return newgroup
            raise AlreadyExistsException("Group needs unique name")
        except:
            raise

    def add_member(self, groupid, profile):
        """

        :param groupid: id of group to add to
        :param profile: user profile to add to group
        :return: boolean, true for success
        """
        # need to come back and assert that the users are in fact friends once friendship is implemented

        # check permission
        try:
            # get the group, but only if the owner is the current user
            group = FriendGroup.objects.get(owner=self.uprofile, id=groupid)
        except FriendGroup.DoesNotExist:
            # insert log message here, maybe raise permission exception
            return False

        # check if the profile already exists in the group
        if group.members.all().filter(id=profile.id).exists():
            # log
            return False

        group.members.add(profile)
        group.save()
        return True


    def delete_group(self):
        pass

    def delete_member(self):
        pass