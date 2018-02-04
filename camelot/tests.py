from django.test import TestCase
from django.test.client import RequestFactory
from django.shortcuts import reverse

from django.contrib.auth.models import User

class LoginTests(TestCase):
    def setUp(self):
        self.credentials = {
            'username': 'testuser',
            'email': 'user@test.com',
            'password': 'secret'}
        u = User.objects.create_user(**self.credentials)
        u.save()

    def test_login(self):
        # send login data
        response = self.client.post('', self.credentials, follow=True)
        # should be logged in now
        self.assertTrue(response.context['user'].is_authenticated)

    def test_logout(self):
        pass

    def test_invalid_login(self):
        pass

from .controllers import albumcontroller
from .album import *

class AlbumTests(TestCase):
    # this setUp code needs to be made universal
    def setUp(self):
        self.credentials = {
            'username': 'testuser',
            'email': 'user@test.com',
            'password': 'secret'}
        self.u = User.objects.create_user(**self.credentials)
        self.u.save()

        # send login data
        #response = self.client.post('', self.credentials, follow=True)

        self.factory = RequestFactory()

    def test_create_controller(self):
        pass

    def test_create_view(self):
        # Create an instance of a GET request.
        request = self.factory.get(reverse("create_album"))
        request.user = self.u
        request.session = {}

        # Test my_view() as if it were deployed at /customer/details
        response = create_album(request)

        self.assertEqual(response.status_code, 200)

# we need to go to each page in urls.py and check the http response code under all conditions
