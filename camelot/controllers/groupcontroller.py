from ..models import FriendGroup
from .utilities import *

class groupcontroller:

    def __init__(self, uid):
        # redundant
        self.uprofile = get_profile_from_uid(uid)

    def create(self, name):
        """

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

    def add_member(self):
        pass

    def delete_group(self):
        pass

    def delete_member(self):
        pass