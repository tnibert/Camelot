from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .constants import *
from .models import FriendGroup
from .controllers.groupcontroller import groupcontroller
from .controllers.friendcontroller import friendcontroller

class SignUpForm(UserCreationForm):
    email = forms.EmailField(help_text='Required')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', )

class AlbumCreateForm(forms.Form):
    albumname = forms.CharField(label='Photo album name', max_length=70)
    description = forms.CharField(label='Photo album description', max_length=300)

class UploadPhotoForm(forms.Form):
    #file = forms.ImageField()        # read django security doc regarding this
                                    # https://docs.djangoproject.com/en/2.0/topics/security/#user-uploaded-content-security
    #description = forms.CharField(max_length=MAXPHOTODESC)
    extra_field_count = forms.CharField(widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        print("In Form Init")
        self.extra_fields = int(kwargs.pop('extra', 0))

        super(UploadPhotoForm, self).__init__(*args, **kwargs)
        self.fields['extra_field_count'].initial = self.extra_fields

        self.fields['file_0'] = forms.ImageField()
        self.fields['desc_0'] = forms.CharField(max_length=MAXPHOTODESC)

        # this loop should only be entered after a post with extra fields
        for index in range(int(self.extra_fields)):
            print("In form for loop index " + str(index))
            # generate extra fields in the number specified via extra_fields
            self.fields['file_{index}'.format(index=index+1)] = \
                forms.ImageField()
            self.fields['desc_{index}'.format(index=index+1)] = \
                forms.CharField(max_length=MAXPHOTODESC)

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

class EditAlbumAccesstypeForm(forms.Form):
    """
    Form to edit album access type
    """
    mytype = forms.ChoiceField(label="Access Types", choices=ACCESSTYPES.items())

class AddContributorForm(forms.Form):

    def __init__(self, myuid, album, *args, **kwargs):
        """
        Form populated by the current user's groups
        :param myuid: current user's id
        :param choicefieldtype: Type of field to instantiate.  Valid types are forms.ChoiceField and forms.MultipleChoiceField.
        :param args:
        :param kwargs:
        """
        super(AddContributorForm, self).__init__(*args, **kwargs)
        control = friendcontroller(myuid)
        ch = lambda: [(x.id, x.user.username) for x in control.return_friend_list(control.uprofile) if x not in album.contributors.all()]
        self.fields['idname'] = forms.MultipleChoiceField(
            label='New Contributor', choices=ch)
