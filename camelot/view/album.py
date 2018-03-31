from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404
from django.forms import MultipleChoiceField
from ..controllers.albumcontroller import albumcontroller
from ..controllers.friendcontroller import are_friends
from ..forms import AlbumCreateForm, UploadPhotoForm, EditAlbumAccesstypeForm, MyGroupSelectForm, AddContributorForm
from ..constants import *
from ..controllers.utilities import *
from ..models import Profile, FriendGroup

"""
Album views
"""

@login_required
def create_album(request):

    # if this is a POST request we need to process the form data
    if request.method == 'POST':

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
                return render(request, 'camelot/messageloggedin.html', {'message': 'Album name must be unique'})

            return redirect("show_album", albummodel.id)

    # if a GET (or any other method) we'll create a blank form
    else:
        form = AlbumCreateForm()

    return render(request, 'camelot/createalbum.html', {'form': form})


@login_required
def display_albums(request, userid):
    albumcontrol = albumcontroller(request.user.id)
    albums = albumcontrol.return_albums(userid)
    return render(request, 'camelot/showalbums.html', {'albums': albums})
    # showalbums.html might be able to be made more generic, may repeat in showalbum.html

@login_required
def display_album(request, id):
    """

    :param request:
    :param id: id of album (need to validate permissions)
    :return:
    """
    # todo: add check for permission exception raised
    albumcontrol = albumcontroller(request.user.id)
    album = albumcontrol.return_album(id)
    # query db for photos in album
    photos = albumcontrol.get_photos_for_album(album)

    return render(request, 'camelot/showalbum.html', {'photos': photos, 'album': album})

@login_required
def add_photo(request, id):
    """
    Need to check if user has permission to access this view
    :param request:
    :param id: id of the album to add photo to
    :return:
    """

    # https://docs.djangoproject.com/en/2.0/topics/http/file-uploads/
    # check that user actually has permission to add to this album
    if request.method == 'POST':
        albumcontrol = albumcontroller(request.user.id)     # there has to be a better way than redeclaring this every time
                                                            # probably with class views and sessions?
        form = UploadPhotoForm(request.POST, request.FILES)

        if form.is_valid():
            photodescription = form.cleaned_data['description']
            for fname, fdat in request.FILES.items():
                # need to sort out multiple file upload and association with description
                albumcontrol.add_photo_to_album(id, photodescription, fdat)
            return redirect("show_album", id)
    else:
        form = UploadPhotoForm()
    return render(request, 'camelot/uploadphoto.html', {'form': form, 'albumid': id})   # so maybe we make the move to class based views

def return_photo_file_http(request, photoid):
    """
    wrapper to security show a photo without exposing externally
    We must ensure the security of photo.filename, because if this can be messed with our whole filesystem could be vulnerable
    :param request:
    :param uid: id of user profile that uploaded photo
    :param albumid: id of album photo belongs to
    :param photoid: id of photo
    :return:
    """
    albumcontrol = albumcontroller(request.user.id)
    photo = albumcontrol.return_photo(photoid)

    # todo: add in permissions check

    try:
        # this scares me from a memory perspective
        with open(photo.filename, "rb") as f:
            return HttpResponse(f.read(), content_type="image/*")
    except IOError:
        # maybe edit this except to be more applicable..
        from PIL import Image
        red = Image.new('RGBA', (1, 1), (255, 0, 0, 0))
        response = HttpResponse(content_type="image/*")
        red.save(response, "JPEG")
        return response


@login_required
def manage_album_permissions(request, albumid):
    """
    Page to manage permissions of album
    Owner should be able to set access type
    Contributors and owner should be able to set groups (but only own groups)
    """
    albumcontrol = albumcontroller(request.user.id)

    # may raise permission exception
    album = albumcontrol.return_album(albumid)

    if album.owner != request.user.profile and request.user.profile not in album.contributors:
        raise PermissionException

    retdict = {
        "owner": album.owner.user.username,
        "contributors": [contrib.user.username for contrib in list(album.contributors.all())],
        "albumid": album.id,
        "accesstype": ACCESSTYPES[album.accesstype]
    }

    if album.owner == request.user.profile:
        retdict["accesstypeform"] = EditAlbumAccesstypeForm()
        retdict["addcontributorsform"] = AddContributorForm(request.user.id, album)

    if album.accesstype == ALBUM_GROUPS:
        retdict["groups"] = list(album.groups.all())        # todo: this needs to be changed to only show for current user
        retdict["groupform"] = MyGroupSelectForm(request.user.id, MultipleChoiceField)

    return render(request, "camelot/managealbumpermission.html", retdict)

@login_required
def update_access_type(request, id):
    """
    Update the access type for a given album
    :param request:
    :param id: album id
    :return:
    """
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = EditAlbumAccesstypeForm(request.POST)

        # check whether it's valid:
        if form.is_valid():
            albumcontrol = albumcontroller(request.user.id)
            album = albumcontrol.return_album(id)
            if album.owner != albumcontrol.uprofile:
                raise PermissionException
            atype = int(form.cleaned_data["mytype"])
            print(atype)
            assert atype in ACCESSTYPES.keys()
            albumcontrol.set_accesstype(album, atype)
            return redirect("manage_album", id)

    return Http404

@login_required
def add_groups(request, albumid):
    """
    Add a group to an album
    :param request:
    :param albumid:
    :return:
    """
    if request.method == 'POST':
        albumcontrol = albumcontroller(request.user.id)
        album = albumcontrol.return_album(albumid)

        # only owner or contributors can add a group
        if albumcontrol.uprofile != album.owner and albumcontrol.uprofile not in album.contributors.all():
            raise PermissionException

        form = MyGroupSelectForm(request.user.id, MultipleChoiceField, request.POST)

        if form.is_valid():
            groups = [FriendGroup.objects.get(id=int(x)) for x in form.cleaned_data['idname']]
            for g in groups:
                # redundant
                # ok, error checking is in controller, let's let it do it's job
                #if albumcontrol.uprofile != g.owner:
                #    raise PermissionException
                if g in album.groups.all():
                    continue
                else:
                    try:
                        # this assert may need to be handled at a higher level depending on what django does
                        assert albumcontrol.add_group_to_album(album, g)
                    except Exception as e:
                        raise PermissionException

        return redirect("manage_album", album.id)

    # if not a post, we 404
    return Http404

@login_required
def add_contrib(request, albumid):
    """
    Add a contributor to the album
    This function makes me cry
    :param request:
    :param albumid: album id
    :return: redirect to album management page or 404 if not post
    """
    if request.method == 'POST':
        albumcontrol = albumcontroller(request.user.id)
        album = albumcontrol.return_album(albumid)

        # only owner can add contributors
        if albumcontrol.uprofile != album.owner:
            raise PermissionException

        form = AddContributorForm(request.user.id, album, request.POST)

        if form.is_valid():
            # should this db query be in a controller?  for now we will leave it as this
            contributors = [Profile.objects.get(id=int(x)) for x in form.cleaned_data['idname']]
            for c in contributors:
                # redundant with add_contributor_to_album() ?
                if not are_friends(c, albumcontrol.uprofile):
                    raise PermissionException

                if c in album.contributors.all():
                    continue
                else:
                    try:
                        # this assert may need to be handled at a higher level depending on what django does
                        assert albumcontrol.add_contributor_to_album(album, c)
                    except Exception as e:
                        raise e

        return redirect("manage_album", album.id)

    # if not a post, we 404
    return Http404
