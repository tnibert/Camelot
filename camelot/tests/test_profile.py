from django.test import TestCase
from django.test.client import RequestFactory
from django.contrib.auth.models import User
from django.shortcuts import reverse
import os
import shutil
from ..controllers.profilecontroller import profilecontroller
from ..controllers.groupcontroller import groupcontroller
from ..controllers.albumcontroller import albumcontroller
from .helperfunctions import complete_add_friends
from ..constants import *
from ..view.profile import *
from ..view.usermgmt import activate_user_no_check


class ProfileControllerTests(TestCase):
    def setUp(self):
        self.credentials = {
            'username': 'testuser',
            'email': 'user@test.com',
            'password': 'secret'}
        self.u = User.objects.create_user(**self.credentials)
        self.u.save()
        activate_user_no_check(self.u)
        self.u.profile.description = "I don't think therefore I am"
        self.u.save()

        self.credentials = {
            'username': 'testuser2',
            'email': 'user2@test.com',
            'password': 'secret'}
        self.u2 = User.objects.create_user(**self.credentials)
        self.u2.save()
        activate_user_no_check(self.u2)
        self.u2.profile.description = "Hajimemashite yoroshiku onegaishimasu"
        self.u2.profile.save()

        self.profilecontrol1 = profilecontroller(self.u.id)
        self.profilecontrol2 = profilecontroller(self.u2.id)
        self.profilecontrolanon = profilecontroller()

    def test_return_profile_data(self):
        """
        Profile data returned by controller should match user and profile information from db
        If user gets own profile, friendstatus is None, a pending friend "pending", a friend "friends", not a friend "not friends"
        If non logged in user gets profile, friendstatus is None
        """
        test = self.profilecontrol1.return_profile_data(self.u2.id)
        assert test["friendstatus"] == "not friends"
        assert test["uid"] == self.u2.id
        assert test["name"] == self.u2.username
        assert test["description"] == self.u2.profile.description

        # test that there is no friendstatus if we get our own profile data
        test = self.profilecontrol1.return_profile_data(self.u.id)
        assert test["friendstatus"] is None

        # non logged in user sees profile
        # later we fine tune
        test = self.profilecontrolanon.return_profile_data(self.u2.id)
        assert test["friendstatus"] == None
        assert test["uid"] == self.u2.id
        assert test["name"] == self.u2.username
        assert test["description"] == self.u2.profile.description

    def test_update_profile_data(self):
        pass

    def test_set_profile_pic(self):

        # set up pre conditions
        self.testdir = "testdir"
        if not os.path.exists(self.testdir):
            os.makedirs(self.testdir)
        os.chdir(self.testdir)
        self.albumcontrol = albumcontroller(self.u.id)
        myalbum = self.albumcontrol.create_album("test album", "lalala")

        try:
            # double check that our test is sending the right type for fi and that django will sent in rb mode
            with open('../camelot/tests/resources/testimage.jpg', 'rb') as fi:
                myphoto = self.albumcontrol.add_photo_to_album(myalbum.id, "generic description", fi)
                # need to add checks for file existence and db existence

        # clean up
        except:
            os.chdir("..")
            shutil.rmtree(self.testdir)
            raise

        # add profile pic
        assert self.profilecontrol1.set_profile_pic(myphoto.id)
        self.u.profile.refresh_from_db()
        assert self.u.profile.profile_pic == myphoto

        # u2 doesn't own or contrib, so can't make profile pic
        assert not self.profilecontrol2.set_profile_pic(myphoto.id)
        self.u2.profile.refresh_from_db()
        assert self.u2.profile.profile_pic != myphoto

        # clean up
        os.chdir("..")
        shutil.rmtree(self.testdir)

    def test_get_feed(self):
        self.testdir = "testdir"
        if not os.path.exists(self.testdir):
            os.makedirs(self.testdir)
        os.chdir(self.testdir)

        complete_add_friends(self.u.id, self.u2.id)
        self.albumcontrol = albumcontroller(self.u2.id)
        self.groupcontrol = groupcontroller(self.u2.id)

        # create albums of each access type, two for groups (one u is in group, one u is not in group)
        alb = []
        phot = []
        try:
            with open('../camelot/tests/resources/testimage.jpg', 'rb') as fi:
                for i in range(5):
                    alb.append(self.albumcontrol.create_album("test {}".format(i), "test"))
                    phot.append(self.albumcontrol.add_photo_to_album(alb[i].id, "description {}".format(i), fi))

            self.albumcontrol.set_accesstype(alb[0], ALBUM_PRIVATE)
            self.albumcontrol.set_accesstype(alb[1], ALBUM_GROUPS)
            self.albumcontrol.set_accesstype(alb[2], ALBUM_GROUPS)
            self.albumcontrol.set_accesstype(alb[3], ALBUM_ALLFRIENDS)
            self.albumcontrol.set_accesstype(alb[4], ALBUM_PUBLIC)

            testgroup = self.groupcontrol.create("testgroup")

            self.albumcontrol.add_group_to_album(alb[1], testgroup)
            self.groupcontrol.add_member(testgroup.id, self.u.profile)

            feed = self.profilecontrol1.get_feed()

            # test that we filter correctly by permissions
            assert phot[4] in feed
            assert phot[3] in feed
            assert phot[2] not in feed
            assert phot[1] in feed
            assert phot[0] not in feed

            # assert that photos are ordered correctly (newest to oldest)
            # todo: the pub_dates of the photos don't vary?  at least not in display, and the following assert doesn't work
            #assert feed[0] is phot[4]

        finally:
            # clean up
            os.chdir("..")
            shutil.rmtree(self.testdir)


