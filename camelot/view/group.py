from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.forms import ChoiceField, MultipleChoiceField
from django.http import Http404

from ..controllers.groupcontroller import groupcontroller
from ..controllers.friendcontroller import are_friends
from ..controllers.utilities import get_profile_from_uid
from ..forms import AddGroupForm, MyGroupSelectForm

"""
Let's try to make this a bit more... restful?  Whatever that really means
We will create dicts and pass those to render for get requests
This will make it easier to implement json views later
"""

@login_required
def create_group(request):
    """
    Will only receive post, create a group, redirect to manage_groups page
    :param request:
    :return: redirect to manage_groups
    """
    # only take post for doing anything
    if request.method == 'POST':
        groupcontrol = groupcontroller(request.user.id)

        form = AddGroupForm(request.POST)

        if form.is_valid():
            newgroupname = form.cleaned_data['name']
            # we can't have an empty newgroupname
            # todo: add as not null database constraint
            if len(newgroupname) == 0:
                # todo: pass in error, need to implement db constraint to take care of this
                return redirect("manage_groups")
            groupcontrol.create(newgroupname)

    # always redirect the same regardless of request type
    return redirect("manage_groups")

@login_required
def delete_group(request):
    pass

@login_required
def manage_groups(request):
    """
    This needs to only be accessible to the current user for themselves
    :param request: only get
    :return: render manage_groups page
    """
    groupcontrol = groupcontroller(request.user.id)
    groups = groupcontrol.return_groups()
    addform = AddGroupForm()        # how would I render a django form in a java android app?
    deleteform = MyGroupSelectForm(request.user.id, ChoiceField)

    retdict = {'groups': groups, 'addform': addform, 'delform': deleteform}        # how will this translate to a json view?  Test in browser
    return render(request, 'camelot/managegroups.html', retdict)

@login_required
def manage_group(request, id):
    """
    View to manage an inidividual group
    :param request:
    :param id: id of the group to manage
    :return:
    """

@login_required
def add_friend_to_group(request, userid):
    """
    View to add a friend to a group
    Need to check if a friendship exists before allowing access
    :param request:
    :param userid: user id of the friend to add to groups
    :return:
    """
    # check that the users are at least pending friends before rendering
    if not (are_friends(get_profile_from_uid(request.user.id), get_profile_from_uid(userid), confirmed=True) \
            or are_friends(get_profile_from_uid(request.user.id), get_profile_from_uid(userid), confirmed=False)):
        raise Http404

    if request.method == 'POST':
        groupcontrol = groupcontroller(request.user.id)

        form = MyGroupSelectForm(request.user.id, MultipleChoiceField, request.POST)

        if form.is_valid():
            # list of group ids
            groups = form.cleaned_data['idname']
            for groupid in groups:
                try:
                    # this assert may need to be handled at a higher level depending on what django does
                    assert groupcontrol.add_member(int(groupid), get_profile_from_uid(userid))
                except Exception as e:
                    raise e

        # if we are in pending requests, we want to redirect to the pending page... hmm... :\
        return redirect("show_profile", userid)

    form = MyGroupSelectForm(request.user.id, MultipleChoiceField)

    retdict = {'uid': userid, 'form': form}
    return render(request, 'camelot/addfriendtogroup.html', retdict)
