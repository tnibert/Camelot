from django.test import TestCase
from django.test.client import RequestFactory
from django.contrib.auth.models import User, AnonymousUser
from django.shortcuts import reverse
from django.http import Http404

import os
import shutil

from ..controllers.albumcontroller import albumcontroller, collate_owner_and_contrib
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

Todo:
    - check access rights for edit and manage endpoints
    - check access rights for viewing and uploading photos

Requirements:
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

#class test_controller_permissions(TestCase):
#    pass

class PermissionTestCase(TestCase):
    """
    Scaffolding for permissions tests
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
        # response = self.client.post('', self.credentials, follow=True)

        self.factory = RequestFactory()

        # create album for self.u
        self.albumcontrol = albumcontroller(self.u.id)
        self.testalbum = self.albumcontrol.create_album("test name", "test description")

        # create a group for self.u
        self.groupcontrol = groupcontroller(self.u.id)
        self.testgroup = self.groupcontrol.create("test group")

        # add group to album
        self.albumcontrol.add_group_to_album(self.testalbum, self.testgroup)

    def make_logged_in_not_friend(self):
        # log in
        response = self.client.post('', self.credentials2, follow=True)

    def make_logged_in_friend_not_in_group(self):

        complete_add_friends(self.u.id, self.u2.id)

        response = self.client.post('', self.credentials2, follow=True)

    def make_logged_in_friend_in_group(self):

        complete_add_friends(self.u.id, self.u2.id)
        self.groupcontrol.add_member(self.testgroup.id, self.u2.profile)

        response = self.client.post('', self.credentials2, follow=True)

    def make_logged_in_contributor(self):

        # add as contributor before adding friend
        # this unit test should be elsewhere
        assert not self.albumcontrol.add_contributor_to_album(self.testalbum, self.u2.profile)

        complete_add_friends(self.u.id, self.u2.id)

        assert self.albumcontrol.add_contributor_to_album(self.testalbum, self.u2.profile)

        response = self.client.post('', self.credentials2, follow=True)

    def make_logged_in_owner(self):
        """
        Login as album creator (owner) and access all access types
        """
        response = self.client.post('', self.credentials, follow=True)

    def perm_escalate_helper(self, albumcontrol, request, testalbum, id, user, func, level):
        """
        Incrementally tighten permissions for album
        :param albumcontrol: albumcontroller object
        :param request: request to test against
        :param testalbum: album to raise permissions of
        :param id: function arg to test against
        :param user: user to test against
        :param func: function matching request
        :param level: level of access user should have
                1: public
                2: all friends
                3: groups
                4: private
                -- defined in constants --
        """
        # assign anonymous user to requests
        request.user = user

        albumcontrol.set_accesstype(testalbum, ALBUM_PUBLIC)

        if level >= ALBUM_PUBLIC:
            response = func(request, id)
            self.assertEqual(response.status_code, 200)
        else:
            self.assertRaises(PermissionException, func, request, id)

        albumcontrol.set_accesstype(testalbum, ALBUM_ALLFRIENDS)

        if level >= ALBUM_ALLFRIENDS:
            response = func(request, id)
            self.assertEqual(response.status_code, 200)
        else:
            self.assertRaises(PermissionException, func, request, id)

        albumcontrol.set_accesstype(testalbum, ALBUM_GROUPS)

        if level >= ALBUM_GROUPS:
            response = func(request, id)
            self.assertEqual(response.status_code, 200)
        else:
            self.assertRaises(PermissionException, func, request, id)

        albumcontrol.set_accesstype(testalbum, ALBUM_PRIVATE)

        if level >= ALBUM_PRIVATE:
            response = func(request, id)
            self.assertEqual(response.status_code, 200)
        else:
            self.assertRaises(PermissionException, func, request, id)


class AlbumPhotoViewPermissionsTest(PermissionTestCase):
    """
    Test album view and photo view permissions
    Covers show_album, show_photo, and present_photo
    """
    def setUp(self):

        super(AlbumPhotoViewPermissionsTest, self).setUp()

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
        self.indivphotorequest = self.factory.get(reverse("present_photo", kwargs={'photoid': self.photo.id}))


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
        """

        # test show album
        self.perm_escalate_helper(self.albumcontrol, self.showalbumrequest, self.testalbum, self.testalbum.id,
                                  AnonymousUser(), album.display_album, ALBUM_PUBLIC)

        # test photo view
        self.perm_escalate_helper(self.albumcontrol, self.photorequest, self.testalbum, self.photo.id,
                                  AnonymousUser(), album.return_photo_file_http, ALBUM_PUBLIC)

        # test individual photo view page
        self.perm_escalate_helper(self.albumcontrol, self.indivphotorequest, self.testalbum, self.photo.id,
                                  AnonymousUser(), album.display_photo, ALBUM_PUBLIC)

    def test_logged_in_not_friend(self):
        """
        Logged in not friend has same permissions as non logged in user
        """

        # log in
        self.make_logged_in_not_friend()

        # test show album
        self.perm_escalate_helper(self.albumcontrol, self.showalbumrequest, self.testalbum, self.testalbum.id,
                                  self.u2, album.display_album, ALBUM_PUBLIC)

        # test photo view
        self.perm_escalate_helper(self.albumcontrol, self.photorequest, self.testalbum, self.photo.id,
                                  self.u2, album.return_photo_file_http, ALBUM_PUBLIC)

        # test individual photo view page
        self.perm_escalate_helper(self.albumcontrol, self.indivphotorequest, self.testalbum, self.photo.id,
                                  self.u2, album.display_photo, ALBUM_PUBLIC)

    def test_logged_in_friend_not_in_group(self):
        """
        Logged in friend not in group should be able to access ALL_FRIENDS permission
        """

        self.make_logged_in_friend_not_in_group()

        # test show album
        self.perm_escalate_helper(self.albumcontrol, self.showalbumrequest, self.testalbum, self.testalbum.id,
                                  self.u2, album.display_album, ALBUM_ALLFRIENDS)

        # test photo view
        self.perm_escalate_helper(self.albumcontrol, self.photorequest, self.testalbum, self.photo.id,
                                  self.u2, album.return_photo_file_http, ALBUM_ALLFRIENDS)

        # test individual photo view page
        self.perm_escalate_helper(self.albumcontrol, self.indivphotorequest, self.testalbum, self.photo.id,
                                  self.u2, album.display_photo, ALBUM_ALLFRIENDS)

    def test_logged_in_friend_in_group(self):
        """
        Logged in friend in group should be able to access GROUPS permission
        """
        self.make_logged_in_friend_in_group()

        # test show album
        self.perm_escalate_helper(self.albumcontrol, self.showalbumrequest, self.testalbum, self.testalbum.id,
                                  self.u2, album.display_album, ALBUM_GROUPS)

        # test photo view
        self.perm_escalate_helper(self.albumcontrol, self.photorequest, self.testalbum, self.photo.id,
                                  self.u2, album.return_photo_file_http, ALBUM_GROUPS)

        # test individual photo view page
        self.perm_escalate_helper(self.albumcontrol, self.indivphotorequest, self.testalbum, self.photo.id,
                                  self.u2, album.display_photo, ALBUM_GROUPS)

    def test_logged_in_contributor(self):
        """
        Contributor can access PRIVATE permission
        """
        self.make_logged_in_contributor()

        # test show album
        self.perm_escalate_helper(self.albumcontrol, self.showalbumrequest, self.testalbum, self.testalbum.id,
                                  self.u2, album.display_album, ALBUM_PRIVATE)

        # test photo view
        self.perm_escalate_helper(self.albumcontrol, self.photorequest, self.testalbum, self.photo.id,
                                  self.u2, album.return_photo_file_http, ALBUM_PRIVATE)

        # test individual photo view page
        self.perm_escalate_helper(self.albumcontrol, self.indivphotorequest, self.testalbum, self.photo.id,
                                  self.u2, album.display_photo, ALBUM_PRIVATE)

    def test_logged_in_owner(self):
        """
        Login as album creator (owner) and access all access types
        """
        self.make_logged_in_owner()

        # test show album
        self.perm_escalate_helper(self.albumcontrol, self.showalbumrequest, self.testalbum, self.testalbum.id,
                                  self.u, album.display_album, ALBUM_PRIVATE)

        # test photo view
        self.perm_escalate_helper(self.albumcontrol, self.photorequest, self.testalbum, self.photo.id,
                                  self.u, album.return_photo_file_http, ALBUM_PRIVATE)

        # test individual photo view page
        self.perm_escalate_helper(self.albumcontrol, self.indivphotorequest, self.testalbum, self.photo.id,
                                  self.u, album.display_photo, ALBUM_PRIVATE)


