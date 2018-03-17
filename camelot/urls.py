from django.urls import path
from django.conf.urls import url
from .view import album, usermgmt, profile

urlpatterns = [
    path('', usermgmt.index, name='index'),
    path('logout', usermgmt.user_logout, name='logout'),
    path('home', usermgmt.user_home, name='user_home'),         # lets move this one to another file
    path('register', usermgmt.register, name='user_register'),
    url('^account_activation_sent/$', usermgmt.account_activation_sent, name='account_activation_sent'),
    url('^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        usermgmt.activate, name='activate'),
    path('createalbum', album.create_album, name="create_album"),
    path('albums', album.display_albums, name="show_albums"),
    url(r'^album/(?P<id>\d+)/$', album.display_album, name="show_album"),
    url(r'^album/(?P<id>\d+)/upload_photos/$', album.add_photo, name="upload_photos"),
    url(r'^photo/(?P<photoid>\d+)/$', album.return_photo_file_http, name="show_photo"),
    url(r'^profile/(?P<userid>\d+)/$', profile.show_profile, name="show_profile"),
]
