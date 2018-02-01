from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout

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
                return HttpResponse("Account Disabled")
        else:
            # need to do something like flask's flash function for these...
            return HttpResponse("Invalid")

    # if user is already logged in
    if request.user.is_authenticated:
        # redirect to user page
        return redirect("user_home")
    else:
        return render(request, 'camelot/index.html')

def user_home(request):
    # this authentication check needs to be a decorator
    if request.user.is_authenticated:
        return render(request, 'camelot/home.html')
    else:
        return redirect("index")

def user_logout(request):
    logout(request)
    return redirect("index")

# need to implement a user registration function with email confirmation
def register(request):
    pass 
