from django.urls import path, re_path
from .constants import REGISTER_DISABLED, REGISTER_EMAIL, REGISTER_CODE
from .view import usermgmt

REGISTRATION_URLS = {
    REGISTER_DISABLED: [],
    REGISTER_CODE: [
        path('register', usermgmt.register_invite_code, name='user_register')
    ],
    REGISTER_EMAIL: [
        path('register', usermgmt.register, name='user_register'),
        re_path('^account_activation_sent/$', usermgmt.account_activation_sent, name='account_activation_sent'),
        re_path('^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
            usermgmt.activate, name='activate')
    ]
}
