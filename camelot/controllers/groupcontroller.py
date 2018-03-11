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

    def add_member(self, groupid, profileid):
        """

        :param groupid: id of group to add to
        :param profileid: id of user profile to add to group
        :return: boolean, true for success
        """
        # check permission

    def delete_group(self):
        pass

    def delete_member(self):
        pass