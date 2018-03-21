from .genericcontroller import genericcontroller
from ..models import Friendship, Profile, FriendGroup
from .utilities import AlreadyExistsException, AddSelfException
from django.db.models import Q

class friendcontroller(genericcontroller):

    def add(self, profile):
        """
        add a friend, at the end of this method the friendship will still need to be confirmed
        :param profile: profile of user to add
        :return: friendship object or raise exception
        """

        # you should not be able to be friends with yourself
        if profile == self.uprofile:
            raise AddSelfException("Tried to add self as friend")

        try:
            # check if a friendship already exists
            try:
                Friendship.objects.get(requester=self.uprofile, requestee=profile)
            except Friendship.DoesNotExist:
                # check reverse case
                try:
                    Friendship.objects.get(requester=profile, requestee=self.uprofile)
                # ok, we can make friendship, yay!
                except Friendship.DoesNotExist:
                    newfriendship = Friendship(requester=self.uprofile, requestee=profile, confirmed=False)
                    newfriendship.save()
                    return newfriendship
            raise AlreadyExistsException("Already friends")
        except:
            raise

    def confirm(self, profile):
        # in this method we will confirm the friendship and add the profile to the profile's friends
        # and add created time
        """
        Confirm a friend request
        :param profile: the requester of the friendship to confirm
        :return: boolean, True on success, False on failure
        """
        # check if a valid friend request exists
        try:
            relation = Friendship.objects.get(requester=profile, requestee=self.uprofile, confirmed=False)
        except Friendship.DoesNotExist:
            return False

        # check that the friendship is unconfirmed and that the current user is the valid requestee
        if not relation.confirmed and relation.requestee == self.uprofile:
            relation.confirmed = True
            relation.save()
            # need to add friend to profile?
            return True
        else:
            return False

    def delete(self):
        pass

    def return_friendship_list(self, profile):
        """
        Return all of the friendships connected to a given profile
        :param profile: profile who's friends to return
        :return: queryset containing all Friendships for the profile
        """
        # make sure to check uprofile has permission to see the profile's friend list
        return Friendship.objects.all().filter((Q(requestee=profile) | Q(requester=profile)) & Q(confirmed=True))

    def return_pending_requests(self):
        """

        :return: queryset containing all unconfirmed friendships for the current user
        """
        return Friendship.objects.all().filter(requestee=self.uprofile, confirmed=False)

    def filter_friendships(self, qset, refprofile):
        """
        Converts a list of friendships to the relevant profiles
        Called in return_friend_list
        Really should be a private method
        :param qset: queryset of friendship objects
        :param refprofile: the profile that we are referencing the friends from, e.g. return the friend in the friendship
        who is not this profile.  As in, we view a profile's friend list in the UI, we get the friendships, we filter the
        friendships by returning whoever is not the refprofile.  We return refprofile's friends from the queryset returned
        by return_friend_list().
        ... maybe we want to just call this in return_friend_list and return this for that
        :return: list of profile objects corresponding to the friendship objects
        """
        # this long loop makes me wary
        profiles = []
        for friendship in qset:
            if friendship.requestee == refprofile:
                profiles.append(friendship.requester)
            else:
                profiles.append(friendship.requestee)
        return profiles

    def return_friend_list(self, profile):
        """
        Return the friend list for a given profile as a list of profiles
        :param profile: profile to get friend list of
        :return: list of profiles
        """
        return self.filter_friendships(self.return_friendship_list(profile), profile)

def are_friends(profile1, profile2, confirmed=True):
    """
    Test if two users are friends or pending
    :param profile1:
    :param profile2:
    :param confirmed: boolean, if True will only return True if friendship is confirmed
                      if False will only return True if friendship is pending
    :return: boolean, True if friends
    """
    # oh god this is ugly
    try:
        Friendship.objects.get(requester=profile1, requestee=profile2, confirmed=confirmed)
    except Friendship.DoesNotExist:
        try:
            Friendship.objects.get(requester=profile2, requestee=profile1, confirmed=confirmed)
        except Friendship.DoesNotExist:
            return False
    return True

