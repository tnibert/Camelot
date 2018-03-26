from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages

from ..forms import SignUpForm
from ..tokens import account_activation_token
from ..controllers.friendcontroller import friendcontroller

"""
User login and home page
"""

def index(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)    # check for login failure?
                return redirect("user_home")
            else:
                # add unit test coverage
                messages.add_message(request, messages.INFO, 'Please confirm your account')
                return redirect("index")

        else:
            # need to do something like flask's flash function for these...
            # only one error message should show for all bad logins (don't reveal user's existance)
            # fix unit test for redirect and check for message
            messages.add_message(request, messages.INFO, 'Invalid Login')
            return redirect("index")

    # if user is already logged in
    if request.user.is_authenticated:
        # redirect to user page
        return redirect("user_home")
    else:
        return render(request, 'camelot/index.html')

@login_required
def user_home(request):
    retdict = {
        "pendingreqs": len(friendcontroller(request.user.id).return_pending_requests())
    }
    return render(request, 'camelot/home.html', retdict)

def user_logout(request):
    logout(request)
    return redirect("index")

"""
User registration
"""

from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string

# need to implement a user registration function with email confirmation
# need to error handle if email can't be sent
def register(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            current_site = get_current_site(request)
            subject = 'Activate Your Camelot Account'
            message = render_to_string('camelot/account_activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode(),
                'token': account_activation_token.make_token(user),
            })
            user.email_user(subject, message)

            return redirect('account_activation_sent')
    else:
        form = SignUpForm()
    
    return render(request, 'camelot/register.html', {'form': form})

def account_activation_sent(request):
    return render(request, 'camelot/account_activation_sent.html')


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.profile.email_confirmed = True
        user.save()
        login(request, user)
        return redirect('user_home')
    else:
        return render(request, 'camelot/account_activation_invalid.html')
