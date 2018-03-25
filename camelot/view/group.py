from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from ..controllers.groupcontroller import groupcontroller
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
    deleteform = MyGroupSelectForm(request.user.id)

    retdict = {'groups': groups, 'addform': addform, 'delform': deleteform}        # how will this translate to a json view?  Test in browser
    return render(request, 'camelot/managegroups.html', retdict)