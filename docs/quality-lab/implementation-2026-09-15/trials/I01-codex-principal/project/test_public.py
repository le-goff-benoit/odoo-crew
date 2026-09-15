import unittest
from scheduler import ready

class PublicTest(unittest.TestCase):
    def test_independent_pending(self):
        task = dict(id='A', status='pending', proof_current=False, deps=[], reads=[], writes=[])
        self.assertEqual(ready([task], {}), ['A'])
