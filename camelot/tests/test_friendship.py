from django.test import TestCase
from django.contrib.auth.models import User
from django.test.client import RequestFactory
from django.shortcuts import reverse
from ..controllers.friendcontroller import friendcontroller, are_friends
from ..models import Friendship
from .helperfunctions import complete_add_friends
from ..view.usermgmt import activate_user_no_check
from ..view import friend


class FriendGroupControllerTests(TestCase):

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
            'email': 'user1@test.com',
            'password': 'secret'}

        self.friend2credentials = {
            'username': 'testuser3',
            'email': 'user2@test.com',
            'password': 'secret'}

        self.friend3credentials = {
            'username': 'TeStuSeR4',
            'email': 'user@blah.com',
            'password': 'secret'}

        self.u = User.objects.create_user(**self.credentials)
        self.u.save()
        activate_user_no_check(self.u)

        self.friend = User.objects.create_user(**self.friendcredentials)
        self.friend.save()
        activate_user_no_check(self.friend)

        self.friend2 = User.objects.create_user(**self.friend2credentials)
        self.friend2.save()
        activate_user_no_check(self.friend2)

        self.friend3 = User.objects.create_user(**self.friend3credentials)
        self.friend3.save()
        activate_user_no_check(self.friend3)

        self.friendcontrol = friendcontroller(self.u.id)
        self.otherfriendcontrol = friendcontroller(self.friend.id)
        self.otherfriendcontrol2 = friendcontroller(self.friend2.id)


class FriendshipTests(FriendGroupControllerTests):

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

    def test_deny_friend(self):
        self.friendcontrol.add(self.friend.profile)

        assert self.otherfriendcontrol.remove(self.u.profile)

        self.assertRaises(Friendship.DoesNotExist, Friendship.objects.get, requester=self.friend.profile,
                          requestee=self.u.profile)

    def test_delete_friend(self):
        # try all combinations of requester and requestee

        complete_add_friends(self.friend.id, self.u.id)

        assert self.otherfriendcontrol.remove(self.u.profile)

        self.assertRaises(Friendship.DoesNotExist, Friendship.objects.get, requester=self.friend.profile,
                          requestee=self.u.profile)

        self.assertRaises(Friendship.DoesNotExist, Friendship.objects.get, requester=self.u.profile,
                          requestee=self.friend.profile)

        complete_add_friends(self.friend.id, self.u.id)

        assert self.friendcontrol.remove(self.friend.profile)

        self.assertRaises(Friendship.DoesNotExist, Friendship.objects.get, requester=self.friend.profile,
                          requestee=self.u.profile)

        self.assertRaises(Friendship.DoesNotExist, Friendship.objects.get, requester=self.u.profile,
                          requestee=self.friend.profile)

        complete_add_friends(self.u.id, self.friend.id)

        assert self.friendcontrol.remove(self.friend.profile)

        self.assertRaises(Friendship.DoesNotExist, Friendship.objects.get, requester=self.friend.profile,
                          requestee=self.u.profile)

        self.assertRaises(Friendship.DoesNotExist, Friendship.objects.get, requester=self.u.profile,
                          requestee=self.friend.profile)

        complete_add_friends(self.u.id, self.friend.id)

        assert self.otherfriendcontrol.remove(self.u.profile)

        self.assertRaises(Friendship.DoesNotExist, Friendship.objects.get, requester=self.friend.profile,
                          requestee=self.u.profile)

        self.assertRaises(Friendship.DoesNotExist, Friendship.objects.get, requester=self.u.profile,
                          requestee=self.friend.profile)

    def test_return_friend_list(self):
        # TODO: Expand these unit tests on the train in the morning
        """
        this must be tested more - omg a soothsayer up in here O_O *facepalm*
        ... it's getting late though... for the train
        test who friends are
        """
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

    def test_filter_friends(self):
        pass

    def test_return_friendship_list(self):
        pass

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

    def test_find_friends(self):
        self.u.profile.dname = "test hi"
        self.u.profile.save()
        search1 = "test"
        search2 = "3"
        search3 = "NOT IN USERS"
        search4 = "hi"
        qset = self.friendcontrol.findfriends(search1)
        assert len(qset) == 4
        qset = self.friendcontrol.findfriends(search2)
        assert len(qset) == 1
        qset = self.friendcontrol.findfriends(search3)
        assert len(qset) == 0
        qset = self.friendcontrol.findfriends(search4)
        assert len(qset) == 1


class FriendViewTests(TestCase):

    def setUp(self):
        self.credentials = {
            'username': 'testuser',
            'email': 'user@test.com',
            'password': 'secret'}
        self.u = User.objects.create_user(**self.credentials)
        self.u.save()
        activate_user_no_check(self.u)

        self.credentials2 = {
            'username': 'testuser2',
            'email': 'user2@test.com',
            'password': 'secret'}
        self.u2 = User.objects.create_user(**self.credentials2)
        self.u2.save()
        activate_user_no_check(self.u2)

        self.factory = RequestFactory()

        self.friendcontrol = friendcontroller(self.u.id)

        # login
        response = self.client.post('', self.credentials2, follow=True)

    def test_deny_friend(self):
        self.friendcontrol.add(self.u2.profile)

        request = self.client.get(reverse('remove_friend', kwargs={'userid': self.u.id}))
        request.user = self.u2
        response = friend.delete_friend(request, self.u.id)
        self.assertEqual(response.status_code, 302)

        self.assertRaises(Friendship.DoesNotExist, Friendship.objects.get, requester=self.u.profile,
                          requestee=self.u2.profile)

    def test_delete_friend(self):
        complete_add_friends(self.u.id, self.u2.id)

        request = self.client.get(reverse('remove_friend', kwargs={'userid': self.u.id}))
        request.user = self.u2

        response = friend.delete_friend(request, self.u.id)

        self.assertEqual(response.status_code, 302)
        self.assertRaises(Friendship.DoesNotExist, Friendship.objects.get, requester=self.u.profile,
                          requestee=self.u2.profile)
        self.assertRaises(Friendship.DoesNotExist, Friendship.objects.get, requester=self.u2.profile,
                          requestee=self.u.profile)

        # test the same for the other friend
        complete_add_friends(self.u.id, self.u2.id)

        request = self.client.get(reverse('remove_friend', kwargs={'userid': self.u2.id}))
        request.user = self.u
        response = friend.delete_friend(request, self.u2.id)

        self.assertEqual(response.status_code, 302)
        self.assertRaises(Friendship.DoesNotExist, Friendship.objects.get, requester=self.u.profile,
                          requestee=self.u2.profile)
        self.assertRaises(Friendship.DoesNotExist, Friendship.objects.get, requester=self.u2.profile,
                          requestee=self.u.profile)

    def test_delete_friend_groups_removed(self):
        """
        Test that when we delete a friend, that friend is no longer in any groups
        """
        pass