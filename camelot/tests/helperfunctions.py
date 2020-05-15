from ..controllers.friendcontroller import friendcontroller
from ..controllers.utilities import get_profile_from_uid


def complete_add_friends(requesterid, requesteeid):
    """
    Execute a full friend request and confirm for testing
    :param requesterid: userid of requester
    :param requesteeid: userid of requestee
    :return: friendship object
    """
    friendcontrol1 = friendcontroller(requesterid)
    friendcontrol2 = friendcontroller(requesteeid)
    fship = friendcontrol1.add(get_profile_from_uid(requesteeid))
    friendcontrol2.confirm(get_profile_from_uid(requesterid))
    return fship


def pretty_request(request):
    headers = ''
    for header, value in request.META.items():
        if not header.startswith('HTTP'):
            continue
        header = '-'.join([h.capitalize() for h in header[5:].lower().split('_')])
        headers += '{}: {}\n'.format(header, value)

    return (
        '{method} HTTP/1.1\n'
        'Content-Length: {content_length}\n'
        'Content-Type: {content_type}\n'
        '{headers}\n\n'
        '{body}'
    ).format(
        method=request.method,
        content_length=request.META['CONTENT_LENGTH'],
        content_type=request.META['CONTENT_TYPE'],
        headers=headers,
        body=request.body,
    )
