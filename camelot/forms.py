from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class SignUpForm(UserCreationForm):
    email = forms.EmailField(help_text='Required')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', )

class AlbumCreateForm(forms.Form):
    albumname = forms.CharField(label='Photo album name', max_length=100)
    description = forms.CharField(label='Photo album description', max_length=500)
