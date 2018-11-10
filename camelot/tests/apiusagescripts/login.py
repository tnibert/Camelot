import requests


HOST = 'http://127.0.0.1:8000'


def login(username, password):

    s = requests.session()
    p = s.get(HOST)
    csrftoken = s.cookies['csrftoken']

    payload = {
        'csrfmiddlewaretoken': csrftoken,
        'username': username,
        'password': password
    }

    print(csrftoken)
    p = s.post(HOST, data=payload, headers=dict(Referer=HOST))
    print(p)
    return s