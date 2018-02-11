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
        request = self.factory.post(reverse("index"), data=self.credentials, follow=True)
        request.session = self.client.session

        response = index(request)
        #print(response)

        # response 302 again... hmm
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/home")     # update this with reverse to not directly reference the string

        # need to follow request through...
        self.assertTrue(response.context['user'].is_authenticated)

    def test_logout(self):
        pass

    def test_invalid_login(self):
        badcredentials = {
            'username': 'testuser',
            'email': 'user@test.com',
            'password': 'notcorrect'}

        # send login data
        response = self.client.post('', badcredentials, follow=True)

        print(response)

        # this will break after we update the login function with a redirect
        self.assertEqual(response.status_code, 200)

# we need to go to each page in urls.py and check the http response code under all conditions
