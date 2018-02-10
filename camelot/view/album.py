from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import HttpResponse
from ..controllers import albumcontroller
from ..forms import AlbumCreateForm

"""
Album views
"""

@login_required
def create_album(request):
    # TEST: this *might* be creating 2 of the same album on the first creation, make unit test
    # if this is a POST request we need to process the form data
    if request.method == 'POST':        # this all needs to be put in the controller.. maybe
        # create a form instance and populate it with data from the request:
        form = AlbumCreateForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            albumname = form.cleaned_data['albumname']
            albumdescription = form.cleaned_data['description']

            albummodel = albumcontroller.create_album(albumname, albumdescription, request.user.id)
            # response:
            return HttpResponse('Created album ' + albummodel.name)

    # if a GET (or any other method) we'll create a blank form
    else:
        form = AlbumCreateForm()

    return render(request, 'camelot/createalbum.html', {'form': form})


@login_required
def display_albums(request):
    albums = albumcontroller.return_albums(request.user.id)
    return render(request, 'camelot/showalbums.html', {'albums': albums})

@login_required
def display_album(request):
    pass

