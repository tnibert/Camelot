from django.test import TestCase

"""
In this file we need to define what our access permissions need to be
and test correct access and access violations

Default groups:
Public, All Friends, Private
We need to prevent user modification of these groups

Album:
If album has no groups, default is all friends.  Default groups are exclusive.

To validate an album:
Check if accessing user is in album's groups
"""

class test_controller_permissions(TestCase):
    pass

class test_view_permissions(TestCase):
    pass