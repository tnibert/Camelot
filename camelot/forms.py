from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.template.defaultfilters import filesizeformat

from .constants import *
from .models import FriendGroup
from .controllers.groupcontroller import groupcontroller
from .controllers.friendcontroller import friendcontroller


# https://docs.djangoproject.com/en/dev/ref/validators/
def validate_email(value):
    """
    Validate that email address of newly created user is not already registered
    :param value:
    :return:
    """
    try:
        email = User.objects.get(email=value)
    except User.DoesNotExist:
        # if a user doesn't exist with the email, we pass
        return
    # if a user does exist with the email, raise
    raise ValidationError("Email address already registered")


class SignUpForm(UserCreationForm):
    email = forms.EmailField(help_text='Required', validators=[validate_email])

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', )


class AlbumCreateForm(forms.Form):
    albumname = forms.CharField(label='Photo album name', max_length=70)
    description = forms.CharField(label='Photo album description', max_length=300, required=False)

def validate_image(value):
    if value._size > MAX_UPLOAD_SIZE:
        raise ValidationError("Please keep file size under {}. Current file size {}".format(filesizeformat(str(MAX_UPLOAD_SIZE)), filesizeformat(value._size)))


class UploadPhotoForm(forms.Form):
    # todo: read django security doc regarding this
    # https://docs.djangoproject.com/en/2.0/topics/security/#user-uploaded-content-security
    extra_field_count = forms.CharField(widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        #print("In Form Init")
        self.extra_fields = int(kwargs.pop('extra', 0))

        super(UploadPhotoForm, self).__init__(*args, **kwargs)
        self.fields['extra_field_count'].initial = self.extra_fields

        self.fields['file_0'] = forms.ImageField(validators=[validate_image])
        self.fields['desc_0'] = forms.CharField(max_length=MAXPHOTODESC, required=False)
        self.fields['file_0'].label = "File"
        self.fields['desc_0'].label = "Description"

        # this loop should only be entered after a post with extra fields
        for index in range(int(self.extra_fields)):
            #print("In form for loop index " + str(index))
            # generate extra fields in the number specified via extra_fields
            # we can use label variable here
            self.fields['file_{index}'.format(index=index+1)] = \
                forms.ImageField(label="File", validators=[validate_image])
            self.fields['desc_{index}'.format(index=index+1)] = \
                forms.CharField(label="Description", max_length=MAXPHOTODESC, required=False)


class EditProfileForm(forms.Form):
    # need to have existing fields filled in by default on form display
    displayname = forms.CharField(label='Display Name', max_length=MAXDISPLAYNAME)
    description = forms.CharField(label='Description', max_length=300,
                                  # the following might be best done in css
                                  widget=forms.Textarea(attrs={'cols': 50, 'rows': 6}))


class SearchForm(forms.Form):
    searchtext = forms.CharField(label='Friend Search', max_length=MAXDISPLAYNAME)


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
        # todo: change this to str(x) rather than x.user.username, look for other instances
        ch = lambda: [(x.id, x.user.username) for x in control.return_friend_list(control.uprofile) if x not in album.contributors.all()]
        self.fields['idname'] = forms.MultipleChoiceField(
            label='New Contributor', choices=ch)


class ManageGroupMemberForm(forms.Form):
    # todo: order alphabetically
    def __init__(self, myprofile, group, remove=False, *args, **kwargs):
        super(ManageGroupMemberForm, self).__init__(*args, **kwargs)

        friendcontrol = friendcontroller(myprofile.user.id)
        if not remove:
            # add friend to group
            ch = lambda: [(x.user.id, str(x)) for x in friendcontrol.return_friend_list(myprofile) if
                          x not in group.members.all()]
            label = "Add Friends"
        else:
            # remove friend from group
            ch = lambda: [(x.user.id, str(x)) for x in friendcontrol.return_friend_list(myprofile) if
                          x in group.members.all()]
            label = "Remove Friends"

        self.fields['idname'] = forms.MultipleChoiceField(
            label=label, choices=ch)


class DeleteConfirmForm(forms.Form):

    def __init__(self, id, *args, **kwargs):
        super(DeleteConfirmForm, self).__init__(*args, **kwargs)

        self.fields['resource'] = forms.IntegerField(widget=forms.HiddenInput(), initial=id)