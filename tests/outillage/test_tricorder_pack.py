"""Dedicated runtime profiles, independently of the historical CLI flows."""
import json
from pathlib import Path
import re
import unittest
ROOT=Path(__file__).resolve().parents[2]

class TricorderPackTests(unittest.TestCase):
    def test_six_dedicated_profiles_and_single_shared_contract(self):
        pack=json.loads((ROOT/'tricorder-pack.json').read_text())
        self.assertEqual(pack['version'],'0.3.1')
        self.assertEqual(len(pack['profiles']),6)
        for profile in pack['profiles']:
            text=(ROOT/profile['source']).read_text()
            sections=re.split(r'(?m)^## ([a-zA-Z][a-zA-Z0-9_.-]*)\s*$',text)
            matches=[sections[i+1] for i in range(1,len(sections),2) if sections[i]==profile['section']]
            self.assertEqual(len(matches),1)
            self.assertIn('moteur',sections[0])
            self.assertIn('release/<id>/README.md',sections[0])
            self.assertNotIn('odoo_flow.py',sections[0]+matches[0])
            self.assertNotIn('changelog/',sections[0]+matches[0])
        self.assertTrue(pack['policies']['qa_requires_local_copy'])

if __name__=='__main__':unittest.main()
