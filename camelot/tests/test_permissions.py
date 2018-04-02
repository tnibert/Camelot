from django.test import TestCase
from django.test.client import RequestFactory
from django.contrib.auth.models import User, AnonymousUser

from ..controllers.albumcontroller import albumcontroller
from ..controllers.groupcontroller import groupcontroller
from ..controllers.utilities import PermissionException
from ..constants import *
from ..view import album
from django.shortcuts import reverse

"""
In this file we need to define what our access permissions need to be
and test correct access and access violations

Access types:
Public, All Friends, Groups, Private
public - everyone can view
all friends - all friends can view (DEFAULT)
groups - only group members can view
private - only owner and contributors can view

Album:
If album has no groups, default is all friends? - not current implementation
Contributor can always view album

To validate an album:
Check if accessing user is in album's groups
"""

#class test_controller_permissions(TestCase):
#    pass

class AlbumViewPermissionsTest(TestCase):
    """
    This test will go through all possible access cases
    - not logged in
        - can view public album
    - logged in not friend
        - can view public, album
    - logged in friend not in group
        - can view public, all friends album
    - logged in friend in group
        - can view public, all friends, groups album
    - logged in contributor
        - can view all access types
        - can view manage page
        - can add/remove own groups if access type is groups
        - can add photos to album
    - logged in owner
        - can view all access types
        - can view manage page
        - can edit album access type
        - can add/remove own groups
        - can add/remove contributors
        - can add photos to album
    """
    def setUp(self):
        self.credentials = {
            'username': 'testuser',
            'email': 'user@test.com',
            'password': 'secret'}
        self.u = User.objects.create_user(**self.credentials)
        self.u.save()

        self.credentials = {
            'username': 'testuser2',
            'email': 'user2@test.com',
            'password': 'secret'}
        self.u2 = User.objects.create_user(**self.credentials)
        self.u2.save()

        # send login data
        #response = self.client.post('', self.credentials, follow=True)

        self.factory = RequestFactory()

        # create album for self.u
        self.albumcontrol = albumcontroller(self.u.id)
        self.testalbum = self.albumcontrol.create_album("test name", "test description")

        # create a group for self.u
        self.groupcontrol = groupcontroller(self.u.id)
        self.testgroup = self.groupcontrol.create("test group")

        # add group to album
        self.albumcontrol.add_group_to_album(self.testalbum, self.testgroup)

        # add photo to album

    def test_not_logged_in(self):
        """
        Can view public album only
        Cannot view other access types
        cannot edit album or upload photos
        Cannot add non logged in user to group
        :param self:
        :return:
        """
        self.albumcontrol.set_accesstype(self.testalbum, ALBUM_PUBLIC)
        request = self.factory.get(reverse("show_album", kwargs={'id': self.testalbum.id}))
        request.user = AnonymousUser()

        response = album.display_album(request, self.testalbum.id)

        self.assertEqual(response.status_code, 200)

        self.albumcontrol.set_accesstype(self.testalbum, ALBUM_ALLFRIENDS)

        self.assertRaises(PermissionException, album.display_album, request, self.testalbum.id)

        self.albumcontrol.set_accesstype(self.testalbum, ALBUM_GROUPS)

        # we don't match at this line
        self.assertRaises(PermissionException, album.display_album, request, self.testalbum.id)

        self.albumcontrol.set_accesstype(self.testalbum, ALBUM_PRIVATE)

        self.assertRaises(PermissionException, album.display_album, request, self.testalbum.id)

        # show_photo

    def test_logged_in_not_friend(self):
        pass

    def test_logged_in_friend_not_in_group(self):
        pass

    def test_logged_in_friend_in_group(self):
        pass

    def test_logged_in_contributor(self):
        pass

    def test_logged_in_owner(self):
        pass