from django.shortcuts import render
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
        # redirect to user page

    else:
        return render(request, 'camelot/index.html')

def user_logout(request):
    logout(request)
    return HttpResponse("Logout")
