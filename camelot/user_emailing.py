from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from .tokens import account_activation_token

# number of days for reminder and expire
REMINDER = 7
EXPIRE = 14


def send_registration_email(user, domain):
    """
    Send out registration email to user
    :param user: user object
    :param domain: the website we are sending from
    :return:
    """
    subject = 'Activate Your PicPicPanda Account'
    message = render_to_string('camelot/account_activation_email.html', {
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


def remind_stale_reg(user, msg):
    """
    Is this function necessary?
    Do we want to separate the emailing from register()? yes
    :param user: What do we want to pass here?
    :param msg:
    :return: string to be emailed to user
    """
    pass
    # email the user with the message and link


def remind_all_stale_reg():
    """

    :return: list of all usernames emailed
    """
    pass
    # query for inactive users registers past threshold
    # call remind_stale_reg() for all users in query
