from login import HOST
import json


def get_albums(s, userid):
    response = s.get(HOST + "/api/{}/getalbums".format(userid))
    data = json.loads(response.content)
    return data
