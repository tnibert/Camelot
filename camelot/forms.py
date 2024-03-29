from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from .constants import *
from .constants2 import SITEDOMAIN
from .controllers.groupcontroller import groupcontroller
from .controllers.friendcontroller import friendcontroller
from .logs import log_exception
from .user_emailing import send_registration_email


def validate_email(value):
    """
    Validate that email address of newly created user is not already registered
    https://docs.djangoproject.com/en/dev/ref/validators/
    :param value:
    :return:
    """
    # this will raise django.contrib.auth.models.MultipleObjectsReturned if email is not unique
    try:
        user = User.objects.get(email=value)
    except User.DoesNotExist:
        # if a user doesn't exist with the email, we pass
        return

    # if the email address has been registered previously,
    # we will silently send another registration email
    # and prevent the form from validating
    if user.is_active is False:
        try:
            send_registration_email(user, SITEDOMAIN, htmlfile='camelot/account_activation_reminder.html')
        except Exception as e:
            log_exception(__name__, e)

        raise ValidationError("Email address unavailable, please check your email")

    # if a user does exist with the email, raise
    raise ValidationError("Email address not available")


def validate_username(value):
    """
    Ensure that usernames that are the same with differing cases are invalid
    :param value:
    :return:
    """
    try:
        User.objects.get(username__iexact=value)
    except User.DoesNotExist:
        return

    raise ValidationError("Username already exists")


class SignUpForm(UserCreationForm):
    email = forms.EmailField(help_text='Required', validators=[validate_email])
    username = forms.CharField(help_text='Required', validators=[validate_username])

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', )


class AlbumCreateForm(forms.Form):
    albumname = forms.CharField(label='Photo album name', max_length=70)
    description = forms.CharField(label='Photo album description', max_length=300, required=False)


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
