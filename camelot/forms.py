from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

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

