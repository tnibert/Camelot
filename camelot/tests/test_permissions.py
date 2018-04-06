from django.test import TestCase
from django.test.client import RequestFactory
from django.contrib.auth.models import User, AnonymousUser
from django.shortcuts import reverse

import os
import shutil

from ..controllers.albumcontroller import albumcontroller
from ..controllers.groupcontroller import groupcontroller
from ..controllers.utilities import PermissionException
from ..constants import *
from ..view import album
from .helperfunctions import complete_add_friends

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

    Implemented:
    - check all view album calls
    Need to:
    - check access rights for edit and manage endpoints
    - check access rights for viewing and uploading photos

    This testcase might need to be split up in the future
    """
    def setUp(self):
        self.credentials = {
            'username': 'testuser',
            'email': 'user@test.com',
            'password': 'secret'}
        self.u = User.objects.create_user(**self.credentials)
        self.u.save()

        self.credentials2 = {
            'username': 'testuser2',
            'email': 'user2@test.com',
            'password': 'secret'}
        self.u2 = User.objects.create_user(**self.credentials2)
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

        self.testdir = "testdir"

        # add photo to album
        if not os.path.exists(self.testdir):
            os.makedirs(self.testdir)
        os.chdir(self.testdir)

        with open('../camelot/tests/resources/testimage.jpg', 'rb') as fi:
            self.photo = self.albumcontrol.add_photo_to_album(self.testalbum.id, "our test album", fi)

        # define requests to test
        self.showalbumrequest = self.factory.get(reverse("show_album", kwargs={'id': self.testalbum.id}))
        self.photorequest = self.factory.get(reverse("show_photo", kwargs={'photoid': self.photo.id}))
        self.uploadphotorequest = self.factory.get(reverse("upload_photos", kwargs={'id': self.testalbum.id}))
        # todo: add post upload photo request

    def tearDown(self):
        os.chdir("..")
        shutil.rmtree(self.testdir)

    def test_not_logged_in(self):
        """
        Can view public album only
        test can view public photo
        - Photo view inherits permission from album
        Cannot view other access types
        cannot edit album or upload photos
        Cannot add non logged in user to group
        :param self:
        :return:
        """

        # assign anonymous user to requests
        self.showalbumrequest.user = AnonymousUser()
        self.photorequest.user = AnonymousUser()
        self.uploadphotorequest.user = AnonymousUser()

        self.albumcontrol.set_accesstype(self.testalbum, ALBUM_PUBLIC)

        response = album.display_album(self.showalbumrequest, self.testalbum.id)
        self.assertEqual(response.status_code, 200)

        # test photo access, public album will be accessible
        response = album.return_photo_file_http(self.photorequest, self.photo.id)
        self.assertEqual(response.status_code, 200)

        self.albumcontrol.set_accesstype(self.testalbum, ALBUM_ALLFRIENDS)

        self.assertRaises(PermissionException, album.display_album, self.showalbumrequest, self.testalbum.id)
        self.assertRaises(PermissionException, album.return_photo_file_http, self.photorequest, self.photo.id)

        self.albumcontrol.set_accesstype(self.testalbum, ALBUM_GROUPS)

        self.assertRaises(PermissionException, album.display_album, self.showalbumrequest, self.testalbum.id)
        self.assertRaises(PermissionException, album.return_photo_file_http, self.photorequest, self.photo.id)

        self.albumcontrol.set_accesstype(self.testalbum, ALBUM_PRIVATE)

        self.assertRaises(PermissionException, album.display_album, self.showalbumrequest, self.testalbum.id)
        self.assertRaises(PermissionException, album.return_photo_file_http, self.photorequest, self.photo.id)

        # can't view manage page
        # can't edit album access type
        # can't edit contributors to album
        # can't add photos to album

        response = album.add_photo(self.uploadphotorequest, self.testalbum.id)
        # since we are not logged in, redirects to login page
        assert response.status_code == 302
        # may be good to add a post test for upload_photos, even though we have login_required decorator
        # just to have complete coverage

    def test_logged_in_not_friend(self):
        """
        Logged in not friend has same permissions as non logged in user
        """

        response = self.client.post('', self.credentials2, follow=True)

        self.albumcontrol.set_accesstype(self.testalbum, ALBUM_PUBLIC)

        self.showalbumrequest.user = self.u2
        self.photorequest.user = self.u2
        self.uploadphotorequest.user = self.u2

        response = album.display_album(self.showalbumrequest, self.testalbum.id)
        self.assertEqual(response.status_code, 200)

        response = album.return_photo_file_http(self.photorequest, self.photo.id)
        self.assertEqual(response.status_code, 200)

        self.albumcontrol.set_accesstype(self.testalbum, ALBUM_ALLFRIENDS)

        self.assertRaises(PermissionException, album.display_album, self.showalbumrequest, self.testalbum.id)
        self.assertRaises(PermissionException, album.return_photo_file_http, self.photorequest, self.photo.id)

        self.albumcontrol.set_accesstype(self.testalbum, ALBUM_GROUPS)

        self.assertRaises(PermissionException, album.display_album, self.showalbumrequest, self.testalbum.id)
        self.assertRaises(PermissionException, album.return_photo_file_http, self.photorequest, self.photo.id)

        self.albumcontrol.set_accesstype(self.testalbum, ALBUM_PRIVATE)

        self.assertRaises(PermissionException, album.display_album, self.showalbumrequest, self.testalbum.id)
        self.assertRaises(PermissionException, album.return_photo_file_http, self.photorequest, self.photo.id)

        # test get upload photo page
        self.assertRaises(PermissionException, album.add_photo, self.uploadphotorequest, self.testalbum.id)

    def test_logged_in_friend_not_in_group(self):

        complete_add_friends(self.u.id, self.u2.id)

        response = self.client.post('', self.credentials2, follow=True)

        self.albumcontrol.set_accesstype(self.testalbum, ALBUM_PUBLIC)
        request = self.factory.get(reverse("show_album", kwargs={'id': self.testalbum.id}))
        request.user = self.u2

        response = album.display_album(request, self.testalbum.id)

        self.assertEqual(response.status_code, 200)

        self.albumcontrol.set_accesstype(self.testalbum, ALBUM_ALLFRIENDS)

        response = album.display_album(request, self.testalbum.id)

        self.assertEqual(response.status_code, 200)

        self.albumcontrol.set_accesstype(self.testalbum, ALBUM_GROUPS)

        self.assertRaises(PermissionException, album.display_album, request, self.testalbum.id)

        self.albumcontrol.set_accesstype(self.testalbum, ALBUM_PRIVATE)

        self.assertRaises(PermissionException, album.display_album, request, self.testalbum.id)

    def test_logged_in_friend_in_group(self):
        complete_add_friends(self.u.id, self.u2.id)
        self.groupcontrol.add_member(self.testgroup.id, self.u2.profile)

        response = self.client.post('', self.credentials2, follow=True)

        self.albumcontrol.set_accesstype(self.testalbum, ALBUM_PUBLIC)
        request = self.factory.get(reverse("show_album", kwargs={'id': self.testalbum.id}))
        request.user = self.u2

        response = album.display_album(request, self.testalbum.id)

        self.assertEqual(response.status_code, 200)

        self.albumcontrol.set_accesstype(self.testalbum, ALBUM_ALLFRIENDS)

        response = album.display_album(request, self.testalbum.id)

        self.assertEqual(response.status_code, 200)

        self.albumcontrol.set_accesstype(self.testalbum, ALBUM_GROUPS)

        response = album.display_album(request, self.testalbum.id)

        self.assertEqual(response.status_code, 200)

        self.albumcontrol.set_accesstype(self.testalbum, ALBUM_PRIVATE)

        self.assertRaises(PermissionException, album.display_album, request, self.testalbum.id)

    def test_logged_in_contributor(self):
        # add as contributor before adding friend
        assert not self.albumcontrol.add_contributor_to_album(self.testalbum, self.u2.profile)

        complete_add_friends(self.u.id, self.u2.id)

        assert self.albumcontrol.add_contributor_to_album(self.testalbum, self.u2.profile)

        response = self.client.post('', self.credentials2, follow=True)

        self.albumcontrol.set_accesstype(self.testalbum, ALBUM_PUBLIC)
        request = self.factory.get(reverse("show_album", kwargs={'id': self.testalbum.id}))
        request.user = self.u2

        response = album.display_album(request, self.testalbum.id)

        self.assertEqual(response.status_code, 200)

        self.albumcontrol.set_accesstype(self.testalbum, ALBUM_ALLFRIENDS)

        response = album.display_album(request, self.testalbum.id)

        self.assertEqual(response.status_code, 200)

        self.albumcontrol.set_accesstype(self.testalbum, ALBUM_GROUPS)

        response = album.display_album(request, self.testalbum.id)

        self.assertEqual(response.status_code, 200)

        self.albumcontrol.set_accesstype(self.testalbum, ALBUM_PRIVATE)

        response = album.display_album(request, self.testalbum.id)

        self.assertEqual(response.status_code, 200)

    def test_logged_in_owner(self):
        """
        Login as album creator (owner) and access all access types
        """
        response = self.client.post('', self.credentials, follow=True)

        self.albumcontrol.set_accesstype(self.testalbum, ALBUM_PUBLIC)
        request = self.factory.get(reverse("show_album", kwargs={'id': self.testalbum.id}))
        request.user = self.u

        response = album.display_album(request, self.testalbum.id)

        self.assertEqual(response.status_code, 200)

        self.albumcontrol.set_accesstype(self.testalbum, ALBUM_ALLFRIENDS)

        response = album.display_album(request, self.testalbum.id)

        self.assertEqual(response.status_code, 200)

        self.albumcontrol.set_accesstype(self.testalbum, ALBUM_GROUPS)

        response = album.display_album(request, self.testalbum.id)

        self.assertEqual(response.status_code, 200)

        self.albumcontrol.set_accesstype(self.testalbum, ALBUM_PRIVATE)

        response = album.display_album(request, self.testalbum.id)

        self.assertEqual(response.status_code, 200)