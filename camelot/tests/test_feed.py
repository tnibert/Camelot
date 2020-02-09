from django.test import TestCase
from .mocks import profilecontrolmock
from ..friendfeed import generate_feed


class FeedTests(TestCase):
    def test_generate_feed(self):
        pcontrol = profilecontrolmock()
        testfeed = generate_feed(pcontrol)

        assert len(testfeed) == 5
