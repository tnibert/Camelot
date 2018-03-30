from django.test import TestCase

"""
In this file we need to define what our access permissions need to be
and test correct access and access violations

Access types:
Public, All Friends, Groups, Private
public - everyone can view
all friends - all friends can view (DEFAULT)
groups - only group members can view
private - only owner and contributors can view

Album:
If album has no groups, default is all friends.
Contributor can always view album

To validate an album:
Check if accessing user is in album's groups
"""

class test_controller_permissions(TestCase):
    pass

class test_view_permissions(TestCase):
    pass