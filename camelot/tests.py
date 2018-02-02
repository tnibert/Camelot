from django.test import TestCase
from django.contrib.auth.models import User

class LoginTests(TestCase):
    # well this is broken af        
    def setUp(self):
        self.credentials = {
            'username': 'testuser',
            'email': 'user@test.com',
            'password': 'secret'}
        u = User.objects.create_user(**self.credentials)
        u.save()
        
    def test_login(self):
        # send login data
        response = self.client.post('', self.credentials, follow=True)
        # should be logged in now
        self.assertTrue(response.context['user'].is_authenticated)

    def test_logout(self):
        pass

    def test_invalid_login(self):
        pass
