from django.test import TestCase, Client
from django.test.client import RequestFactory
from django.shortcuts import reverse
from django.contrib.messages import get_messages

from django.contrib.auth.models import User

from ..view.usermgmt import *

# these need to be expanded out into user management tests
# probably in an additional test case class


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
        response = self.client.post(reverse("index"), data=self.credentials, follow=True)
        #request.session = self.client.session

        #response = index(request)
        #response.client = Client()
        #print(response)

        self.assertEqual(response.status_code, 200)
        #self.assertEqual(response.url, reverse("user_home"))

        # I suppose this tests our redirect through, sufficient?
        self.assertRedirects(response, reverse("user_home"))

        self.assertTrue(response.context['user'].is_authenticated)

    def test_logout(self):
        """
        Logout page (with follow True) should return 200 and leave user not authenticated
        """
        # login
        response = self.client.post('', self.credentials, follow=True)

        # logout
        response = self.client.post(reverse('logout'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['user'].is_authenticated)

        # if we try to logout again we get a 302 redirect (no follow) (to index page)
        response = self.client.post(reverse('logout'))
        self.assertEqual(response.status_code, 302)

    def test_invalid_login(self):
        badcredentials = {
            'username': 'testuser',
            'email': 'user@test.com',
            'password': 'notcorrect'}

        # send login data
        response = self.client.post(reverse("index"), badcredentials, follow=True)

        #print(response)

        # this will break after we update the login function with a redirect
        self.assertEqual(response.status_code, 200)

        # need to test flash message
        #msg = get_messages(response)
        #self.assertEqual(msg[0], "Invalid Login")

# we need to go to each page in urls.py and check the http response code under all conditions
