import requests
import json
from login import login, HOST


def upload_photo(albumid):
    """
    This is an example of how to interface with the photo upload api endpoint using requests
    :param albumid:
    :return:
    """
    s = login("testuser", "testpassword")
    with open('../resources/testimage.jpg', 'rb') as f:
        response = s.post("{}/api/upload/{}".format(HOST, albumid), files={'image': f})

    print(response)
    data = json.loads(response.content)
    print(data)

if __name__ == '__main__':
    upload_photo(23)
