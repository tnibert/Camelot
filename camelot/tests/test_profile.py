from django.test import TestCase
from django.test.client import RequestFactory
from django.contrib.auth.models import User
from django.shortcuts import reverse

from ..controllers import profilecontroller

class ProfileControllerTests(TestCase):
    def setUp(self):
        self.credentials = {
            'username': 'testuser',
            'email': 'user@test.com',
            'password': 'secret'}
        self.u = User.objects.create_user(**self.credentials)
        self.u.profile.description = "I don't think therefore I am"
        self.u.save()

        self.credentials = {
            'username': 'testuser2',
            'email': 'user2@test.com',
            'password': 'secret'}
        self.u2 = User.objects.create_user(**self.credentials)
        self.u2.profile.description = "Hajimemashite yoroshiku onegaishimasu"
        self.u2.save()

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

from ..view.profile import *

class ProfileViewTestsLoggedIn(TestCase):
    def setUp(self):
        # create user
        self.credentials = {
            'username': 'testuser',
            'email': 'user@test.com',
            'password': 'secret'}
        self.u = User.objects.create_user(**self.credentials)
        self.u.save()

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
        This test is broken, we aren't sending a valid csrf token
        Probably need to get page first, get csrf token from that, then post in same session
        """
        #from urllib.parse import urlencode
        description = "I am a pumpkin"
        data = {'description': description}
        #request = self.factory.post(reverse("update_profile"), data=data, content_type="application/x-www-form-urlencoded")
        request = self.factory.post(reverse("update_profile"), data)
        request.user = self.u
        request.session = {}

        response = self.client.post(reverse("update_profile"), data, follow=True)

        self.assertEqual(response.status_code, 200)
        print(self.u.profile.description)
        assert self.u.profile.description == description

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