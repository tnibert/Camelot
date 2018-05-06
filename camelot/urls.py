from django.urls import path
from django.conf.urls import url
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.auth import views as auth_views
from .view import album, usermgmt, profile, friend, group

urlpatterns = [
    path('', usermgmt.index, name='index'),
    path('logout', usermgmt.user_logout, name='logout'),
    path('home', usermgmt.user_home, name='user_home'),         # lets move this one to another file
    path('register', usermgmt.register, name='user_register'),
    url('^account_activation_sent/$', usermgmt.account_activation_sent, name='account_activation_sent'),
    url('^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        usermgmt.activate, name='activate'),
    path('createalbum', album.create_album, name="create_album"),
    url(r'^profile/(?P<userid>\d+)/albums$', album.display_albums, name="show_albums"),
    url(r'^album/(?P<id>\d+)/$', album.display_album, name="show_album"),
    url(r'^album/(?P<id>\d+)/(?P<contribid>\d+)$', album.display_album, name="show_album"),
    url(r'^album/(?P<id>\d+)/upload_photos/$', album.add_photo, name="upload_photos"),
    url(r'^photo/(?P<photoid>\d+)/$', album.return_photo_file_http, name="show_photo"),
    url(r'^profile/(?P<userid>\d+)/$', profile.show_profile, name="show_profile"),
    url(r'^profile/(?P<userid>\d+)/friends$', friend.view_friend_list, name="show_friends"),
    url(r'^profile/(?P<userid>\d+)/add_friend$', friend.add_friend, name="add_friend"),
    url(r'^profile/(?P<userid>\d+)/confirm$', friend.confirm_friend, name="confirm_friend"),
    url(r'^profile/(?P<userid>\d+)/remove', friend.delete_friend, name="remove_friend"),
    path('pending_requests', friend.show_pending_friend_reqs, name="show_pending_requests"),
    path('update_profile', profile.update_profile, name='update_profile'),
    path('manage_groups', group.manage_groups, name='manage_groups'),
    path('create_group', group.create_group, name='create_group'),
    url(r'^add_friend_to_groups/(?P<userid>\d+)/$', group.add_friend_to_group, name="add_friend_to_groups"),
    url(r'^album/(?P<albumid>\d+)/manage$', album.manage_album_permissions, name="manage_album"),
    url(r'^album/(?P<id>\d+)/update_access_type$', album.update_access_type, name="update_album_access"),
    url(r'^album/(?P<albumid>\d+)/add_groups$', album.add_groups, name="add_album_groups"),
    url(r'^album/(?P<albumid>\d+)/add_contributor$', album.add_contrib, name="add_album_contrib"),
    url(r'^album/(?P<photoid>\d+)/show_photo$', album.display_photo, name="present_photo"),
    url(r'^profile/(?P<userid>\d+)/profilepic$', profile.return_raw_profile_pic, name="profile_pic"),
    url(r'^profile/photo/(?P<photoid>\d+)/set_profilepic$', profile.make_profile_pic, name="set_profile_pic"),
    url(r'^photo/(?P<photoid>\d+)/delete$', album.delete_photo, name="delete_photo"),
    url(r'^album/(?P<albumid>\d+)/delete$', album.delete_album, name="delete_album"),
    url(r'^group/delete$', group.delete_group, name="delete_group"),
    path('search', friend.search, name="search"),
    url(r'^group/(?P<id>\d+)/manage$', group.manage_group, name="manage_group"),
    url(r'^group/(?P<groupid>\d+)/rmmember$', group.remove_friend_from_group, name="group_friend_remove"),
    url(r'^group/(?P<groupid>\d+)/addmember$', group.add_friend_to_group_mgmt, name="group_friend_add"),
    url(r'^password_reset/$', auth_views.password_reset, name='password_reset'),
    url(r'^password_reset/done/$', auth_views.password_reset_done, name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_views.password_reset_confirm, name='password_reset_confirm'),
    url(r'^reset/done/$', auth_views.password_reset_complete, name='password_reset_complete'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)