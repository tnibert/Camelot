from rest_framework.parsers import JSONParser, FileUploadParser
from rest_framework.exceptions import ParseError
from django.http import HttpResponse, JsonResponse
import json
import base64
from django.contrib.auth.decorators import login_required
from django.http.response import Http404
from django.views.decorators.csrf import csrf_exempt        # don't continue to use this
from ...controllers.albumcontroller import albumcontroller, collate_owner_and_contrib
from ...controllers.utilities import *
from ...apiserializers import PhotoUploadSerializer, PhotoDescriptSerializer
from ...forms import validate_image


# upload photo
@login_required
@csrf_exempt
def upload_photo(request, id):
    """
    Used for image validation in photo upload API call
    Accept POSTed json
    format:
    {
        'description': description of photo
        'image': base 64 encoded image data
    }
    :param request:
    :param id: id of album to upload to
    :return: json response with id of photo
    """
    if request.method == 'POST':
        albumcontrol = return_album_controller(request.user.id, id)

        print(request.body)

        data = FileUploadParser().parse(request)

        # validate posted data
        validation = PhotoUploadSerializer(data=data)
        print(validation.data)
        if validation.is_valid():
            print(validation.data)

            # b64 decode apijson['image']
            #rawimg = base64.decodebytes()
            photoid = 1
            #photoid = albumcontrol.add_photo_to_album(id, '', rawimg).id
            return JsonResponse({"id": photoid}, status=201)
        return JsonResponse(validation.errors, status=400)

    else:
        raise Http404


@login_required
@csrf_exempt
def update_photo_description(request, photoid):
    if request.method == 'POST':
        # get relevant controller and model data
        albumcontrol = albumcontroller(request.user.id)
        photo = albumcontrol.return_photo(photoid)

        # check permissions - must be either photo uploader or album owner to change description
        if (albumcontrol.uprofile != photo.uploader and albumcontrol.uprofile != photo.album.owner) or albumcontrol.uprofile is None:
            raise PermissionException

        # todo: validate the request
        jsdat = request.body.decode('utf8')
        data = json.loads(jsdat)

        try:
            albumcontrol.update_photo_description(photo, data['description'])
        except Exception as e:
            print(e)
            raise e
        return HttpResponse(status=204)



def return_album_controller(userid, albumid):
    albumcontrol = albumcontroller(userid)
    album = albumcontrol.return_album(albumid)
    uploaders = collate_owner_and_contrib(album)
    if albumcontrol.uprofile not in uploaders or albumcontrol.uprofile is None:
        raise PermissionException
    return albumcontrol


def load_post_data(request):
    """
    short form for loading json content from request body
    :param request:
    :return: json data from post request
    """
    return json.loads(request.body.decode('utf-8'))['content']