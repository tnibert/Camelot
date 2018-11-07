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

    def test_photo_upload(self):
        albumid = self.albumcontrol.create_album("album for test", "lalala").id

        with open('camelot/tests/resources/testimage.jpg', 'rb') as f:
            # this request is probably wrong
            response = self.client.post(reverse("uploadphotoapi", kwargs={'id': albumid}), files={'image': f})

        print(response.text)
        self.assertEqual(response.status_code, 201)

    def test_photo_description_update(self):
        seconddesc = "this is the second description"
        payload = {"description": seconddesc}

        # set up test
        albumid = self.albumcontrol.create_album("album for test2", "lalala").id
        with open('camelot/tests/resources/testimage.jpg', 'rb') as f:
            newphoto = self.albumcontrol.add_photo_to_album(albumid, "this is the first description", f)

        # send request
        response = self.client.post(reverse("uploadphotoapi", kwargs={'id': albumid}), data=payload)

        # checks
        newphoto.refresh_from_db()
        assert newphoto.description == seconddesc
        self.assertEqual(response.status_code, 204)