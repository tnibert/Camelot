import json
from django.contrib.auth.decorators import login_required
from ...controllers.albumcontroller import albumcontroller, collate_owner_and_contrib
from ...controllers.utilities import *

# upload photo
@login_required
def upload_photo(request, id):
    """
    Accept POSTed json
    format:
    {
        'description': description of photo
        'image': raw image data
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

        # process request body and get image file
        apijson = load_post_data(request)

        # todo: sanitize image data
        albumcontrol.add_photo_to_album(id, apijson['description'], apijson['image'])

    else:
        # return 404
        pass

    todo: test


def load_post_data(request):
    """
    short form for loading json content from request body
    :param request:
    :return: json data from post request
    """
    return json.loads(request.body.decode('utf-8'))['content']