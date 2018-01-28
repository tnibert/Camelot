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
                login(request, user)
                return HttpResponse("Successful")
            else:
                return HttpResponse("Account Disabled")
        else:
            return HttpResponse("Invalid")

    # if user is already logged in
    if request.user.is_authenticated:
        # redirect to user page
        return HttpResponse("You are logged in")

    else:
        return render(request, 'camelot/index.html')

def user_logout(request):
    logout(request)
    return HttpResponse("Logout")

# need to implement a user registration function with email confirmation
