from django.test import TestCase
from django.core import mail
from django.shortcuts import reverse
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from ..models import Profile
from ..user_emailing import remind_stale_reg, send_registration_email
from ..forms import SignUpForm
from ..view.usermgmt import activate_user_no_check


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
        # this could be parameterized...

        # test GET
        response = self.client.get(reverse('user_register'))
        assert response.status_code == 200
        assert len(User.objects.all()) == 0
        assert len(Profile.objects.all()) == 0

        # test POST
        with self.settings(DEBUG=True):
            response = self.client.post(reverse('user_register'), self.regdata)
        assert response.status_code == 302
        assert len(User.objects.all()) == 1
        assert len(Profile.objects.all()) == 0
        # outbox can be cleared with mail.outbox = []
        self.assertEqual(len(mail.outbox), 1)

        # test reregister with same email address, inactive user
        # registration email will be resent
        sameemailregdata = self.regdata.copy()
        sameemailregdata['username'] = 'test2'

        errormessages = {
            "email": "Email address unavailable, please check your email",  # if reminder sent
            "no_email": "Email address not available",                      # if no reminder sent
            "username": "A user with that username already exists.",        # if username error caught in django default
            "username_case": "Username already exists",                     # if username error caught in custom validator
            "email_err": "Error sending confirmation email, please try again"
        }

        with self.settings(DEBUG=True):
            response = self.client.post(reverse('user_register'), sameemailregdata)
        assert errormessages["email"] in response.content.decode()
        assert errormessages["username"] not in response.content.decode()
        assert errormessages["no_email"] not in response.content.decode()
        self.assertEqual(len(mail.outbox), 2)
        assert response.status_code == 200
        assert len(User.objects.all()) == 1
        assert len(Profile.objects.all()) == 0

        # test reregister with same username, inactive user
        sameusernameregdata = self.regdata.copy()
        sameusernameregdata['email'] = 'different@different.com'

        with self.settings(DEBUG=True):
            response = self.client.post(reverse('user_register'), sameusernameregdata)
        assert errormessages["username_case"] in response.content.decode()
        assert errormessages["username"] not in response.content.decode()
        assert errormessages["email"] not in response.content.decode()
        assert errormessages["no_email"] not in response.content.decode()
        self.assertEqual(len(mail.outbox), 2)
        assert response.status_code == 200
        assert len(User.objects.all()) == 1
        assert len(Profile.objects.all()) == 0

        # test reregister with same username, different case, inactive user
        sameusernamediffcaseregdata = sameusernameregdata.copy()
        sameusernamediffcaseregdata['username'] = sameusernamediffcaseregdata['username'].upper()

        with self.settings(DEBUG=True):
            response = self.client.post(reverse('user_register'), sameusernamediffcaseregdata)
        assert response.status_code == 200
        assert errormessages["username_case"] in response.content.decode()
        assert errormessages["username"] not in response.content.decode()
        assert errormessages["email"] not in response.content.decode()
        assert errormessages["no_email"] not in response.content.decode()
        self.assertEqual(len(mail.outbox), 2)
        assert len(User.objects.all()) == 1
        assert len(Profile.objects.all()) == 0

        # test reregister with both duplicate, inactive user
        with self.settings(DEBUG=True):
            response = self.client.post(reverse('user_register'), self.regdata)
        assert response.status_code == 200
        assert errormessages["username_case"] in response.content.decode()
        assert errormessages["username"] not in response.content.decode()
        assert errormessages["email"] in response.content.decode()
        assert errormessages["no_email"] not in response.content.decode()
        assert len(User.objects.all()) == 1
        assert len(Profile.objects.all()) == 0
        self.assertEqual(len(mail.outbox), 3)

        # activate the user
        user = User.objects.get(email=self.regdata['email'], username=self.regdata['username'])
        activate_user_no_check(user)

        # test reregister with same email address, active user
        # registration email will not be resent
        with self.settings(DEBUG=True):
            response = self.client.post(reverse('user_register'), sameemailregdata)
        self.assertEqual(len(mail.outbox), 3)
        assert response.status_code == 200
        assert errormessages["username"] not in response.content.decode()
        assert errormessages["email"] not in response.content.decode()
        assert errormessages["no_email"] in response.content.decode()
        assert len(User.objects.all()) == 1
        assert len(Profile.objects.all()) == 1
        assert isinstance(user.profile, Profile)

        # test reregister with same username, active user
        with self.settings(DEBUG=True):
            response = self.client.post(reverse('user_register'), sameusernameregdata)
        self.assertEqual(len(mail.outbox), 3)
        assert response.status_code == 200
        assert errormessages["username_case"] in response.content.decode()
        assert errormessages["username"] not in response.content.decode()
        assert errormessages["email"] not in response.content.decode()
        assert errormessages["no_email"] not in response.content.decode()
        assert len(User.objects.all()) == 1
        assert len(Profile.objects.all()) == 1
        assert isinstance(user.profile, Profile)

        # test reregister with both duplicate, active user
        with self.settings(DEBUG=True):
            response = self.client.post(reverse('user_register'), self.regdata)
        self.assertEqual(len(mail.outbox), 3)
        assert response.status_code == 200
        assert errormessages["username_case"] in response.content.decode()
        assert errormessages["username"] not in response.content.decode()
        assert errormessages["email"] not in response.content.decode()
        assert errormessages["no_email"] in response.content.decode()
        assert len(User.objects.all()) == 1
        assert len(Profile.objects.all()) == 1
        assert isinstance(user.profile, Profile)

        # todo: test failure to send mail in POST, mock exception from send_registration_email()

    def test_send_registration_email(self):
        testuser = SignUpForm(data=self.regdata).save(commit=False)
        testuser.is_active = False
        testuser.save()

        # tests run with setting EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend'
        send_registration_email(testuser, "picpicpanda.com")
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Activate Your PicPicPanda Account')
        #print(mail.outbox[0].body)

    def test_activate_endpoint(self):
        # register user
        with self.settings(DEBUG=True):
            response = self.client.post(reverse('user_register'), self.regdata)
        assert response.status_code == 302

        assert len(User.objects.all()) == 1
        assert len(Profile.objects.all()) == 0

        # get activation url
        assert len(mail.outbox) == 1
        activate_url = mail.outbox[0].body.split("\n")[7].split("/")
        activate_url[2] = "127.0.0.1"
        activate_url = "/".join(activate_url)

        # activate the user
        response = self.client.post(activate_url, follow=True)
        assert response.status_code == 200

        assert len(User.objects.all()) == 1
        assert len(Profile.objects.all()) == 1

    def test_activate_user_no_check(self):
        with self.settings(DEBUG=True):
            response = self.client.post(reverse('user_register'), self.regdata)

        assert len(User.objects.all()) == 1
        assert len(Profile.objects.all()) == 0

        user = User.objects.get(email=self.regdata['email'], username=self.regdata['username'])
        with self.assertRaises(Profile.DoesNotExist):
            user.profile
        assert user.is_active is False

        activate_user_no_check(user)
        user.refresh_from_db()
        assert user.is_active is True
        assert len(User.objects.all()) == 1
        assert len(Profile.objects.all()) == 1
        assert isinstance(user.profile, Profile)
        assert user.profile.email_confirmed is True


class ReminderTests(TestCase):
    def setUp(self):
        remind_date = datetime.now() - timedelta(days=8)
        expire_date = datetime.now() - timedelta(days=15)

        # create users
        self.remind1 = User.objects.create_user(**{'username': 'to_remind',
                                                 'email': 'user@test.com',
                                                 'password': 'secret',
                                                 'is_active': False,
                                                 'date_joined': remind_date})
        self.remind1.save()

        self.expire1 = User.objects.create_user(**{'username': 'to expire',
                                                 'email': 'user2@test.com',
                                                 'password': 'secret',
                                                 'is_active': False,
                                                 'date_joined': expire_date})
        self.expire1.save()

        self.noaction1 = User.objects.create_user(**{'username': 'no dramas',
                                                   'email': 'user3@test.com',
                                                   'password': 'secret',
                                                   'is_active': False,
                                                   'date_joined': datetime.now()})
        self.noaction1.save()

        self.users = [self.remind1, self.expire1, self.noaction1]

    def test_remind_stale_reg(self):
        remind_stale_reg(self.users, 'camelot/account_activation_reminder.html')
        self.assertEqual(len(mail.outbox), 3)
