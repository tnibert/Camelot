from django.test import TestCase
from django.core import mail
from django.shortcuts import reverse
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from ..models import Profile
from ..user_emailing import REMINDER, EXPIRE, remind_stale_reg, remind_all_stale_reg, send_registration_email
from ..forms import SignUpForm


class RegistrationTests(TestCase):
    """
    These tests are quite poor
    todo: improve
    """

    def setUp(self):
        self.regdata = {'username': 'test1',
                        'email': 'user4@test.com',
                        'password1': 'blahblah123',
                        'password2': 'blahblah123'}

    def test_register(self):
        # test GET
        response = self.client.get(reverse('user_register'), follow=True)
        assert response.status_code == 200
        assert len(User.objects.all()) == 0
        assert len(Profile.objects.all()) == 0

        # test POST
        with self.settings(DEBUG=True):
            response = self.client.post(reverse('user_register'), self.regdata, follow=True)
        assert response.status_code == 200
        assert len(User.objects.all()) == 1
        assert len(Profile.objects.all()) == 0
        # outbox can be cleared with mail.outbox = []
        self.assertEqual(len(mail.outbox), 1)

        # test reregister with same email address
        with self.settings(DEBUG=True):
            response = self.client.post(reverse('user_register'), self.regdata, follow=True)
            self.assertEqual(len(mail.outbox), 2)
        assert response.status_code == 200
        assert len(User.objects.all()) == 1
        assert len(Profile.objects.all()) == 0

        # todo: test failure to send mail in POST

    def test_send_registration_email(self):
        testuser = SignUpForm(data=self.regdata).save(commit=False)
        testuser.is_active = False
        testuser.save()

        # tests run with setting EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend'
        send_registration_email(testuser, "picpicpanda.com")
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Activate Your PicPicPanda Account')
        #print(mail.outbox[0].body)

    def test_activate(self):
        pass


class ExpirationTests(TestCase):
    def setUp(self):
        remind_date = datetime.now() - timedelta(days=REMINDER + 1)
        expire_date = datetime.now() - timedelta(days=EXPIRE + 1)

        # create users
        self.remind1 = User.objects.create_user({'username': 'to_remind',
                                                 'email': 'user@test.com',
                                                 'password': 'secret',
                                                 'is_active': False,
                                                 'date_joined': remind_date})
        self.remind1.save()

        self.expire1 = User.objects.create_user({'username': 'to expire',
                                                 'email': 'user2@test.com',
                                                 'password': 'secret',
                                                 'is_active': False,
                                                 'date_joined': expire_date})
        self.expire1.save()

        self.noaction1 = User.objects.create_user({'username': 'no dramas',
                                                   'email': 'user3@test.com',
                                                   'password': 'secret',
                                                   'is_active': False,
                                                   'date_joined': datetime.now()})
        self.noaction1.save()

    def test_remind_stale_reg(self):
        #remind_stale_reg()
        pass

    def test_remind_all_stale_reg(self):
        pass


