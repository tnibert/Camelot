from django.test import TestCase
from django.test.client import RequestFactory
from django.shortcuts import reverse

from django.contrib.auth.models import User

from ..controllers.albumcontroller import albumcontroller, collate_owner_and_contrib
from ..controllers.groupcontroller import groupcontroller
from ..controllers.utilities import *
from ..view.album import *
from .helperfunctions import complete_add_friends
from ..constants import *

import os
import shutil

class AlbumControllerTests(TestCase):
    # this setUp code needs to be made universal
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
        response = self.client.post('', self.credentials, follow=True)

        self.factory = RequestFactory()
        self.albumcontrol = albumcontroller(self.u.id)
        self.albumcontrol2 = albumcontroller(self.u2.id)

        # not logged in
        self.albumcontrol3 = albumcontroller()

        self.groupcontrol = groupcontroller(self.u.id)

        self.testdir = "testdir"

    def test_get_profile_from_uid(self):
        profile = get_profile_from_uid(self.u.id)
        self.assertEqual(profile.user, self.u)
        self.assertEqual(self.u.profile, profile)

    def test_create_controller_duplicate_name(self):
        self.albumcontrol.create_album("test title", "test description")
        self.assertRaises(AlreadyExistsException, self.albumcontrol.create_album, "test title", "test description2")

    def test_return_albums_controller(self):
        # can't count on tests running in order
        self.albumcontrol.create_album("a test title", "test description")
        albums = self.albumcontrol.return_albums()

        # there's probably some string compare assert for this
        assert albums[0].name == "a test title"
        assert albums[0].description == "test description"

    def test_return_album(self):
        newalbum = self.albumcontrol.create_album("return album test", "lalala")
        testalbum = self.albumcontrol.return_album(newalbum.id)
        assert newalbum == testalbum
        self.assertRaises(PermissionException, self.albumcontrol2.return_album, newalbum.id)


    def test_add_image_to_album_controller(self):

        if not os.path.exists(self.testdir):
            os.makedirs(self.testdir)
        os.chdir(self.testdir)

        myalbum = self.albumcontrol.create_album("image add test", "lalala")

        try:
            # double check that our test is sending the right type for fi and that django will sent in rb mode
            with open('../camelot/tests/resources/testimage.jpg', 'rb') as fi:
                self.albumcontrol.add_photo_to_album(myalbum.id, "generic description", fi)
                # need to add checks for file existence and db existence

        # clean up
        except:
            os.chdir("..")
            shutil.rmtree(self.testdir)
            raise
        os.chdir("..")
        shutil.rmtree(self.testdir)
        # example (for view):
        #c = Client()
        #with open('wishlist.doc') as fp:
        #    c.post('/customers/wishes/', {'name': 'fred', 'attachment': fp})

    def test_add_image_to_other_user_album_controller(self):
        """
        User should not be able to add image to another user's album
        :return:
        """
        if not os.path.exists(self.testdir):
            os.makedirs(self.testdir)
        os.chdir(self.testdir)

        notmyalbum = self.albumcontrol2.create_album("other person's album", "ruh roh")

        with open('../camelot/tests/resources/testimage.jpg', 'rb') as fi:
            self.assertRaises(PermissionException, self.albumcontrol.add_photo_to_album, notmyalbum.id, "generic description", fi)

        os.chdir("..")
        shutil.rmtree(self.testdir)

    def test_get_images_for_album(self):
        # implemented
        pass

    def test_add_contributor_to_album(self):
        """
        Test adding a contributor to album
        Owner and new contributor must be friends
        """

        testalbum = self.albumcontrol.create_album("test album", "test description")

        # not friends, cannot add
        assert not self.albumcontrol.add_contributor_to_album(testalbum, self.u2.profile)
        assert len(testalbum.contributors.all()) == 0

        # add friends
        complete_add_friends(self.u.id, self.u2.id)
        # now can add contributor
        assert self.albumcontrol.add_contributor_to_album(testalbum, self.u2.profile)

        assert len(testalbum.contributors.all()) == 1
        assert self.u2.profile in testalbum.contributors.all()

        # confirm cannot re add contributor
        self.albumcontrol.add_contributor_to_album(testalbum, self.u2.profile)
        assert len(testalbum.contributors.all()) == 1

    def test_add_group_to_album(self):
        """
        Test adding a group to an album
        Need to test that we can't add group to album that is not our own
        :return:
        """
        groupcontrol = groupcontroller(self.u.id)
        testgroup = groupcontrol.create("test group")
        testalbum = self.albumcontrol.create_album("test album", "test description")
        self.albumcontrol.add_group_to_album(testalbum, testgroup)
        assert len(testalbum.groups.all()) == 1
        assert testgroup in testalbum.groups.all()

        # confirm adding a second time does nothing
        self.albumcontrol.add_group_to_album(testalbum, testgroup)
        assert len(testalbum.groups.all()) == 1

        # confirm can't add group to another user's album
        groupcontrol2 = groupcontroller(self.u2.id)
        testgroup2 = groupcontrol2.create("test group 2")

        assert not self.albumcontrol2.add_group_to_album(testalbum, testgroup2)

        # can't add group we don't own to an album
        assert not self.albumcontrol.add_group_to_album(testalbum, testgroup2)

        # add friends, but still cannot add group to friend's album
        complete_add_friends(self.u.id, self.u2.id)
        assert not self.albumcontrol2.add_group_to_album(testalbum, testgroup)

        assert len(testalbum.groups.all()) == 1

        # add as contributor
        self.albumcontrol.add_contributor_to_album(testalbum, self.u2.profile)
        # confirm can add group to other user's album
        assert self.albumcontrol2.add_group_to_album(testalbum, testgroup2)

        assert testgroup in testalbum.groups.all()
        assert testgroup2 in testalbum.groups.all()
        assert len(testalbum.groups.all()) == 2

    def test_remove_image_from_album(self):
        pass

    def test_download_album(self):
        pass

    def test_remove_contributor_from_album(self):
        pass

    def test_get_album_contributors(self):
        pass

    def test_user_access(self):
        """
        Permissions check to view album
        We have groups and we have access types
        Access types are more universal - public, all friends, groups, private
        Groups take effect in the groups access type
        Test takes permission check through full range of relationships
        Need to test for user not logged in case
        """
        testalbum = self.albumcontrol.create_album("access test", "testing access")
        # owner can view
        assert self.albumcontrol.has_permission_to_view(testalbum)

        # change access to public
        self.albumcontrol.set_accesstype(testalbum, ALBUM_PUBLIC)
        # non friend can view album
        assert self.albumcontrol2.has_permission_to_view(testalbum)
        assert self.albumcontrol3.has_permission_to_view(testalbum)

        # change access to all friends, non friend cannot view
        self.albumcontrol.set_accesstype(testalbum, ALBUM_ALLFRIENDS)
        assert not self.albumcontrol2.has_permission_to_view(testalbum)
        assert not self.albumcontrol3.has_permission_to_view(testalbum)

        # add friend and can view
        complete_add_friends(self.u.id, self.u2.id)
        assert self.albumcontrol2.has_permission_to_view(testalbum)

        # change access to groups, friend cannot view
        self.albumcontrol.set_accesstype(testalbum, ALBUM_GROUPS)
        assert not self.albumcontrol2.has_permission_to_view(testalbum)

        # create group, add member, and add group to album
        # friend will be able to view
        testgroup = self.groupcontrol.create("test group")
        self.groupcontrol.add_member(testgroup.id, self.u2.profile)
        self.albumcontrol.add_group_to_album(testalbum, testgroup)
        assert self.albumcontrol2.has_permission_to_view(testalbum)

        # set access to private
        self.albumcontrol.set_accesstype(testalbum, ALBUM_PRIVATE)
        assert not self.albumcontrol2.has_permission_to_view(testalbum)

        # contributor can view
        self.albumcontrol.add_contributor_to_album(testalbum, self.u2.profile)
        assert self.albumcontrol2.has_permission_to_view(testalbum)
        # owner can view
        assert self.albumcontrol.has_permission_to_view(testalbum)

    def test_collate_owner_and_contrib(self):
        """
        Test collate_owner_and_contrib(), returns list of album owner and contributors
        """
        testalbum = self.albumcontrol.create_album("collate test", "testing collate tool")
        complete_add_friends(self.u.id, self.u2.id)
        self.albumcontrol.add_contributor_to_album(testalbum, self.u2.profile)
        contribs = collate_owner_and_contrib(testalbum)
        assert len(contribs) == 2
        assert self.u.profile in contribs
        assert self.u2.profile in contribs

    def test_change_access_type(self):
        """
        Default access type is all friends
        Only owner can change access type
        Access type must be valid integer
        :return:
        """
        testalbum = self.albumcontrol.create_album("access type test", "testing access type")
        # default all friends
        assert testalbum.accesstype == ALBUM_ALLFRIENDS

        # change to public
        assert self.albumcontrol.set_accesstype(testalbum, ALBUM_PUBLIC)
        assert testalbum.accesstype == ALBUM_PUBLIC

        # change to groups
        assert self.albumcontrol.set_accesstype(testalbum, ALBUM_GROUPS)
        assert testalbum.accesstype == ALBUM_GROUPS

        # change to private
        assert self.albumcontrol.set_accesstype(testalbum, ALBUM_PRIVATE)
        assert testalbum.accesstype == ALBUM_PRIVATE

        # set an album you don't own
        testalbum2 = self.albumcontrol2.create_album("set invalid", "test set invalid")
        assert not self.albumcontrol.set_accesstype(testalbum2, ALBUM_PUBLIC)
        assert testalbum2.accesstype == ALBUM_ALLFRIENDS

        # set to float and invalid int
        assert not self.albumcontrol.set_accesstype(testalbum, 2.5)
        assert not self.albumcontrol.set_accesstype(testalbum, 100)
        assert testalbum.accesstype == ALBUM_PRIVATE


class AlbumViewTests(TestCase):
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
        response = self.client.post('', self.credentials, follow=True)

        self.factory = RequestFactory()

    def test_album_view(self):
        # implemented
        pass

    def test_create_view(self):
        # Create an instance of a GET request.
        request = self.factory.get(reverse("create_album"))
        request.user = self.u
        request.session = {}

        # Test my_view() as if it were deployed at /customer/details
        response = create_album(request)

        self.assertEqual(response.status_code, 200)