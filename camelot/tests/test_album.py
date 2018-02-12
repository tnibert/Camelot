from django.test import TestCase
from django.test.client import RequestFactory
from django.shortcuts import reverse

from django.contrib.auth.models import User

from ..controllers.albumcontroller import albumcontroller, get_profile_from_uid
from ..view.album import *

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
        response = self.client.post('', self.credentials, follow=True)

        self.factory = RequestFactory()
        self.albumcontrol = albumcontroller(self.u.id)

    def test_get_profile_from_uid(self):
        profile = get_profile_from_uid(self.u.id)
        self.assertEqual(profile.user, self.u)
        self.assertEqual(self.u.profile, profile)

    def test_create_controller(self):
        self.albumcontrol.create_album("test title", "test description")
        # need to either add an assert of accept that test_return_albums() tests this

    def test_create_view(self):
        # Create an instance of a GET request.
        request = self.factory.get(reverse("create_album"))
        request.user = self.u
        request.session = {}

        # Test my_view() as if it were deployed at /customer/details
        response = create_album(request)

        self.assertEqual(response.status_code, 200)

    def test_return_albums(self):
        # can't count on tests running in order
        self.albumcontrol.create_album("test title", "test description")
        albums = self.albumcontrol.return_albums()

        # there's probably some string compare assert for this
        assert albums[0].name == "test title"
        assert albums[0].description == "test description"

    # the following tests are for functionality that hasn't been written yet
    # just defining the future path
    def test_add_image_to_album(self):
        pass

    def test_remove_image_from_album(self):
        pass

    def test_download_album(self):
        pass

    def test_add_contributor_to_album(self):
        pass

    def test_remove_contributor_from_album(self):
        pass

    def test_get_album_contributors(self):
        pass

    def test_user_can_access(self):
        pass

    def test_user_cant_access(self):
        pass
