from django.http import HttpResponse, JsonResponse
import json
import io
from django.contrib.auth.decorators import login_required
from django.http.response import Http404
from ...controllers.albumcontroller import albumcontroller, collate_owner_and_contrib
from ...controllers.utilities import *
from ...datavalidation.validationfunctions import *


@login_required
def upload_photo(request, id):
    """
    Upload photo via API
    Accept POSTed request with field 'image' of raw image data

    :param request:
    :param id: id of album to upload to
    :return: json response with id of photo
    """

    if request.method == 'POST':

        def return_album_controller(userid, albumid):
            albumcontrol = albumcontroller(userid)
            album = albumcontrol.return_album(albumid)
            uploaders = collate_owner_and_contrib(album)
            if albumcontrol.uprofile not in uploaders or albumcontrol.uprofile is None:
                raise PermissionException
            return albumcontrol

        albumcontrol = return_album_controller(request.user.id, id)

        rawimg = io.BytesIO()
        rawimg.write(request.FILES['image'].read())

        # todo: validate image, running into issues using bytesio object, no attrib size
        # validate size
        # validate is image -> http://effbot.org/imagingbook/image.htm#tag-Image.Image.verify
        validate_image(rawimg)

        photoid = albumcontrol.add_photo_to_album(id, '', rawimg).id
        return JsonResponse({"id": photoid}, status=201)

    else:
        raise Http404


@login_required
def update_photo_description(request, photoid):
    """
    Update the description of a photo
    :param request: json post request {'description': 'new description'}
    :param photoid: the id of the photo to update descriotion of
    :return: HTTP 204 code on success, 404 if not POST
    """

    if request.method == 'POST':
        # get relevant controller and model data
        albumcontrol = albumcontroller(request.user.id)
        photo = albumcontrol.return_photo(photoid)

        # check permissions - must be either photo uploader or album owner to change description
        if (albumcontrol.uprofile != photo.uploader and albumcontrol.uprofile != photo.album.owner) or albumcontrol.uprofile is None:
            raise PermissionException

        jsdat = request.body.decode('utf8')
        data = json.loads(jsdat)

        # validate
        validatedstr = validate_photo_description(data['description'])

        try:
            albumcontrol.update_photo_description(photo, validatedstr)
        except Exception as e:
            print(e)
            raise e
        return HttpResponse(status=204)
    else:
        raise Http404


def load_post_data(request):
    """
    short form for loading json content from request body
    :param request:
    :return: json data from post request
    """
    return json.loads(request.body.decode('utf-8'))['content']