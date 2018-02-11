from django.test import TestCase
from django.test.client import RequestFactory
from django.shortcuts import reverse

from django.contrib.auth.models import User

from ..view.usermgmt import *

class LoginTests(TestCase):
    def setUp(self):
        self.credentials = {
            'username': 'testuser',
            'email': 'user@test.com',
            'password': 'secret'}
        self.u = User.objects.create_user(**self.credentials)
        self.u.save()

        self.factory = RequestFactory()

    def test_login(self):
        # send login data
        response = self.client.post('', self.credentials, follow=True)
        # should be logged in now
        self.assertTrue(response.context['user'].is_authenticated)

    def test_login_view_post(self):
        request = self.factory.post(reverse("index"), data=self.credentials)
        request.session = self.client.session

        response = index(request)

        # response 302 again... hmm
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['user'].is_authenticated)

    def test_logout(self):
        pass

    def test_invalid_login(self):
        pass

# we need to go to each page in urls.py and check the http response code under all conditions
