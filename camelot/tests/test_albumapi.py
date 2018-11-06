from django.test import TestCase
from django.contrib.auth.models import User
from django.test.client import RequestFactory
from django.shortcuts import reverse
import json
import os
from ..controllers.albumcontroller import albumcontroller

class albumAPItests(TestCase):
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

        self.albumcontrol = albumcontroller(self.u.id)

    def test_album_upload(self):
        albumid = self.albumcontrol.create_album("album for test", "lalala").id

        fi = 'camelot/tests/resources/testimage.jpg'
        payload = {"description": "this is a test"}
        files = {
            'json': (None, json.dumps(payload), 'application/json'),
            'file': (os.path.basename(fi), open(fi, 'rb'), 'application/octet-stream')
        }

        response = self.client.post(reverse("uploadphotoapi", kwargs={'id': albumid}),
                                    files=files)

        self.assertEqual(response.status_code, 204)
