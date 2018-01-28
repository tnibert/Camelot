from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout

def index(request):
    if request.method == "POST":
        return HttpResponse("We have received a post!")
    else:
        return render(request, 'camelot/index.html')
