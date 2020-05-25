from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from django.conf import settings
from functools import wraps
from ..forms import SignUpForm, SearchForm
from ..models import Profile
from ..tokens import account_activation_token
from ..controllers.friendcontroller import friendcontroller
from ..friendfeed import generate_feed
from ..controllers.profilecontroller import profilecontroller
from ..user_emailing import send_registration_email
from ..logs import log_exception
import requests


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


def check_recaptcha(view_func):
    """
    Decorator to check recaptcha
    from https://simpleisbetterthancomplex.com/tutorial/2017/02/21/how-to-add-recaptcha-to-django-site.html
    :param view_func:
    :return:
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # if we are not in production, do not use recaptcha
        if settings.DEBUG is True:
            request.recaptcha_is_valid = True
            return view_func(request, *args, **kwargs)

        request.recaptcha_is_valid = None
        if request.method == 'POST':
            recaptcha_response = request.POST.get('g-recaptcha-response')
            data = {
                'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY,
                'response': recaptcha_response
            }
            r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
            result = r.json()
            if result['success']:
                request.recaptcha_is_valid = True
            else:
                request.recaptcha_is_valid = False
                messages.add_message(request, messages.ERROR, 'Invalid reCAPTCHA. Please try again.')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


@check_recaptcha
def register(request):
    """
    User registration function with email confirmation
    :param request:
    :return:
    """
    if request.method == 'POST' and request.recaptcha_is_valid is True:
        form = SignUpForm(request.POST)

        if form.is_valid():
            try:
                User.objects.get(username__iexact=form.cleaned_data['username'])
            except User.DoesNotExist:
                user = form.save(commit=False)
                user.is_active = False
                user.save()

                try:
                    send_registration_email(user, get_current_site(request).domain)
                except Exception as e:
                    log_exception(__name__, e)

                    # did not send email correctly, roll back
                    user.delete()

                    messages.add_message(request, messages.INFO, 'Error sending confirmation email')
                    # why does this render work, but the bottom one requires a request?
                    return render('camelot/register.html', {'form': form,
                                                            'recaptchakey': settings.GOOGLE_RECAPTCHA_PUBLIC_KEY})

                return redirect('account_activation_sent')

            messages.add_message(request, messages.INFO, 'Username already exists')
        else:
            # there was some error, rerender with errors displayed to user
            return render(request, 'camelot/register.html',
                          {'form': form, 'recaptchakey': settings.GOOGLE_RECAPTCHA_PUBLIC_KEY})

    form = SignUpForm()

    return render(request,
                  'camelot/register.html',
                  {'form': form, 'recaptchakey': settings.GOOGLE_RECAPTCHA_PUBLIC_KEY})


def account_activation_sent(request):
    # todo: add more description to this html (check your spam folder)
    return render(request, 'camelot/account_activation_sent.html')


def activate(request, uidb64, token):
    """
    Profile for the user is created here
    If the profile endpoint is attempted to be accessed before creation (via url)
    then a 500 will be raised on that access
    :param request:
    :param uidb64:
    :param token:
    :return:
    """
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        # activate the account and create the profile

        # the following is just in case a profile was created in the previous ppp version
        try:
            user.profile
        except Profile.DoesNotExist:
            # create() saves to db
            Profile.objects.create(user=user, dname=user.username)

        user.profile.email_confirmed = True
        user.is_active = True
        user.save()

        # create default groups
        profilecontrol = profilecontroller(uid)
        profilecontrol.create_default_groups()

        #login(request, user)
        return redirect('user_home')
    else:
        return render(request, 'camelot/account_activation_invalid.html')
