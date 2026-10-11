import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from src import core as c


class CloudAuthTests(unittest.TestCase):
    def test_private_reviewer_bootstrap_and_recreation(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(c, 'STORE', Path(directory)), patch.dict(os.environ, {'REVIEWER_IDENTITY': 'demo-reviewer', 'REVIEWER_PASSWORD': 'private-demo-password'}):
            self.assertTrue(c.configured())
            self.assertTrue(c.login('demo-reviewer', 'private-demo-password'))
            self.assertFalse(c.login('visitor', 'private-demo-password'))
            with self.assertRaises(ValueError):
                c.setup('visitor', 'another-long-password')
            self.assertTrue(c.configured())
            (Path(directory) / 'reviews.sqlite').unlink()
            self.assertTrue(c.configured())
            self.assertTrue(c.login('demo-reviewer', 'private-demo-password'))

    def test_partial_secrets_fail_closed(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(c, 'STORE', Path(directory)), patch.dict(os.environ, {'REVIEWER_IDENTITY': 'demo-reviewer', 'REVIEWER_PASSWORD': ''}):
            with self.assertRaises(ValueError):
                c.configured()
