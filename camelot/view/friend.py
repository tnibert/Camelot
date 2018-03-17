from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from ..controllers.friendcontroller import friendcontroller
from ..controllers.utilities import get_profile_from_uid

@login_required()
def add_friend(request):
    pass

@login_required()
def confirm_friend(request):
    pass

@login_required
def delete_friend(request):
    pass

@login_required
def view_friend_list(request, userid):
    """

    :param request: http request
    :param profileid: profile to return friendlist of
    :return:
    """
    friendcontrol = friendcontroller(request.user.id)
    profile = get_profile_from_uid(userid)
    friendlist = friendcontrol.return_friend_list(profile)
    return render(request, 'camelot/showfriends.html', {'friendlist': friendlist})