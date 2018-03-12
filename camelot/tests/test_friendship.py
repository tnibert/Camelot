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

from ..controllers.friendcontroller import friendcontroller
from ..models import Friendship

class FriendshipTests(FriendGroupTests):

    """
    Controller tests for friendship
    """

    def setUp(self):
        super().setUp()
        self.friendcontrol = friendcontroller(self.u.id)
        self.otherfriendcontrol = friendcontroller(self.friend.id)

    def test_add_friend(self):
        myquery = Friendship.objects.filter(requester=self.u.profile, requestee=self.friend.profile)
        assert len(myquery) == 0
        self.friendcontrol.add(self.friend.profile)
        myquery = Friendship.objects.filter(requester=self.u.profile, requestee=self.friend.profile)
        assert len(myquery) == 1
        assert myquery[0].confirmed == False

    def test_confirm_friend(self):
        self.friendcontrol.add(self.friend.profile)
        #assert len(self.otherfriendcontrol.return_friend_list(self.otherfriendcontrol.uprofile)) == 0
        assert self.otherfriendcontrol.confirm(self.u.profile)
        #assert len(self.otherfriendcontrol.return_friend_list(self.otherfriendcontrol.uprofile)) == 1
        #assert len(self.otherfriendcontrol.return_friend_list(self.friendcontrol.uprofile)) == 1
        myquery = Friendship.objects.filter(requester=self.u.profile, requestee=self.friend.profile, confirmed=True)
        assert len(myquery) == 1

    def test_delete_friend(self):
        pass

    def test_return_friend_list(self):
        pass

    def test_return_pending_requests(self):
        pass

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

        assert self.groupcontrol.add_member(newgroup.id, self.friend.profile)
        assert len(newgroup.members.all()) == 1
        assert not self.groupcontrol.add_member(newgroup.id, self.friend.profile)
        assert len(newgroup.members.all()) == 1

        assert self.groupcontrol.add_member(newgroup.id, self.friend2.profile)
        assert len(newgroup.members.all()) == 2

        # add coverage for if we try to add to another user's group

    def test_delete_member(self):
        pass