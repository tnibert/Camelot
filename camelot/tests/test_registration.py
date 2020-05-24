from django.test import TestCase
from django.http import HttpRequest
from django.shortcuts import reverse
from django.contrib.auth.models import User
from ..view.usermgmt import check_recaptcha
from ..models import Profile


class RegistrationTests(TestCase):
    """
    These tests are quite poor
    todo: improve
    """

    def test_recaptcha_check_empty_request(self):
        @check_recaptcha
        def recap_test(request):
            assert request.recaptcha_is_valid is not True
        recap_test(HttpRequest())

    def test_recaptcha_check_keymismatch(self):
        @check_recaptcha
        def recap_test(request):
            assert request.recaptcha_is_valid is not True

        with self.settings(GOOGLE_RECAPTCHA_SECRET_KEY='test1'):
            recap_test(HttpRequest())

        with self.settings(GOOGLE_RECAPTCHA_PUBLIC_KEY='test2'):
            recap_test(HttpRequest())

    def test_register(self):
        """
        Todo: mock recaptcha
        """
        # test GET
        response = self.client.get(reverse('user_register'), follow=True)
        assert response.status_code == 200
        assert len(User.objects.all()) == 0
        assert len(Profile.objects.all()) == 0

        # test POST - inhibited by recaptcha
        #response = self.client.post(reverse('user_register'), follow=True)
        #assert response.status_code == 200
        #assert len(User.objects.all()) == 1
        #assert len(Profile.objects.all()) == 0

    def test_activate(self):
        pass
