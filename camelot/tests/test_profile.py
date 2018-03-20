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
        test = self.profilecontrol1.return_profile_data(self.u2.id)
        assert test["friendstatus"] == "not friends"
        assert test["uid"] == self.u2.id
        assert test["name"] == self.u2.username
        assert test["description"] == self.u2.profile.description

    def test_update_profile_data(self):
        pass

from ..view.profile import *

class ProfileViewTests(TestCase):
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
        # Create an instance of a GET request.
        request = self.factory.get(reverse("show_profile", kwargs={'userid': self.u.id}))
        request.user = self.u
        request.session = {}

        response = show_profile(request, self.u.id)

        self.assertEqual(response.status_code, 200)

        # test with another user's id

    def test_update_profile_view(self):
        pass