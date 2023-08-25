from ..logs import log_exception
from django.test import TestCase
from unittest import skip


class LogTests(TestCase):
    def setUp(self):
        pass

    @skip("requires write permission in /var")
    def test_log_exception(self):
        try:
            1/0
        except Exception as e:
            assert log_exception(__name__, e)

        # check file end
        with open("/var/log/www-data/exceptions.log", 'r') as f:
            lines = f.read().splitlines()
            last_line = lines[-2]
            assert last_line == "    1/0"
