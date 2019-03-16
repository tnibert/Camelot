from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404, JsonResponse
from django.forms import MultipleChoiceField
from django.views.decorators.http import etag
from django.template.loader import render_to_string
from random import randint
from ..controllers.albumcontroller import albumcontroller, collate_owner_and_contrib
from ..controllers.friendcontroller import are_friends
from ..controllers.utilities import PermissionException, get_rotation
from ..forms import AlbumCreateForm, UploadPhotoForm, EditAlbumAccesstypeForm, MyGroupSelectForm, AddContributorForm, DeleteConfirmForm
from ..constants import *
from ..controllers.utilities import *
from ..models import Profile, FriendGroup, Photo
from ..logs import log_exception

#def album_perm_check(func):
#    """
#    This is a decorator to validate permissions
#    This is being implemented late, so it isn't used in most places we check permissions
#    Has been created for photo returning etag
#    :param func:
#    :return:
#    """
#    def wrapper(*args, **kwargs):
#        pass
#    return wrapper

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


def display_albums(request, userid, api=False):
    # todo: add unit test for non logged in user accessing
    albumcontrol = albumcontroller(request.user.id)

    # get albums
    albums = albumcontrol.return_albums(userid)
    contrib = albumcontrol.return_albums(userid, contrib=True)

    # get an image for each album
    for album in (albums+contrib):
        photos = albumcontrol.get_photos_for_album(album)
        if len(photos) > 0:
            # we check if this exists in the template and if not, render a default image
            randindex = randint(0, len(photos)-1)
            album.temp = photos[randindex].id
            album.myphotorotation = get_rotation(photos[randindex])
            #print(album.myphotorotation)

    # create dictionary to render
    retdict = {}
    retdict['userid'] = int(userid)

    if not api:
        retdict['albums'] = albums

        if len(contrib) > 0:
            retdict['contrib'] = contrib

        return render(request, 'camelot/showalbums.html', retdict)
        # showalbums.html might be able to be made more generic, may repeat in showalbum.html

    else:
        # form albums field into json compatible format
        retdict['albums'] = [{'id': album.id, 'name': album.name, 'description': album.description } for album in albums]
        if len(contrib) > 0:
            retdict['contrib'] = [{'id': album.id, 'name': album.name, 'description': album.description} for album in contrib]

        return JsonResponse(retdict, status=200)


def display_album(request, id, contribid=None, api=False):
    """
    Display photos for album
    :param request:
    :param id: id of album (need to validate permissions)
    :param contribid: if we reached the page from a contributor's show albums page, back nav to contributor
    :param api: boolean for if we return a json response or not
    :return:
    """

    albumcontrol = albumcontroller(request.user.id)
    album = albumcontrol.return_album(id)
    # query db for photos in album
    photos = albumcontrol.get_photos_for_album(album)

    # return for api
    if api:
        if request.method == 'GET':
            retdict = {}
            retdict['photos'] = [{'id': photo.id, 'description': photo.description, 'pub_date': photo.pub_date, 'type': photo.imgtype } for photo in photos]

            return JsonResponse(retdict, status=200)
        else:
            raise Http404

    # return for html rendering
    else:
        for photo in photos:

            try:
                photo.myrotation = get_rotation(photo)
            except Exception as e:
                print(e)
                print(type(e))

        # for back link navigation to contributors
        # if the id provided is not valid, set to the album owner
        if not contribid or int(contribid) not in [x.id for x in collate_owner_and_contrib(album)]:
            contribid = album.owner.id

        retdict = {'photos': photos, 'album': album, 'contribid': contribid}

        return render(request, 'camelot/showalbum.html', retdict)



def display_photo(request, photoid):
    """
    Display an individual photo in UI
    Allow circular navigation through all photos in album, so must generate previous and next photo ids
    :param request:
    :param photoid:
    :return:
    """

    albumcontrol = albumcontroller(request.user.id)
    photo = albumcontrol.return_photo(photoid)

    # permission check
    if not albumcontrol.has_permission_to_view(photo.album):
        raise PermissionException

    albumphotos = albumcontrol.get_photos_for_album(photo.album)

    # find index of our photo in the queryset
    i = list(albumphotos.values_list('id', flat=True)).index(int(photoid))

    rotation = get_rotation(photo)

    retdict = {
        'next': albumphotos[i+1].id if i < (len(albumphotos) - 1) else albumphotos[0].id,
        'previous': albumphotos[i-1].id if i > 0 else albumphotos[(len(albumphotos)-1)].id,
        'photo': photo,
        'rotation': rotation
    }

    return render(request, 'camelot/presentphoto.html', retdict)


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
    # todo: add ability to select multiple files in file picker and auto fill form

    # https://docs.djangoproject.com/en/2.0/topics/http/file-uploads/
    albumcontrol = albumcontroller(request.user.id)
    # will raise PermissionException if user does not have permission to view
    album = albumcontrol.return_album(id)
    uploaders = collate_owner_and_contrib(album)
    # check that user actually has permission to add to this album before showing view
    # this collation and check may be best in its own function
    if albumcontrol.uprofile not in uploaders or albumcontrol.uprofile is None:
        raise PermissionException

    form = UploadPhotoForm()

    return render(request, 'camelot/uploadphoto.html', {'form': form, 'albumid': id})


