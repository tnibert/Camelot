from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .constants import *
from .models import FriendGroup
from .controllers.groupcontroller import groupcontroller

class SignUpForm(UserCreationForm):
    email = forms.EmailField(help_text='Required')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', )

class AlbumCreateForm(forms.Form):
    albumname = forms.CharField(label='Photo album name', max_length=70)
    description = forms.CharField(label='Photo album description', max_length=300)

class UploadPhotoForm(forms.Form):
    description = forms.CharField(max_length=150)
    file = forms.ImageField()        # read django security doc regarding this
                                    # https://docs.djangoproject.com/en/2.0/topics/security/#user-uploaded-content-security

class EditProfileForm(forms.Form):
    # need to have existing description filled in by default on form display
    description = forms.CharField(label='Description', max_length=300,
                                  # the following might be best done in css
                                  widget=forms.Textarea(attrs={'cols': 50, 'rows': 6}))

class ManageGroupsForm(forms.Form):
    """
    So requirements:
    - must be able to add users to a group
    - must be able to delete users from a group
    - must be able to add a group
    - must be able to delete a group
    This may be best done in multiple forms

    Workflow will be:
    Add friend -> specify groups -> confirm friend -> specify groups
    or
    Home -> manage groups
    Perhaps it would be best to define the groups in terms of the friend, e.g. you go
    to a friend and you edit their group permissions from there
    ... yes, I think that is simpler
    In that case manage groups only needs to add or delete groups
    """
    pass

class AddGroupForm(forms.Form):
    """
    Form to add a group
    """
    name = forms.CharField(label='Group Name', max_length=GROUPNAMELEN)

class FriendGroupingForm(forms.Form):
    """
    List groups in a scroll box that allows selecting of multiple entries
    """
    pass

class MyGroupSelectForm(forms.Form):

    def __init__(self, myuid, choicefieldtype, *args, **kwargs):
        """
        Form populated by the current user's groups
        :param myuid: current user's id
        :param choicefieldtype: Type of field to instantiate.  Valid types are forms.ChoiceField and forms.MultipleChoiceField.
        :param args:
        :param kwargs:
        """
        super(MyGroupSelectForm, self).__init__(*args, **kwargs)
        control = groupcontroller(myuid)
        ch = lambda: [(x.id, x.name) for x in control.return_groups()]
        self.fields['idname'] = choicefieldtype(
            label='Group Name', choices=ch)
