import requests
import json
from login import login, HOST


def alter_description(s, photoid, desc):
    """
    Example of how to change photo description using requests and API
    :param s:
    :param photoid:
    :param desc:
    :return:
    """
    payload = {"description": desc}
    headers = {'content_type': "application/json"}
    p = s.post("{}/api/update/photo/desc/{}".format(HOST, photoid),
                                    json.dumps(payload))
    print(p)
    return p