class ProfileViewTestsLoggedIn(TestCase):
    def setUp(self):
        # create user
        self.credentials = {
            'username': 'testuser',
            'email': 'user@test.com',
            'password': 'secret'}
        self.u = User.objects.create_user(**self.credentials)
        self.u.save()

        activate_user_no_check(self.u)

        # send login data
        response = self.client.post('', self.credentials, follow=True)

        self.factory = RequestFactory()

    def test_show_profile(self):
        """
        Profile page should return 200 for all users logged in and not logged in
        Content will vary based on profile permissions?  Maybe not, just albums
        """
        # Create an instance of a GET request.
        request = self.factory.get(reverse("show_profile", kwargs={'userid': self.u.id}))
        request.user = self.u
        request.session = {}

        # self.client.get()?
        response = show_profile(request, self.u.id)

        self.assertEqual(response.status_code, 200)

        # test with another user's id

    def test_update_profile_get(self):
        """
        Logged in user should be able to get update profile page
        """
        request = self.factory.get(reverse("update_profile"))
        request.user = self.u
        request.session = {}

        response = update_profile(request)

        self.assertEqual(response.status_code, 200)

    def test_update_profile_post(self):
        """
        Logged in user should be able to update profile information via post
        This is our template for how to test a post
        """

        response = self.client.get(reverse('update_profile'))

        myform = response.context['form']

        dname = "Test Name"
        description = "I am a pumpkin"
        data = myform.initial
        data['displayname'] = dname
        data['description'] = description

        response = self.client.post(reverse('update_profile'), data, follow=True)

        self.assertEqual(response.status_code, 200)
        self.u.profile.refresh_from_db()
        assert self.u.profile.description == description
        assert self.u.profile.dname == dname


class ProfileViewTestsNotLoggedIn(TestCase):
    def setUp(self):
        # create user
        self.credentials = {
            'username': 'testuser',
            'email': 'user@test.com',
            'password': 'secret'}
        self.u = User.objects.create_user(**self.credentials)
        self.u.save()

        self.factory = RequestFactory()

    def test_show_profile(self):
        """
        Non logged in user should be able to view profile
        unless private
        :return:
        """
        pass

    def test_update_profile_get(self):
        """
        Non logged in user should not be able to get update profile page
        :return:
        """
        pass

    def test_update_profile_post(self):
        """
        Non logged in user should not be able to post to update profile
        :return:
        """
        pass
