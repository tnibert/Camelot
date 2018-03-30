from ..controllers.friendcontroller import friendcontroller

# add friends
def complete_add_friends(requesterid, requesteeid):
    """

    :param requesterid:
    :param requesteeid:
    :return: friendship object
    """
    friendcontrol1 = friendcontroller(requesterid)
    friendcontrol2 = friendcontroller(requesteeid)
    fship = friendcontrol1.add(friendcontrol2.profile)
    friendcontrol2.confirm(friendcontrol1.profile)
    return fship