def make_photo_etag(request, *args, **kwargs):
    """
    Permission check and return etag for photo
    :param request:
    :param args:
    :param kwargs:
    :return: etag if has permission, else raise PermissionException
    """
    photoid = kwargs.get('photoid')
    albumcontrol = albumcontroller(request.user.id)
    photo = albumcontrol.return_photo(int(photoid))
    if not albumcontrol.has_permission_to_view(photo.album):
        raise PermissionException
    else:
        return str(photo.pub_date)


@etag(make_photo_etag)
def return_photo_file_http(request, photoid, thumb=False, mid=True):
    """
    wrapper to securely show a photo without exposing externally
    We must ensure the security of photo.filename, because if this can be messed with our whole filesystem could be vulnerable
    :param request:
    :param photoid: id of photo
    :param thumb: If true display thumbnail image
    :param mid: If true and thumb is false, display mid size image
    If both thumb and mid are false, display full size image
    :return:
    """
    # Permission check moved to make_photo_etag()
    # and the next two lines just got redundant... double db queries...
    albumcontrol = albumcontroller(request.user.id)
    photo = albumcontrol.return_photo(photoid)

    # default to rendering midsize image
    name = photo.midsize
    # todo: handle conversion to jpeg of existing images in migration
    mime = "image/jpeg"
    if thumb:
        name = photo.thumb
    elif not mid:
        name = photo.filename
        mime = photo.imgtype

    # we might want to enclose these withs in a try except block, but for now it is ok like this
    #try:
    with open(name, "rb") as f:
        return HttpResponse(f.read(), content_type=mime)
    # if we don't have a thumb, pass the whole image - it's an option
    #except FileNotFoundError:
        # todo: log


@login_required
def delete_photo(request, photoid):
    """
    Delete a photo

    There is too much copy pasting between this and and delete_album()
    May want to consolidate later

    :param request:
    :param photoid: id of photo to delete
    :return: redirect to album
    """
    albumcontrol = albumcontroller(request.user.id)
    photo = albumcontrol.return_photo(photoid)
    album = photo.album

    # if we are not the owner or uploader, don't allow access
    if albumcontrol.uprofile != album.owner and albumcontrol.uprofile != photo.uploader:
        raise PermissionException

    # if we post, delete the photo
    if request.method == 'POST':
        # controller method will check permission
        if albumcontrol.delete_photo(photo):
            return redirect("show_album", album.id)
        else:
            # todo: add some kind of failure notification
            return redirect("present_photo", photo.id)
    # if we don't post, present confirmation form
    else:
        # present confirmation dialog
        confirm = DeleteConfirmForm(photo.id)
        retdict = {'confirmform': confirm, 'photo': photo}
        return render(request, "camelot/confirmdelete.html", retdict)

# I don't like how similar the code between show albums and show album is
@login_required
def delete_album(request, albumid):
    """
    Ok, I was wrong, let's be more restful
    Delete an album, check for confirmation first
    :param request:
    :param albumid: id of album to delete
    :return:
    """

    albumcontrol = albumcontroller(request.user.id)
    album = albumcontrol.return_album(albumid)

    if albumcontrol.uprofile != album.owner:
        raise PermissionException

    if request.method == 'POST':
        # todo: should use form to get album id
        if albumcontrol.delete_album(album):
            messages.add_message(request, messages.INFO, "Successfully deleted album")
            return redirect("show_albums", albumcontrol.uprofile.id)
        else:
            messages.add_message(request, messages.INFO, "Failed to delete album")
            return redirect("show_album", album.id)

    else:
        # present confirmation dialog
        confirm = DeleteConfirmForm(albumid)
        retdict = {'confirmform': confirm, 'album': album}
        return render(request, "camelot/confirmdelete.html", retdict)


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
        retdict["groups"] = list(album.groups.all())        # todo: specify which user with group
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

            assert atype in ACCESSTYPES.keys()
            albumcontrol.set_accesstype(album, atype)
            return redirect("manage_album", id)

    raise Http404

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
    raise Http404

@login_required
def add_contrib(request, albumid):
    """
    Add a contributor to the album
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

                        # notify the new contributor
                        try:
                            # prepare email
                            subject = "You've been invited to contribute to a photo album!"
                            message = render_to_string('camelot/added_as_contributor.html', {
                                'user': c.user,
                                'adder': albumcontrol.uprofile.dname,
                                'thealbum': album.name,
                                'albumid': album.id,
                            })
                            # send email
                            c.user.email_user(subject, message)
                        except Exception as EmailEx:
                            # failed to send email
                            # log here because this error should not abort the process
                            log_exception(__name__, EmailEx)

                    except Exception as e:
                        raise e

        return redirect("manage_album", album.id)

    # if not a post, we 404
    raise Http404


def download_album(request, albumid):
    pass
