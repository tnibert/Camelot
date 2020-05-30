from django.test import TestCase
from django.http import Http404
from django.contrib.auth.models import User
from ..controllers.genericcontroller import genericcontroller
from ..view.usermgmt import activate_user_no_check


class GenericControllerTests(TestCase):

    def test_init(self):
        g = genericcontroller()
        assert g.uprofile is None

        self.credentials = {
            'username': 'testuser',
            'email': 'user@test.com',
            'password': 'secret'}
        self.u = User.objects.create_user(**self.credentials)
        self.u.save()

        with self.assertRaises(Http404):
            g = genericcontroller(self.u.id)

        activate_user_no_check(self.u)
        g = genericcontroller(self.u.id)
        assert g.uprofile == self.u.profile
