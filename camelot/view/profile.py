from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from ..controllers.profilecontroller import profilecontroller
from ..controllers.utilities import PermissionException

from ..forms import EditProfileForm

def show_profile(request, userid):
    """

    :param request:
    :param userid: the id of the profile's user to show
    :return: render of specified profile
    """
    # a controller might not be the best way to handle profiles...
    # consistency is a really nice thing though...
    pcontrol = profilecontroller(request.user.id)
    try:
        data = pcontrol.return_profile_data(userid)
    except PermissionException:
        # do something relevant
        raise

    return render(request, 'camelot/profile.html', data)

@login_required
def update_profile(request):
    """
    View for update profile page
    :param request:
    :return:
    """
    profilecontrol = profilecontroller(request.user.id)

    if request.method == 'POST':
        form = EditProfileForm(request.POST)

        data = {}

        if form.is_valid():
            data['description'] = form.cleaned_data['description']

            # we may want to kwargs the following
            profilecontrol.update_profile_data(**data)
            return redirect("show_profile", request.user.id)
    else:
        form = EditProfileForm(initial={'description': profilecontrol.uprofile.description})
    return render(request, 'camelot/editprofile.html', {'form': form})

