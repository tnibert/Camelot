from django.test import TestCase
from django.test.client import RequestFactory
from django.shortcuts import reverse
from django.contrib.auth.models import User
from PIL import Image
from ..models import Album, Photo
from ..controllers.albumcontroller import *
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

    def test_return_contrib_albums(self):
        """
        Return a list of albums that the profile contributes to
        This is currently broken
        """
        complete_add_friends(self.u.id, self.u2.id)
        testalbum = self.albumcontrol.create_album("a test title", "test description")
        assert self.albumcontrol.add_contributor_to_album(testalbum, self.u2.profile)

        testalbum2 = self.albumcontrol.create_album("another test title", "another test description")
        assert self.albumcontrol.add_contributor_to_album(testalbum2, self.u2.profile)

        albums = self.albumcontrol2.return_albums(contrib=True)

        # there's probably some string compare assert for this
        assert albums[0].name == "a test title"
        assert albums[0].description == "test description"
        assert albums[1].name == "another test title"
        assert albums[1].description == "another test description"

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
            # todo: add a test for png
            with open('../camelot/tests/resources/testimage.jpg', 'rb') as fi:
                myphoto = self.albumcontrol.add_photo_to_album(myalbum.id, "generic description", fi)

            # asserts
            assert myphoto.uploader == self.u.profile
            assert myphoto.album == myalbum
            assert myphoto.description == "generic description"
            assert myphoto.filename == "userphotos/1/1/1"
            assert myphoto.thumb == "thumbs/1/1/1.jpg"
            assert myphoto.midsize == "mid/1/1/1.jpg"

            # test file existence
            assert os.path.isfile(myphoto.filename)
            assert os.path.isfile(myphoto.thumb)
            assert os.path.isfile(myphoto.midsize)

            with Image.open(myphoto.thumb) as img:
                assert img.format == "JPEG"

            with Image.open(myphoto.midsize) as img:
                assert img.format == "JPEG"

        finally:
            # clean up
            os.chdir("..")
            shutil.rmtree(self.testdir)

        # example (for view):
        #c = Client()
        #with open('wishlist.doc') as fp:
        #    c.post('/customers/wishes/', {'name': 'fred', 'attachment

    def test_get_rotation(self):
        if not os.path.exists(self.testdir):
            os.makedirs(self.testdir)
        os.chdir(self.testdir)

        myalbum = self.albumcontrol.create_album("image add test", "lalala")

        try:
            # todo: add a test image with exif rotation tag
            # todo: flesh out this test a bit
            with open('../camelot/tests/resources/testimage.jpg', 'rb') as fi:
                myphoto = self.albumcontrol.add_photo_to_album(myalbum.id, "generic description", fi)
                assert myphoto.exiforientation is None
                assert get_rotation(myphoto) == ""
                myphoto.refresh_from_db()
                assert myphoto.exiforientation == 1

        finally:
            # clean up
            os.chdir("..")
            shutil.rmtree(self.testdir)


    def test_add_image_to_other_user_album_controller(self):
        """
        User should not be able to add image to another user's album
        :return:
        """
        if not os.path.exists(self.testdir):
            os.makedirs(self.testdir)
        os.chdir(self.testdir)

        notmyalbum = self.albumcontrol2.create_album("other person's album", "ruh roh")

        try:
            with open('../camelot/tests/resources/testimage.jpg', 'rb') as fi:
                self.assertRaises(PermissionException, self.albumcontrol.add_photo_to_album, notmyalbum.id, "generic description", fi)

        finally:
            os.chdir("..")
            shutil.rmtree(self.testdir)

    def test_delete_photo(self):
        # set up dir
        if not os.path.exists(self.testdir):
            os.makedirs(self.testdir)
        os.chdir(self.testdir)

        # create album
        myalbum = self.albumcontrol.create_album("delete photo test", "lalala")

        complete_add_friends(self.u.id, self.u2.id)

        # add contributor
        assert self.albumcontrol.add_contributor_to_album(myalbum, self.u2.profile)

        # add photos - one as owner, two as contrib
        try:
            with open('../camelot/tests/resources/testimage.jpg', 'rb') as fi:
                ownerphoto = self.albumcontrol.add_photo_to_album(myalbum.id, "owner uploaded", fi)
                contribphoto1 = self.albumcontrol2.add_photo_to_album(myalbum.id, "contrib uploaded 1", fi)
                contribphoto2 = self.albumcontrol2.add_photo_to_album(myalbum.id, "contrib uploaded 2", fi)

            # files exist
            assert os.path.isfile('userphotos/1/1/1')
            assert os.path.isfile('userphotos/2/1/2')
            assert os.path.isfile('userphotos/2/1/3')

            # cannot delete any photo as non logged in user
            # todo: add user privilege escalation
            self.assertRaises(PermissionException, self.albumcontrol3.delete_photo, ownerphoto)
            self.assertRaises(PermissionException, self.albumcontrol3.delete_photo, contribphoto1)

            # cannot delete owner photo as contributor
            self.assertRaises(PermissionException, self.albumcontrol2.delete_photo, ownerphoto)

            # can delete contributor photo as contributor
            assert self.albumcontrol2.delete_photo(contribphoto1)

            # can delete contributor photo as owner
            assert self.albumcontrol.delete_photo(contribphoto2)

            # can delete owner photo as owner
            assert self.albumcontrol.delete_photo(ownerphoto)

            assert (ownerphoto, contribphoto1, contribphoto2) not in self.albumcontrol.get_photos_for_album(myalbum)

            # check that db objects are gone
            self.assertRaises(Photo.DoesNotExist, ownerphoto.refresh_from_db)
            self.assertRaises(Photo.DoesNotExist, contribphoto1.refresh_from_db)
            self.assertRaises(Photo.DoesNotExist, contribphoto2.refresh_from_db)

            # check that files have actually been deleted on disk
            assert not os.path.isfile('userphotos/1/1/1')
            assert not os.path.isfile('userphotos/2/1/2')
            assert not os.path.isfile('userphotos/2/1/3')

        finally:
            # clean up
            os.chdir("..")
            shutil.rmtree(self.testdir)

    def test_delete_album(self):
        # set up dir
        if not os.path.exists(self.testdir):
            os.makedirs(self.testdir)
        os.chdir(self.testdir)
        #print(os.getcwd())

        # create album
        myalbum = self.albumcontrol.create_album("delete album test", "lalala")

        complete_add_friends(self.u.id, self.u2.id)

        # add contributor
        assert self.albumcontrol.add_contributor_to_album(myalbum, self.u2.profile)

        # add photos - one as owner, two as contrib
        try:
            with open('../camelot/tests/resources/testimage.jpg', 'rb') as fi:
                ownerphoto = self.albumcontrol.add_photo_to_album(myalbum.id, "owner uploaded", fi)
                contribphoto1 = self.albumcontrol2.add_photo_to_album(myalbum.id, "contrib uploaded 1", fi)
                contribphoto2 = self.albumcontrol2.add_photo_to_album(myalbum.id, "contrib uploaded 2", fi)

            # image files exist
            assert os.path.isfile('userphotos/1/1/1')
            assert os.path.isfile('userphotos/2/1/2')
            assert os.path.isfile('userphotos/2/1/3')

            # non owner cannot delete
            self.assertRaises(PermissionException, self.albumcontrol2.delete_album, myalbum)
            # owner can delete
            assert self.albumcontrol.delete_album(myalbum)

            # myalbum no longer exists
            self.assertRaises(Album.DoesNotExist, myalbum.refresh_from_db)

            # image files no longer exist
            assert not os.path.isfile('userphotos/1/1/1')
            assert not os.path.isfile('userphotos/2/1/2')
            assert not os.path.isfile('userphotos/2/1/3')

        # todo: apply this finally pattern to other file opening unit tests
        finally:
            # clean up
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

    def test_create_thumbnail_in_memory(self):

        with open('camelot/tests/resources/testimage.jpg', 'rb') as fi:
            try:
                thumb = ThumbFromBuffer(fi, "blahblahblah.jpg")
                # testimage is a square, so thumbheight will work for both - 180
                # todo: improve test with multi dimensioned image
                assert thumb.size[0] == THUMBHEIGHT         # width
                assert thumb.size[1] == THUMBHEIGHT         # height
                # todo: assert file exists blahblahblah.jpg
            finally:
                os.unlink("blahblahblah.jpg")


class AlbumViewTests(TestCase):
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

        response = create_album(request)

        self.assertEqual(response.status_code, 200)

    def test_add_photos(self):
        # test add one photo
        # test add two
        # test add three
        pass