from django.contrib.auth.decorators import login_required

@login_required()
def add_friend():
    pass

@login_required()
def confirm_friend():
    pass

@login_required()
def delete_friend():
    pass