from django.test import TestCase
from django.contrib.auth.models import User
from django.shortcuts import reverse
from .test_friendship import FriendGroupControllerTests
from ..controllers.groupcontroller import groupcontroller, is_in_group
from .helperfunctions import complete_add_friends
from ..models import FriendGroup

class GroupControllerTests(FriendGroupControllerTests):

    """
    Controller tests for friendgroups
    """

    def setUp(self):
        super().setUp()
        # send login data - these commented lines are for view testing
        #response = self.client.post('', self.credentials, follow=True)

        #self.factory = RequestFactory()

        self.groupcontrol = groupcontroller(self.u.id)
        self.groupcontrol2 = groupcontroller(self.friend.id)

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

    def test_are_friends_check(self):
        pass

    def test_return_groups(self):
        """
        Every user should be able to access another user's groups
        because this is how permissions are determined
        """
        # create a group for first user
        name1 = "Test New Group 1"
        newgroup1 = self.groupcontrol.create(name1)
        # will return self.u's groups
        ret1 = self.groupcontrol.return_groups()

        assert len(ret1) == 1
        assert ret1[0] == newgroup1

        # create a group for second user
        name2 = "Test New Group 2"
        newgroup2 = self.groupcontrol2.create(name2)
        # will return self.friend's groups
        ret2 = self.groupcontrol.return_groups(self.friend.profile)
        assert len(ret2) == 1
        assert ret2[0] == newgroup2

        # create a second group for self.friend
        name3 = "Test New Group 3"
        newgroup3 = self.groupcontrol2.create(name3)

        # self.u will access
        ret3 = self.groupcontrol.return_groups(self.friend.profile)

        assert len(ret3) == 2
        assert ret3[0] == newgroup2
        assert ret3[1] == newgroup3

        # todo: test none case

    def test_is_in_group(self):
        """
        Test utility to check if a profile is in a given group
        Before adding to group return false
        After return true
        """
        name = "Test in group"
        newgroup = self.groupcontrol.create(name)
        assert not is_in_group(newgroup, self.friend.profile)
        complete_add_friends(self.u.id, self.friend.id)
        self.groupcontrol.add_member(newgroup.id, self.friend.profile)
        assert is_in_group(newgroup, self.friend.profile)


from django.test.client import RequestFactory
from ..view.group import *

class GroupViewTests(TestCase):
    def setUp(self):
        # this is identical for the setup to albumviewtests, need to share code
        self.credentials = {
            'username': 'testuser',
            'email': 'user@test.com',
            'password': 'secret'}
        self.u = User.objects.create_user(**self.credentials)
        self.u.save()

        self.credentials = {
            'username': 'testuser2',
            'email': 'user2@test.com',
            'password': 'secret'}
        self.u2 = User.objects.create_user(**self.credentials)
        self.u2.save()

        # send login data
        #response = self.client.post('', self.credentials, follow=True)

        self.factory = RequestFactory()

    def test_manage_groups_view(self):
        """
        should return 200 when we request manage_groups view as logged in user
        TODO: need to figure out how to test for non logged in user
        TODO: test that a user can't get another user's pro
        """
        request = self.factory.get(reverse("manage_groups"))
        request.user = self.u
        request.session = {}

        #response = manage_groups(request)

        #self.assertEqual(response.status_code, 302)

        # log in
        response = self.client.post('', self.credentials, follow=True)

        response = manage_groups(request)

        # now that we are logged in, success
        self.assertEqual(response.status_code, 200)