from .genericcontroller import genericcontroller
from ..models import Friendship, Profile, FriendGroup
from .utilities import AlreadyExistsException, AddSelfException
from django.db.models import Q
from itertools import chain

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
        # this second clause is probably redundant
        if not relation.confirmed and relation.requestee == self.uprofile:
            relation.confirmed = True
            relation.save()
            # need to add friend to profile?
            return True
        else:
            return False

    def remove(self, profile):
        """
        Delete a friend friendship, also deny friend request
        :param profile: the requester of the friendship to deny
        :return: boolean, True if friendship does not exist anymore
        """
        try:
            relation = Friendship.objects.get(requester=profile, requestee=self.uprofile)
        except Friendship.DoesNotExist:
            # if that doesn't work, try reverse before deciding friendship doesn't exist
            try:
                relation = Friendship.objects.get(requester=self.uprofile, requestee=profile)
            except Friendship.DoesNotExist:
                return True

        status = relation.delete()
        if status[0] == 1:
            return True
        elif status[0] == 0:
            return False

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

    def findfriends(self, searchstr):
        """
        Search for friends by display name and username, filtering out existing friends
        :param searchstr: string to search for
        :return: queryset of profiles
        """
        def _defaultsearch(str):
            return Profile.objects.filter(dname__icontains=str)\
                .union(Profile.objects.filter(user__username__icontains=str))

        def _pgsearch(str):
            # postgres specific search
            # todo: test, maybe create environment with postgres
            return Profile.objects.filter(dname__unaccent__lower__trigram_similar=searchstr)\
                .union(Profile.objects.filter(user__username__unaccent__lower__trigram_similar=str))

        profiles = _defaultsearch(searchstr)
        return profiles


def are_friends(profile1, profile2, confirmed=True):
    """
    Test if two users are friends or pending
    :param profile1:
    :param profile2:
    :param confirmed: boolean, if True will only return True if friendship is confirmed
                      if False will only return True if friendship is pending
    :return: boolean, True if friends
    """
    try:
        Friendship.objects.get(requester=profile1, requestee=profile2, confirmed=confirmed)
    except Friendship.DoesNotExist:
        try:
            Friendship.objects.get(requester=profile2, requestee=profile1, confirmed=confirmed)
        except Friendship.DoesNotExist:
            return False
    return True

