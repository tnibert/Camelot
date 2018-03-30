from ..controllers.friendcontroller import friendcontroller
from ..controllers.utilities import get_profile_from_uid
# add friends
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