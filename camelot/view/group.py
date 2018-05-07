from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.forms import ChoiceField, MultipleChoiceField
from django.http import Http404
from django.contrib import messages

from ..controllers.groupcontroller import groupcontroller, is_in_group, return_group_from_id
from ..controllers.friendcontroller import are_friends
from ..controllers.utilities import get_profile_from_uid, AlreadyExistsException
from ..forms import AddGroupForm, MyGroupSelectForm, ManageGroupMemberForm

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
            try:
                groupcontrol.create(newgroupname)
            except AlreadyExistsException as e:
                messages.error(request, "Group name must be unique")

    # always redirect the same regardless of request type
    return redirect("manage_groups")


@login_required
def delete_group(request):
    """
    Delete a group
    :param request: receive a post request with field idname of the group id
    :return: redirect to manage groups page
    """
    # todo: unit test
    if request.method == 'POST':
        groupcontrol = groupcontroller(request.user.id)

        form = MyGroupSelectForm(request.user.id, ChoiceField, request.POST)

        if form.is_valid():

            # list of group ids
            groupid = form.cleaned_data['idname']
            group = return_group_from_id(groupid)

            groupcontrol.delete_group(group)

    return redirect("manage_groups")

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
    View to manage an individual group
    add/remove members
    :param request:
    :param id: id of the group to manage
    :return:
    """
    groupcontrol = groupcontroller(request.user.id)
    group = return_group_from_id(id)
    retdict = {
        "group": group,
        "addform": ManageGroupMemberForm(request.user.profile, group),
        "delform": ManageGroupMemberForm(request.user.profile, group, remove=True)
    }
    return render(request, "camelot/editgroupmembers.html", retdict)


@login_required
def remove_friend_from_group(request, groupid):
    """
    Remove friends from a group from the group management page
    :param request:
    :param groupid:
    :return:
    """
    if request.method == 'POST':
        group = return_group_from_id(groupid)
        groupcontrol = groupcontroller(request.user.id)
        form = ManageGroupMemberForm(request.user.profile, group, True, request.POST)

        if form.is_valid():

            profiles = [get_profile_from_uid(int(x)) for x in form.cleaned_data['idname']]
            for profile in profiles:
                groupcontrol.delete_member(group, profile)
            return redirect("manage_group", group.id)

@login_required
def add_friend_to_group_mgmt(request, groupid):
    """
    Add friends to a group from the group management page
    :param request:
    :param groupid:
    :return:
    """
    if request.method == 'POST':
        group = return_group_from_id(groupid)
        groupcontrol = groupcontroller(request.user.id)
        form = ManageGroupMemberForm(request.user.profile, group, False, request.POST)

        if form.is_valid():

            profiles = [get_profile_from_uid(int(x)) for x in form.cleaned_data['idname']]
            for profile in profiles:
                groupcontrol.add_member(group.id, profile)
            return redirect("manage_group", group.id)

@login_required
def add_friend_to_group(request, userid):
    """
    View to add a friend to a group after creating friendship
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
            profile = get_profile_from_uid(userid)

            # list of group ids
            groups = [int(x) for x in form.cleaned_data['idname']]
            for groupid in groups:
                group = return_group_from_id(groupid)
                if is_in_group(group, profile):
                    pass
                else:
                    try:
                        # this assert may need to be handled at a higher level depending on what django does
                        assert groupcontrol.add_member(groupid, profile)
                    except Exception as e:
                        raise e

        # if we are in pending requests, we want to redirect to the pending page... hmm... :\
        return redirect("show_profile", userid)

    form = MyGroupSelectForm(request.user.id, MultipleChoiceField)

    retdict = {'uid': userid, 'form': form}
    return render(request, 'camelot/addfriendtogroup.html', retdict)
