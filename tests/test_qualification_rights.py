"""The rights runner must reject missing or ambiguous oracle evidence."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from odoo_qualify_rights import extract


class QualificationRightsEvidenceTest(unittest.TestCase):
    def test_unique_oracle_record_among_server_logs(self):
        self.assertEqual(extract('INFO server started\nQUALIFICATION_RPC={"secure": false}\n',
                                 'QUALIFICATION_RPC='), {'secure': False})

    def test_missing_or_embedded_marker_is_not_evidence(self):
        with self.assertRaises(ValueError):
            extract('INFO copied text QUALIFICATION_RPC={"secure": true}\n', 'QUALIFICATION_RPC=')

    def test_contradictory_records_cannot_be_silently_selected(self):
        with self.assertRaises(ValueError):
            extract('QUALIFICATION_RPC={"secure": false}\nQUALIFICATION_RPC={"secure": true}\n',
                    'QUALIFICATION_RPC=')


if __name__ == '__main__':
    unittest.main()
