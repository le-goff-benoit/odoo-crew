import unittest
from quotas import snapshot

class PublicTest(unittest.TestCase):
    def test_missing_is_unknown(self):
        self.assertEqual(snapshot([], 1000), {
            'openai': {'5h': None, 'week': None},
            'anthropic': {'5h': None, 'week': None}})
