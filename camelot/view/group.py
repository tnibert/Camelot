from django.contrib.auth.decorators import login_required

@login_required()
def create_group():
    pass

@login_required()
def delete_group():
    pass