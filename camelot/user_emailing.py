from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from .tokens import account_activation_token
from .constants2 import SITEDOMAIN


def send_registration_email(user, domain, htmlfile='camelot/account_activation_email.html'):
    """
    Send out registration email to user
    :param user: user object
    :param domain: the website we are sending from
    :param htmlfile: filename of the html file to format for registration
    :return:
    """
    subject = 'Activate Your PicPicPanda Account'
    message = render_to_string(htmlfile, {
        'user': user,
        'domain': domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode(),
        'token': account_activation_token.make_token(user),
    })

    user.email_user(subject, message)

    # the following will work as well:
    #from django.core.mail import send_mail
    #send_mail(
    #    subject,
    #    message,
    #    "no-reply@picpicpanda.com",
    #    [user.email],
    #    fail_silently=False,
    #)


def remind_stale_reg(users, htmltemplate):
    """
    Email registration reminders to a list of users
    This is intended to be invoked separately to the app
    :param users: list of User objects
    :param htmltemplate: string of the template filename to use for the email body
    :return: string to be emailed to user
    """
    for user in users:
        send_registration_email(user, SITEDOMAIN, htmlfile=htmltemplate)


def remind_stale_email_list(usernames, htmltemplate):
    """
    send reminder for email registration to a list of email addresses plain text
    :param usernames: list of usernames to send email to
    :return:
    """
    users = []
    for name in usernames:
        try:
            u = User.objects.get(username=name)
        except ObjectDoesNotExist:
            print("User not in db: {}".format(name))
            continue

        if u.is_active is False:
            users.append(u)
        else:
            print("Account is active: {}".format(name))

    remind_stale_reg(users, htmltemplate)
