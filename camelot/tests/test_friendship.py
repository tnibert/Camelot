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

        self.u = User.objects.create_user(**self.credentials)
        self.u.save()

        self.groupcontrol = groupcontroller(self.u.id)

        # send login data - these commented lines are for view testing
        #response = self.client.post('', self.credentials, follow=True)

        #self.factory = RequestFactory()

    def test_create_group(self):
        name = "Test Group"
        self.groupcontrol.create(name)
        myquery = FriendGroup.objects.filter(owner=self.u.profile, name=name)
        assert len(myquery) == 1

    def test_create_group_redundant_name(self):
        pass

    def test_delete_group(self):
        pass

    def test_add_member(self):
        pass

    def test_delete_member(self):
        pass