from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from ..controllers.friendcontroller import friendcontroller
from ..controllers.utilities import get_profile_from_uid, AlreadyExistsException, AddSelfException

@login_required
def add_friend(request, userid):
    friendcontrol = friendcontroller(request.user.id)
    try:
        friendcontrol.add(get_profile_from_uid(userid))
    except AlreadyExistsException:
        # replace the following with something else
        return redirect("user_home") # error
    except AddSelfException:
        return render(request, "camelot/messageloggedin.html", {"message": "Silly human, you can't add yourself"})
    return redirect("add_friend_to_groups", userid)

@login_required
def confirm_friend(request, userid):
    friendcontrol = friendcontroller(request.user.id)
    # may want to check the following return value and do something
    friendcontrol.confirm(get_profile_from_uid(userid))
    return redirect("add_friend_to_groups", userid)

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

    #print(userid)

    friendplist = friendcontrol.return_friend_list(profile)

    #[print(x) for x in friendplist]

    return render(request, 'camelot/showfriends.html', {'friendlist': friendplist})

@login_required
def show_pending_friend_reqs(request):
    """

    :param request:
    :return:
    """
    friendcontrol = friendcontroller(request.user.id)
    pendingfriendships = friendcontrol.return_pending_requests()

    return render(request, 'camelot/showpending.html', {'pending': pendingfriendships})