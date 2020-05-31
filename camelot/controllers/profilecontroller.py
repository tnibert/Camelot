from django.db.models import Q
from .genericcontroller import genericcontroller
from .utilities import get_profile_from_uid, PermissionException
from .friendcontroller import friendcontroller, are_friends
from .groupcontroller import groupcontroller
from .albumcontroller import albumcontroller, collate_owner_and_contrib
from ..models import Photo
from ..constants import *


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

        return {"uid": profile.user.id, "friendstatus": friendstatus,
                "name": profile.user.username if len(profile.dname) == 0 else profile.dname,
                "description": profile.description}

    def update_profile_data(self, **kwargs):
        """
        Update data in user profile
        :param kwargs: dict of data to be updated
        :return: reference to the current profile or None if user not logged in
        """
        # TODO: double check that the following will actually check if the user is not logged in, unit test
        if not self.uprofile:
            return None

        dname = kwargs.get('displayname', self.uprofile.dname)
        desc = kwargs.get('description', self.uprofile.description)

        self.uprofile.dname = dname
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
            raise e
        return True

    def set_profile_pic(self, photoid):
        """
        Set profile picture of current user
        Must check that photo is a valid profile picture
        A valid profile picture must belong to an owned or contributed album
        :param photo: photo to set as profile picturs
        :return: True if valid photo and success, else False
        """

        photo = Photo.objects.get(id=photoid)

        if self.uprofile in collate_owner_and_contrib(photo.album):
            self.uprofile.profile_pic = photo
            self.uprofile.save()
            return True
        else:
            return False

    def get_feed(self):
        """
        Returns all photos from friends that the user has permission to view
        :return: A list of photo model objects
        """
        # initialize our controllers
        friendcontrol = friendcontroller(self.uprofile.user.id)
        friendlist = friendcontrol.return_friend_list(self.uprofile)
        albumcontrol = albumcontroller(self.uprofile.user.id)

        # get all photos owned or uploaded by friends
        allfriendphotos = Photo.objects.filter(Q(uploader__in=friendlist) | Q(uploader=self.uprofile))\
            .order_by('-pub_date')

        # filter the photos based on if our user has permission to view them
        feedphotos = [photo for photo in allfriendphotos if albumcontrol.has_permission_to_view(photo.album)]

        return feedphotos
