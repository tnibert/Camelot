from django.test import TestCase
from django.contrib.auth.models import User

class FriendshipTests(TestCase):

    def setUp(self):
        pass

    def test_add_friend(self):
        pass

    def test_confirm_friend(self):
        pass

    def test_delete_friend(self):
        pass

from ..controllers.groupcontroller import groupcontroller
from ..models import FriendGroup

class GroupControllerTests(TestCase):

    def setUp(self):
        # redundant?
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

        self.groupcontrol = groupcontroller(self.u.id)

        self.friend = User.objects.create_user(**self.friendcredentials)
        self.friend.save()

        self.friend2 = User.objects.create_user(**self.friend2credentials)
        self.friend2.save()

        # send login data - these commented lines are for view testing
        #response = self.client.post('', self.credentials, follow=True)

        #self.factory = RequestFactory()

    def test_create_group(self):
        name = "Test New Group"
        newgroup = self.groupcontrol.create(name)
        myquery = FriendGroup.objects.filter(owner=self.u.profile, name=name)
        assert len(myquery) == 1
        assert newgroup == myquery[0]
        #print(myquery[0])

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