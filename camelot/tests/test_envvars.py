from django.test import TestCase
from unittest.mock import patch
from ..envvars import load_boolean_from_env

class EnvTests(TestCase):
    def test_load_boolean_false_from_env(self):
        for assignment in ("False", "false", "off", "0", "no"):
            with patch.dict('os.environ', {"mybool": assignment}):
                val = load_boolean_from_env("mybool", True)
                assert val is False

    def test_load_boolean_true_from_env(self):
        for assignment in ("True", "true", "on", "1", "yes"):
            with patch.dict('os.environ', {"mybool": assignment}):
                val = load_boolean_from_env("mybool", False)
                assert val is True

    def test_load_boolean_unassigned_from_env_returns_default(self):
        val = load_boolean_from_env("mybool", True)
        assert val is True

    def test_load_boolean_invalid_from_env_returns_default(self):
        with patch.dict('os.environ', {"mybool": "foo"}):
            val = load_boolean_from_env("mybool", True)
            assert val is True
