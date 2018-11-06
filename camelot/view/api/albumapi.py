from rest_framework.parsers import MultiPartParser
from django.http import HttpResponse, JsonResponse
import base64
from django.contrib.auth.decorators import login_required
from django.http.response import Http404
from django.views.decorators.csrf import csrf_exempt        # don't continue to use this
from ...controllers.albumcontroller import albumcontroller, collate_owner_and_contrib
from ...controllers.utilities import *
from ...forms import UploadPhotoAPIForm
from ...apiserializers import PhotoUploadSerializer


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
    :return:
    """
    if request.method == 'POST':
        # the following should probably be in a function used by both this and add_photo()
        albumcontrol = albumcontroller(request.user.id)
        album = albumcontrol.return_album(id)
        uploaders = collate_owner_and_contrib(album)
        if albumcontrol.uprofile not in uploaders or albumcontrol.uprofile is None:
            raise PermissionException

        print(request.body)
        # todo: parsing is going haywire
        data = MultiPartParser().parse(request)

        # validate posted data
        validation = PhotoUploadSerializer(data=data)
        print(validation.data)
        if validation.is_valid():
            print(validation.data)

            # b64 decode apijson['image']
            #rawimg = base64.decodebytes()

            #albumcontrol.add_photo_to_album(id, apijson['description'], rawimg)
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