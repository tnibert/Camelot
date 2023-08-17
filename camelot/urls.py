from django.urls import path, re_path
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.auth import views as auth_views
from .view import album, usermgmt, profile, friend, group
from .view.api import albumapi

urlpatterns = [
    path('', usermgmt.index, name='index'),
    path('logout', usermgmt.user_logout, name='logout'),
    path('home', usermgmt.user_home, name='user_home'),         # lets move this one to another file
    #path('register', usermgmt.register, name='user_register'),
    #url('^account_activation_sent/$', usermgmt.account_activation_sent, name='account_activation_sent'),
    #url('^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
    #    usermgmt.activate, name='activate'),
    path('createalbum', album.create_album, name="create_album"),
    re_path(r'^profile/(?P<userid>\d+)/albums$', album.display_albums, name="show_albums"),
    re_path(r'^album/(?P<id>\d+)/$', album.display_album, name="show_album"),
    re_path(r'^album/(?P<id>\d+)/(?P<contribid>\d+)$', album.display_album, name="show_album"),
    re_path(r'^album/(?P<id>\d+)/upload_photos/$', album.add_photo, name="upload_photos"),
    re_path(r'^photo/(?P<photoid>\d+)/$', album.return_photo_file_http, name="show_photo"),
    re_path(r'^photo/(?P<photoid>\d+)/thumb/$', album.return_photo_file_http, {'thumb': True}, name="show_thumb"),
    re_path(r'^photo/(?P<photoid>\d+)/fullsize/$', album.return_photo_file_http, {'mid': False}, name="show_photo_full"),
    re_path(r'^profile/(?P<userid>\d+)/$', profile.show_profile, name="show_profile"),
    re_path(r'^space/(?P<username>[\w\-]+)/$', profile.show_profile_by_name, name="show_profile_name"),
    re_path(r'^profile/(?P<userid>\d+)/friends$', friend.view_friend_list, name="show_friends"),
    re_path(r'^profile/(?P<userid>\d+)/add_friend$', friend.add_friend, name="add_friend"),
    re_path(r'^profile/(?P<userid>\d+)/confirm$', friend.confirm_friend, name="confirm_friend"),
    re_path(r'^profile/(?P<userid>\d+)/remove', friend.delete_friend, name="remove_friend"),
    path('pending_requests', friend.show_pending_friend_reqs, name="show_pending_requests"),
    path('update_profile', profile.update_profile, name='update_profile'),
    path('manage_groups', group.manage_groups, name='manage_groups'),
    path('create_group', group.create_group, name='create_group'),
    re_path(r'^add_friend_to_groups/(?P<userid>\d+)/$', group.add_friend_to_group, name="add_friend_to_groups"),
    re_path(r'^album/(?P<albumid>\d+)/manage$', album.manage_album_permissions, name="manage_album"),
    re_path(r'^album/(?P<id>\d+)/update_access_type$', album.update_access_type, name="update_album_access"),
    re_path(r'^album/(?P<albumid>\d+)/add_groups$', album.add_groups, name="add_album_groups"),
    re_path(r'^album/(?P<albumid>\d+)/add_contributor$', album.add_contrib, name="add_album_contrib"),
    re_path(r'^album/(?P<photoid>\d+)/show_photo$', album.display_photo, name="present_photo"),
    re_path(r'^profile/(?P<userid>\d+)/profilepic$', profile.return_raw_profile_pic, name="profile_pic"),
    re_path(r'^profile/photo/(?P<photoid>\d+)/set_profilepic$', profile.make_profile_pic, name="set_profile_pic"),
    re_path(r'^photo/(?P<photoid>\d+)/delete$', album.delete_photo, name="delete_photo"),
    re_path(r'^album/(?P<albumid>\d+)/delete$', album.delete_album, name="delete_album"),
    re_path(r'^group/delete$', group.delete_group, name="delete_group"),
    path('search', friend.search, name="search"),
    re_path(r'^group/(?P<id>\d+)/manage$', group.manage_group, name="manage_group"),
    re_path(r'^group/(?P<groupid>\d+)/rmmember$', group.remove_friend_from_group, name="group_friend_remove"),
    re_path(r'^group/(?P<groupid>\d+)/addmember$', group.add_friend_to_group_mgmt, name="group_friend_add"),
    re_path(r'^password_reset/$', auth_views.PasswordResetView.as_view(), name='password_reset'),
    re_path(r'^password_reset/done/$', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    re_path(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
            auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    re_path(r'^reset/done/$', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    # the following are api end points
    re_path(r'^api/upload/(?P<id>\d+)$', albumapi.upload_photo, name='uploadphotoapi'),
    re_path(r'^api/update/photo/desc/(?P<photoid>\d+)$', albumapi.update_photo_description, name='updatephotodescapi'),
    re_path(r'^api/(?P<userid>\d+)/getalbums$', album.display_albums, {'api': True}, name="getalbumsapi"),
    re_path(r'^api/album/(?P<id>\d+)/getphotos$', album.display_album, {'api': True}, name="getphotosapi"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)