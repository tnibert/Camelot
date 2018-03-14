from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from ..controllers.profilecontroller import profilecontroller
from ..controllers.utilities import PermissionException

@login_required
def show_profile(request, userid):
    """

    :param request:
    :param userid: the id of the profile's user to show
    :return: render of specified profile
    """
    # a controller might not be the best way to handle profiles...
    # consistency is a really nice thing though...
    pcontrol = profilecontroller()
    try:
        data = pcontrol.return_profile_data(userid)
    except PermissionException:
        # do something relevant
        raise

    return render(request, 'camelot/profile.html', data)

def update_profile(request):
    """

    :param request:
    :return:
    """
    # create an update profile form
    pass
