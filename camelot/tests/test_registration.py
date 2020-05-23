from django.test import TestCase
from django.http import HttpRequest
from ..view.usermgmt import check_recaptcha, register


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
        assert register(HttpRequest()).status_code == 200