class test_manage_page_permissions(PermissionTestCase):
    def user_escalate_post_test_helper(self, request, user, alb, id, func, level):
        """
        This will be used with manage page post endpoints
        Maybe pass another function in for additional testing
        :param request:
        :param user:
        :param alb:
        :param id:
        :param func:
        :param level: access level that page should be, private means contributors can access,
                above that means only owner, below ALBUM_PUBLIC means no access to anyone
        """
        # user is not logged in
        # all post endpoints should have login_required decorator
        request.user = AnonymousUser()

        if ALBUM_PRIVATE >= level >= ALBUM_PUBLIC:
            response = func(request, id)
            self.assertEqual(response.status_code, 302)
        else:
            # this is caught by the login_required decorator
            response = func(request, id)
            # confirm redirect to login page
            self.assertEqual(response.status_code, 302)
            self.assertEqual(response.url[:7], "/?next=")

        # user is logged in not friend
        request.user = user
        if ALBUM_PRIVATE >= level >= ALBUM_PUBLIC:
            response = func(request, id)
            self.assertEqual(response.status_code, 302)
        else:
            self.assertRaises(PermissionException, func, request, id)

        # user is logged in friend
        complete_add_friends(user.id, alb.owner.id)
        if ALBUM_PRIVATE >= level >= ALBUM_ALLFRIENDS:
            response = func(request, id)
            self.assertEqual(response.status_code, 302)
        else:
            self.assertRaises(PermissionException, func, request, id)

        # todo: user is in group

        # user is logged in contributor
        assert albumcontroller(alb.owner.user.id).add_contributor_to_album(alb, user.profile)
        if level == ALBUM_PRIVATE:
            response = func(request, id)
            self.assertEqual(response.status_code, 302)
        else:
            self.assertRaises(PermissionException, func, request, id)

        # user is owner - won't test in this fixture

    def setUp(self):
        super(test_manage_page_permissions, self).setUp()
        # view manage page
        self.managepagerequest = self.factory.get(reverse("manage_album", kwargs={'albumid': self.testalbum.id}))

        self.credentials3 = {
            'username': 'testuser3',
            'email': 'user3@test.com',
            'password': 'secret'}
        self.u3 = User.objects.create_user(**self.credentials3)
        self.u3.save()

    def test_get(self):
        """
        Owner and contributors can access manage page
        """
        self.perm_escalate_helper(self.albumcontrol, self.managepagerequest, self.testalbum, self.testalbum.id,
                                  self.u, album.manage_album_permissions, ALBUM_PRIVATE)
        # add u2 as contributor
        self.make_logged_in_contributor()

        self.perm_escalate_helper(self.albumcontrol, self.managepagerequest, self.testalbum, self.testalbum.id,
                                  self.u2, album.manage_album_permissions, ALBUM_PRIVATE)

        # contributor does not obtain addcontributorsform from get
        resp = self.client.get(reverse('manage_album', kwargs={'albumid': self.testalbum.id}))
        assert 'addcontributorsform' not in resp.context.keys()
        assert 'accesstypeform' not in resp.context.keys()
        # todo: elsewhere we need to add testing for group form if the access type is or is not groups

        # use u3 as control, not owner or contributor, pass 0 as permission, no access
        self.perm_escalate_helper(self.albumcontrol, self.managepagerequest, self.testalbum, self.testalbum.id,
                                  self.u3, album.manage_album_permissions, 0)


    def test_post_add_album_contrib_as_owner(self):
        """
        Owner can add and remove contributors
        """
        self.make_logged_in_owner()

        # get our manage page with form
        resp = self.client.get(reverse('manage_album', kwargs={'albumid': self.testalbum.id}))

        # get and populate form
        myform = resp.context['addcontributorsform']
        data = myform.initial
        data['idname'] = self.u2.id

        # construct our post
        self.addcontribpostrequest = self.factory.post(
            reverse("add_album_contrib", kwargs={"albumid": self.testalbum.id}), data=data)
        self.addcontribpostrequest.user = self.u

        # we do not successfully add because not friends, but still redirect
        # todo: why did this not raise?
        resp = album.add_contrib(self.addcontribpostrequest, self.testalbum.id)
        assert resp.status_code == 302
        assert not self.u2.profile in collate_owner_and_contrib(self.testalbum)

        # make friends and we will succeed in adding
        complete_add_friends(self.u.id, self.u2.id)

        resp = album.add_contrib(self.addcontribpostrequest, self.testalbum.id)
        assert resp.status_code == 302
        assert self.u2.profile in collate_owner_and_contrib(self.testalbum)

    def test_post_add_album_contrib_as_not_owner(self):
        """
        Contributor CAN'T add and remove contributors
        """
        complete_add_friends(self.u2.id, self.u3.id)

        self.make_logged_in_owner()

        # get our manage page with form (use self.u as self.u2 will not obtain the form)
        # using self.u will not affect our test later because we aren't using the client later
        resp = self.client.get(reverse('manage_album', kwargs={'albumid': self.testalbum.id}))

        # get and populate form
        myform = resp.context['addcontributorsform']
        data = myform.initial
        data['idname'] = self.u3.id

        # construct our post
        self.addcontribpostrequest = self.factory.post(
            reverse("add_album_contrib", kwargs={"albumid": self.testalbum.id}), data=data)

        self.user_escalate_post_test_helper(self.addcontribpostrequest, self.u2, self.testalbum, self.testalbum.id,
                                            album.add_contrib, ALBUM_PRIVATE+1)

    def test_post_add_remove_group(self):
        """
        Contributor can add/remove own groups if access type is groups
        Owner can add/remove own groups
        """
        # todo: think about what if owner doesn't want contributors to add groups
        # self.addgrouprequest = self.factory.post(reverse("add_album_groups"))
        pass

    def test_post_change_access_type_as_owner(self):
        """
        Only owner can edit album access type
        """
        assert self.testalbum.accesstype != ALBUM_GROUPS
        self.make_logged_in_owner()

        # get our manage page with form
        resp = self.client.get(reverse('manage_album', kwargs={'albumid': self.testalbum.id}))

        # get and populate form
        myform = resp.context['accesstypeform']
        data = myform.initial
        data['mytype'] = ALBUM_GROUPS

        # construct our post
        self.updateaccesspostrequest = self.factory.post(
            reverse("update_album_access", kwargs={"id": self.testalbum.id}), data=data)
        self.updateaccesspostrequest.user = self.u

        # change access type
        resp = album.update_access_type(self.updateaccesspostrequest, self.testalbum.id)
        assert resp.status_code == 302
        self.testalbum.refresh_from_db()
        assert self.testalbum.accesstype == ALBUM_GROUPS

    def test_post_change_access_type_as_not_owner(self):
        """
        Non owner can't change access type
        :return:
        """
        self.make_logged_in_owner()

        # get our manage page with form (use self.u as self.u2 will not obtain the form)
        # using self.u will not affect our test later because we aren't using the client later
        resp = self.client.get(reverse('manage_album', kwargs={'albumid': self.testalbum.id}))

        # get and populate form
        myform = resp.context['accesstypeform']
        data = myform.initial
        data['mytype'] = ALBUM_GROUPS

        # construct our post
        self.updateaccesspostrequest = self.factory.post(
            reverse("update_album_access", kwargs={"id": self.testalbum.id}), data=data)

        self.user_escalate_post_test_helper(self.updateaccesspostrequest, self.u2, self.testalbum, self.testalbum.id,
                                            album.update_access_type, ALBUM_PRIVATE + 1)

    def test_get_post_endpoints(self):
        """
        Get will return a 404 under all conditions
        """
        self.addcontribgetrequest = self.factory.get(
            reverse("add_album_contrib", kwargs={"albumid": self.testalbum.id}))
        self.addcontribgetrequest.user = self.u
        self.updateaccessgetrequest = self.factory.get(
            reverse("update_album_access", kwargs={"id": self.testalbum.id}))
        self.updateaccessgetrequest.user = self.u
        self.addgroupgetrequest = self.factory.get(reverse("add_album_groups", kwargs={"albumid":self.testalbum.id}))
        self.addgroupgetrequest.user = self.u

        self.assertRaises(Http404, album.add_contrib, self.addcontribgetrequest, self.testalbum.id)
        self.assertRaises(Http404, album.update_access_type, self.updateaccessgetrequest, self.testalbum.id)
        self.assertRaises(Http404, album.add_groups, self.addgroupgetrequest, self.testalbum.id)
        # todo: maybe make this a loop


class test_upload_photo_permissions(PermissionTestCase):
    def setUp(self):
        super(test_upload_photo_permissions, self).setUp()

        self.uploadphotorequest = self.factory.get(reverse("upload_photos", kwargs={'id': self.testalbum.id}))
        # todo: add post upload photo request

    def test_not_logged_in(self):
        # can't add photos to album
        # assign anonymous user to request
        self.uploadphotorequest.user = AnonymousUser()

        self.albumcontrol.set_accesstype(self.testalbum, ALBUM_PUBLIC)

        response = album.add_photo(self.uploadphotorequest, self.testalbum.id)
        # since we are not logged in, redirects to login page
        assert response.status_code == 302
        # may be good to add a post test for upload_photos, even though we have login_required decorator
        # just to have complete coverage

    def test_logged_in_not_friend(self):
        self.make_logged_in_not_friend()

        # test get upload photo page
        self.uploadphotorequest.user = self.u2
        self.albumcontrol.set_accesstype(self.testalbum, ALBUM_PUBLIC)

        self.assertRaises(PermissionException, album.add_photo, self.uploadphotorequest, self.testalbum.id)

    def test_logged_in_friend_not_in_group(self):
        self.make_logged_in_friend_not_in_group()
