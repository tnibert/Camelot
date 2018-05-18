from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import HttpResponse
from ..controllers.profilecontroller import profilecontroller
from ..controllers.utilities import PermissionException, get_profile_from_uid

from ..forms import EditProfileForm
from ..constants import PREFIX

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
def make_profile_pic(request, photoid):
    # todo: currently, if we delete friendship or remove contrib or whatnot, profile pic will stay
    # this must be corrected
    # for now we will have this be a GET,
    # but that is not best practice and maybe should be reconsidered later
    pcontrol = profilecontroller(request.user.id)
    if pcontrol.set_profile_pic(photoid):
        return redirect("present_photo", photoid)  # to photo viewer page
    else:
        raise PermissionException


def return_raw_profile_pic(request, userid):
    """
    Allows profile picture to be displayed publicly
    :param request:
    :param userid: user to display profile picture of
    :return: http response of raw image data
    """
    # todo: add unit test
    photo = get_profile_from_uid(userid).profile_pic
    if photo:
        fname = photo.thumb
    else:
        fname = PREFIX + "userphotos/defaultprofile.png"

    with open(fname, "rb") as f:
        return HttpResponse(f.read(), content_type="image/*")


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
            data['displayname'] = form.cleaned_data['displayname']
            data['description'] = form.cleaned_data['description']

            # we may want to kwargs the following
            profilecontrol.update_profile_data(**data)
            return redirect("show_profile", request.user.id)
    else:
        form = EditProfileForm(initial={'description': profilecontrol.uprofile.description})
    return render(request, 'camelot/editprofile.html', {'form': form})

