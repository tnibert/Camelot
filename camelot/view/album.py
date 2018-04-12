from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404
from django.forms import MultipleChoiceField
from ..controllers.albumcontroller import albumcontroller, collate_owner_and_contrib
from ..controllers.friendcontroller import are_friends
from ..controllers.utilities import PermissionException
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


def display_photo(request, photoid):
    """
    Display an individual photo in UI
    Allow circular navigation through all photos in album, so must generate previous and next photo ids
    :param request:
    :param photoid:
    :return:
    """
    # todo: verify what happens if you have only 0, 1, or 2 photos in album

    albumcontrol = albumcontroller(request.user.id)
    photo = albumcontrol.return_photo(photoid)

    # permission check
    if not albumcontrol.has_permission_to_view(photo.album):
        raise PermissionException

    albumphotos = albumcontrol.get_photos_for_album(photo.album)

    # find index of our photo in the queryset
    i = list(albumphotos.values_list('id', flat=True)).index(int(photoid))

    retdict = {
        'next': albumphotos[i+1].id if i < (len(albumphotos) - 1) else albumphotos[0].id,
        'previous': albumphotos[i-1].id if i > 0 else albumphotos[(len(albumphotos)-1)].id,
        'photo': photo
    }

    return render(request, 'camelot/presentphoto.html', retdict)

def pretty_request(request):
    headers = ''
    for header, value in request.META.items():
        if not header.startswith('HTTP'):
            continue
        header = '-'.join([h.capitalize() for h in header[5:].lower().split('_')])
        headers += '{}: {}\n'.format(header, value)

    return (
        '{method} HTTP/1.1\n'
        'Content-Length: {content_length}\n'
        'Content-Type: {content_type}\n'
        '{headers}\n\n'
        '{body}'
    ).format(
        method=request.method,
        content_length=request.META['CONTENT_LENGTH'],
        content_type=request.META['CONTENT_TYPE'],
        headers=headers,
        body=request.body,
    )

@login_required
def add_photo(request, id):
    """
    Add a photo to an album
    Presents form or processes on POST
    :param request:
    :param id: id of the album to add photo to
    :return:
    """
    # todo: add more checking for correct values,
    # descriptions and files need to have same number of elements
    # fname needs to be of correct format
    # confirm all possible ways the js can be messed with

    # todo: add ability to select multiple files in file picker and auto fill form

    #print("In View")
    # https://docs.djangoproject.com/en/2.0/topics/http/file-uploads/
    albumcontrol = albumcontroller(request.user.id)
    # will raise PermissionException if user does not have permission to view
    album = albumcontrol.return_album(id)
    uploaders = collate_owner_and_contrib(album)
    # check that user actually has permission to add to this album before showing view
    # this collation and check may be best in its own function
    if albumcontrol.uprofile not in uploaders or albumcontrol.uprofile is None:
        raise PermissionException

    if request.method == 'POST':
        #print("In View Post")
        form = UploadPhotoForm(request.POST, request.FILES, extra=request.POST.get('extra_field_count'))
        #print("Created post form")
        #print("in post, form.extra_fields is " + str(form.extra_fields))
        if form.is_valid():
            #print("Form valid")
            #for i, j in form.cleaned_data.items():
            #    print(str(i) + " = " + str(j))
            photodesc = []
            photodesc.append(form.cleaned_data['desc_0'])
            for i in range(int(form.extra_fields)):
                #print(i)
                photodesc.append(form.cleaned_data['desc_' + str(i+1)])
            #print(photodesc)
            for fname, fdat in request.FILES.items():
                #print(fname)
                # figure out our index to match description to file
                index = int(fname.split('_')[1])
                # this method will check permission
                albumcontrol.add_photo_to_album(id, photodesc[index], fdat)

            return redirect("show_album", id)
    else:
        form = UploadPhotoForm()
    return render(request, 'camelot/uploadphoto.html', {'form': form, 'albumid': id})   # so maybe we make the move to class based views


def return_photo_file_http(request, photoid):
    """
    wrapper to securely show a photo without exposing externally
    We must ensure the security of photo.filename, because if this can be messed with our whole filesystem could be vulnerable
    :param request:
    :param photoid: id of photo
    :return:
    """
    albumcontrol = albumcontroller(request.user.id)
    photo = albumcontrol.return_photo(photoid)

    # permission check
    if not albumcontrol.has_permission_to_view(photo.album):
        raise PermissionException

    # we might want to enclose this in a try except block, but for now it is ok like this
    with open(photo.filename, "rb") as f:
        return HttpResponse(f.read(), content_type="image/*")


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

    if album.owner != request.user.profile and request.user.profile not in album.contributors.all():
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
