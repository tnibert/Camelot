from django.test import TestCase
from django.contrib.auth.models import User

class FriendGroupTests(TestCase):

    """
    Parent class for friendship and group controller tests so setup code isn't redundant
    """

    def setUp(self):
        self.credentials = {
            'username': 'testuser',
            'email': 'user@test.com',
            'password': 'secret'}

        self.friendcredentials = {
            'username': 'testuser2',
            'email': 'user@test.com',
            'password': 'secret'}

        self.friend2credentials = {
            'username': 'testuser3',
            'email': 'user@test.com',
            'password': 'secret'}

        self.u = User.objects.create_user(**self.credentials)
        self.u.save()

        self.friend = User.objects.create_user(**self.friendcredentials)
        self.friend.save()

        self.friend2 = User.objects.create_user(**self.friend2credentials)
        self.friend2.save()

        self.friendcontrol = friendcontroller(self.u.id)
        self.otherfriendcontrol = friendcontroller(self.friend.id)
        self.otherfriendcontrol2 = friendcontroller(self.friend2.id)

from ..controllers.friendcontroller import friendcontroller, are_friends
from ..models import Friendship

class FriendshipTests(FriendGroupTests):

    """
    Controller tests for friendship
    Must test that both friends have a friend
    """

    def setUp(self):
        super().setUp()

    def test_add_friend(self):
        myquery = Friendship.objects.filter(requester=self.u.profile, requestee=self.friend.profile)
        assert len(myquery) == 0
        self.friendcontrol.add(self.friend.profile)
        myquery = Friendship.objects.filter(requester=self.u.profile, requestee=self.friend.profile)
        assert len(myquery) == 1
        assert myquery[0].confirmed == False

    def test_confirm_friend(self):
        self.friendcontrol.add(self.friend.profile)

        assert self.otherfriendcontrol.confirm(self.u.profile)

        myquery = Friendship.objects.filter(requester=self.u.profile, requestee=self.friend.profile, confirmed=True)
        assert len(myquery) == 1
        # expand this coverage, check that we properly return false

    def test_delete_friend(self):
        pass

    def test_return_friend_list(self):
        # this must be tested more
        self.friendcontrol.add(self.friend.profile)
        assert len(self.friendcontrol.return_friend_list(self.u.profile)) == 0
        self.otherfriendcontrol.confirm(self.u.profile)
        assert len(self.friendcontrol.return_friend_list(self.u.profile)) == 1
        self.friendcontrol.add(self.friend2.profile)
        self.otherfriendcontrol2.confirm(self.u.profile)
        assert len(self.friendcontrol.return_friend_list(self.u.profile)) == 2

        assert len(self.otherfriendcontrol.return_friend_list(self.friend.profile)) == 1

        # make sure other friends each have 1 friend
        assert len(self.friendcontrol.return_friend_list(self.friend.profile)) == 1
        assert len(self.friendcontrol.return_friend_list(self.friend2.profile)) == 1

    def test_return_pending_requests(self):
        assert len(self.friendcontrol.return_pending_requests()) == 0
        self.otherfriendcontrol.add(self.u.profile)
        assert len(self.friendcontrol.return_pending_requests()) == 1
        self.friendcontrol.confirm(self.otherfriendcontrol.uprofile)
        assert len(self.friendcontrol.return_pending_requests()) == 0

    def test_friend_test(self):
        # we start as not friends
        assert not are_friends(self.friend.profile, self.u.profile)
        assert not are_friends(self.u.profile, self.friend.profile)

        # add friends
        self.friendcontrol.add(self.friend.profile)
        self.otherfriendcontrol.confirm(self.u.profile)

        # now we are friends
        assert are_friends(self.friend.profile, self.u.profile)
        assert are_friends(self.u.profile, self.friend.profile)

from ..controllers.groupcontroller import groupcontroller
from ..models import FriendGroup

class GroupControllerTests(FriendGroupTests):

    """
    Controller tests for friendgroups
    """

    def setUp(self):
        super().setUp()
        # send login data - these commented lines are for view testing
        #response = self.client.post('', self.credentials, follow=True)

        #self.factory = RequestFactory()

        self.groupcontrol = groupcontroller(self.u.id)

    def test_create_group(self):
        name = "Test New Group"
        newgroup = self.groupcontrol.create(name)
        myquery = FriendGroup.objects.filter(owner=self.u.profile, name=name)
        assert len(myquery) == 1
        assert newgroup == myquery[0]

    def test_create_group_redundant_name(self):
        pass

    def test_delete_group(self):
        pass

    def test_add_member(self):
        name = "Test Add Member"
        newgroup = self.groupcontrol.create(name)

        # can't add user to group who is not a friend
        assert not self.groupcontrol.add_member(newgroup.id, self.friend.profile)
        assert len(newgroup.members.all()) == 0

        # become friends
        self.friendcontrol.add(self.friend.profile)
        self.otherfriendcontrol.confirm(self.u.profile)

        # now can add to group
        assert self.groupcontrol.add_member(newgroup.id, self.friend.profile)
        assert len(newgroup.members.all()) == 1
        # cannot add user to group twice
        assert not self.groupcontrol.add_member(newgroup.id, self.friend.profile)
        assert len(newgroup.members.all()) == 1

        # can't add other user to group
        assert not self.groupcontrol.add_member(newgroup.id, self.friend2.profile)
        assert len(newgroup.members.all()) == 1

        # become friends
        self.friendcontrol.add(self.friend2.profile)
        self.otherfriendcontrol2.confirm(self.u.profile)

        # now it's all good
        assert self.groupcontrol.add_member(newgroup.id, self.friend2.profile)
        assert len(newgroup.members.all()) == 2

        # add coverage for if we try to add to another user's group

    def test_delete_member(self):
        pass