from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import HttpResponse
from ..controllers.albumcontroller import albumcontroller, AlreadyExistsException
from ..forms import AlbumCreateForm, UploadPhotoForm

"""
Album views
Permissions checking should be in this layer
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

            albumcontrol = albumcontroller(request.user.id)

            try:
                albummodel = albumcontrol.create_album(albumname, albumdescription)
            except AlreadyExistsException as e:
                return HttpResponse('Album name must be unique')

            # response:
            return HttpResponse('Created album ' + albummodel.name)

    # if a GET (or any other method) we'll create a blank form
    else:
        form = AlbumCreateForm()

    return render(request, 'camelot/createalbum.html', {'form': form})


@login_required
def display_albums(request):
    albumcontrol = albumcontroller(request.user.id)
    albums = albumcontrol.return_albums()
    return render(request, 'camelot/showalbums.html', {'albums': albums})
    # showalbums.html might be able to be made more generic, may repeat in showalbum.html

@login_required
def display_album(request):
    # this needs to receive a post
    albumcontrol = albumcontroller(request.user.id)
    album = albumcontrol.return_album()
    # query db for photos in album
    photos = albumcontrol.get_photos_for_album(album)
    # etc etc

@login_required
def add_photo(request):
    # https://docs.djangoproject.com/en/2.0/topics/http/file-uploads/
    # check that user actually has permission to add to this album
    if request.method == 'POST':
        albumcontrol = albumcontroller(request.user.id)     # there has to be a better way than redeclaring this every time
        form = UploadPhotoForm(request.POST, request.FILES)
        if form.is_valid():
            for fi in request.FILES:
                albumcontrol.add_photo_to_album(album, fi)
            return redirect('')     # where to redirect to...
    else:
        form = UploadPhotoForm()
    return render(request, 'uploadphoto.html', {'form': form})