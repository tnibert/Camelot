from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from ..controllers import groupcontroller

"""
Let's try to make this a bit more... restful?
We will create dicts and pass those to render for get requests
This will make it easier to implement json views later
"""

@login_required
def create_group(request):
    pass

@login_required
def delete_group(request):
    pass

@login_required
def manage_groups(request):
    """
    This needs to only be accessible to the current user for themselves
    :param request:
    :return:
    """
    groupcontrol = groupcontroller(request.user.id)
    groups = groupcontrol.return_groups()

    retdict = {'groups': groups}        # how will this translate to a json view?  Test in browser
    return render(request, 'camelot/manage_groups.html', retdict)