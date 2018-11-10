import requests
import json
from login import HOST


def upload_photo(s, albumid):
    """
    This is an example of how to interface with the photo upload api endpoint using requests
    :param albumid:
    :return:
    """
    with open('../resources/testimage.jpg', 'rb') as f:
        response = s.post("{}/api/upload/{}".format(HOST, albumid), files={'image': f})

    print(response)
    data = json.loads(response.content)
    print(data)
    return data
