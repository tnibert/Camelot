from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
#import logging
from ..forms import SignUpForm, SearchForm
from ..tokens import account_activation_token
from ..controllers.friendcontroller import friendcontroller
from ..friendfeed import generate_feed

#logger = logging.getLogger(__name__)


"""
User login and home page
"""


def index(request):
    if request.method == "POST":
        # todo: use is_valid() here?
        username = request.POST['username']
        password = request.POST['password']
        # be aware of potential for returning multiple users?
        try:
            temp_user = User.objects.get(username__iexact=username)
        except User.DoesNotExist:
            # create message
            messages.add_message(request, messages.INFO, 'Invalid Login')
            return redirect("index")
        user = authenticate(username=temp_user.username, password=password)
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
    pcontrol = profilecontroller(request.user.id)
    retdict = {
        "pendingreqs": len(friendcontroller(request.user.id).return_pending_requests()),
        "searchform": SearchForm(),
        "feed": generate_feed(pcontrol)[:15]
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

from ..controllers.profilecontroller import profilecontroller


# user registration function with email confirmation
def register(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            try:
                User.objects.get(username__iexact=form.cleaned_data['username'])
            except User.DoesNotExist:
                user = form.save(commit=False)
                user.is_active = False
                user.save()

                current_site = get_current_site(request)
                subject = 'Activate Your PicPicPanda Account'
                message = render_to_string('camelot/account_activation_email.html', {
                    'user': user,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode(),
                    'token': account_activation_token.make_token(user),
                })
                try:
                    user.email_user(subject, message)
                except Exception as e:
                    # did not send email correctly, roll back
                    user.delete()
                    #logger.warning(e)
                    messages.add_message(request, messages.INFO, 'Error sending confirmation email')
                    # why does this render work, but the bottom one requires a request?
                    return render('camelot/register.html', {'form': form})

                return redirect('account_activation_sent')

            messages.add_message(request, messages.INFO, 'Username already exists')

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

        # create default groups
        profilecontrol = profilecontroller(uid)
        profilecontrol.create_default_groups()

        #login(request, user)
        return redirect('user_home')
    else:
        return render(request, 'camelot/account_activation_invalid.html')
