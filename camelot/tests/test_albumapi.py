from django.test import TestCase
from django.contrib.auth.models import User
from django.test.client import RequestFactory
from django.shortcuts import reverse
import json
import os
from ..controllers.albumcontroller import albumcontroller
from .helperfunctions import complete_add_friends

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
        self.albumcontrol2 = albumcontroller(self.u2.id)

    def test_photo_upload(self):
        """
        Test regular usage of photo upload via API
        :return:
        """
        albumid = self.albumcontrol.create_album("album for test", "lalala").id

        with open('camelot/tests/resources/testimage.jpg', 'rb') as f:
            response = self.client.post(reverse("uploadphotoapi", kwargs={'id': albumid}), {'image': f}, enctype="multipart/form-data")

        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data['id'], 1)
        self.assertEqual(response.status_code, 201)

    def test_photo_upload_non_image(self):
        """
        Test upload of code via photo upload API, should not work
        todo: manually test
        :return:
        """
        albumid = self.albumcontrol.create_album("album for test", "lalala").id

        with open('camelot/tests/resources/notanimage.jpg', 'rb') as f:
            with self.assertRaises(Exception):
                response = self.client.post(reverse("uploadphotoapi", kwargs={'id': albumid}), {'image': f},
                                        enctype="multipart/form-data")

    def test_photo_description_update(self):
        """
        Test regular usage of photo description update via API
        :return:
        """
        seconddesc = "this is the second description"
        payload = {"description": seconddesc}

        # set up test
        albumid = self.albumcontrol.create_album("album for test2", "lalala").id
        with open('camelot/tests/resources/testimage.jpg', 'rb') as f:
            newphoto = self.albumcontrol.add_photo_to_album(albumid, "this is the first description", f)

        # send request
        response = self.client.post(reverse("updatephotodescapi", kwargs={'photoid': newphoto.id}),
                                    json.dumps(payload),
                                    content_type="application/json")

        # checks
        newphoto.refresh_from_db()
        self.assertEqual(response.status_code, 204)
        assert newphoto.description == seconddesc

    def test_photo_description_sql_injection(self):
        """
        Test SQL injection via photo description update in API
        :return:
        todo: manually test
        """
        injectstr = "; update from camelot_photo set description='oh hai';"
        payload = {"description": injectstr}

        # set up test
        albumid = self.albumcontrol.create_album("album sql inject test", "lalala").id
        # todo: set album to public
        with open('camelot/tests/resources/testimage.jpg', 'rb') as f:
            newphoto = self.albumcontrol.add_photo_to_album(albumid, "this is the first description", f)
            secondphoto = self.albumcontrol.add_photo_to_album(albumid, "this is the second description", f)

        # send request
        response = self.client.post(reverse("updatephotodescapi", kwargs={'photoid': newphoto.id}),
                                    json.dumps(payload),
                                    content_type="application/json")

        # todo: create get request that displays the

        # checks
        newphoto.refresh_from_db()
        #print(newphoto.description)
        assert newphoto.description == "; update from camelot_photo set description=&#x27;oh hai&#x27;;"
        assert secondphoto.description == "this is the second description";

    def test_photo_description_aslan(self):
        """
        Failed to upload "aslan" as description from js front end
        Testing in unit test to isolate issue - seems to work in back end testing
        :return:
        """
        str = "aslan"
        payload = {"description": str}

        # set up test
        albumid = self.albumcontrol.create_album("album", "lalala").id
        with open('camelot/tests/resources/testimage.jpg', 'rb') as f:
            newphoto = self.albumcontrol.add_photo_to_album(albumid, "", f)

        # send request
        response = self.client.post(reverse("updatephotodescapi", kwargs={'photoid': newphoto.id}),
                                    json.dumps(payload),
                                    content_type="application/json")

        # checks
        newphoto.refresh_from_db()
        #print(newphoto.description)
        self.assertEqual(response.status_code, 204)
        assert newphoto.description == str

    def test_get_albums(self):
        """
        Test the getalbumsapi api call
        """

        # u2 adds two albums, not public (by default)
        self.albumcontrol2.create_album("test1", "testdesc1")
        self.albumcontrol2.create_album("test2", "testdesc2")

        # u requests albums
        response = self.client.get(reverse("getalbumsapi", kwargs={'userid': self.u2.id}))
        self.assertEqual(response.status_code, 200)

        # assert content, no albums
        data = json.loads(response.content.decode('utf-8'))
        #print(data)
        self.assertEqual(data['albums'], [])

        # complete add friends
        complete_add_friends(self.u.id, self.u2.id)

        # u requests albums
        response = self.client.get(reverse("getalbumsapi", kwargs={'userid': self.u2.id}))
        self.assertEqual(response.status_code, 200)

        # assert content, 2 albums
        data = json.loads(response.content.decode('utf-8'))
        #print(data)
        self.assertEqual(data['albums'], [{'id': 1, 'name': 'test1', 'description': 'testdesc1'}, {'id': 2, 'name': 'test2', 'description': 'testdesc2'}])

