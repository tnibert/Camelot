from django.contrib.auth.decorators import login_required

"""
Album views
"""

@login_required
def create_album(request):
    pass

@login_required
def display_albums(request):
    pass

@login_required
def display_album(request):
    pass

