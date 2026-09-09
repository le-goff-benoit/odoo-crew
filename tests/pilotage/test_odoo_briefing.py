import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('briefing', ROOT / 'scripts/odoo_briefing.py')
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)


class BriefingTests(unittest.TestCase):
    def test_shared_lessons_loaded_from_reference_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            reference = root / 'docs/reference'
            reference.mkdir(parents=True)
            (reference / 'LESSONS.md').write_text(
                '### L1 — Préserver les décisions\n**Portée** : universelle\n'
                '**Règle** : Conserver les exceptions du client.\n'
                '### L2 — Série suivante\n**Portée** : série >= 19.0\n'
                '**Règle** : Réserver cette règle à la série suivante.\n')
            with patch.object(b, 'HOME', root):
                lines = b.lessons('18.0')
            self.assertEqual(len(lines), 1)
            self.assertIn('Conserver les exceptions du client.', lines[0])

    def test_multiple_learnings_keep_exceptions(self):
        exception = 'Les partenaires sont autorisés ' + 'selon le dossier ' * 25 + 'SAUF si le contact de livraison refuse.'
        entries = ['## 2026-09-08 — Décision\n**Appris** : première règle\n**Fait** : vérifié\n**Appris** : ' + exception]
        actual = '\n'.join(b.learned_lines(entries))
        self.assertIn('première règle', actual)
        self.assertIn('SAUF si le contact de livraison refuse.', actual)
        self.assertNotIn('**Fait**', actual)

    def test_zero_journal_still_preserves_all_learnings(self):
        entries = ['## 2026-09-08 — Ancien\n**Appris** : règle A']
        text = b.journal_summary(entries, 0, False)
        self.assertNotIn('## 2026-09-08 — Ancien\n', text)
        self.assertIn('règle A', text)
        self.assertIn('les 0 dernières', text)

    def test_recent_truncated_entry_does_not_drop_learning(self):
        entry = '## 2026-09-08 — Longue\n' + 'détail ' * 400 + '\n**Appris** : exception essentielle'
        text = b.journal_summary([entry], 3, False)
        self.assertIn('exception essentielle', text)
        self.assertIn('entrée tronquée', text)

    def test_negative_count_refused(self):
        with self.assertRaises(ValueError):
            b.journal_summary([], -1, False)

    def test_project_without_generated_marker_is_not_empty(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'PROJECT.md'
            path.write_text('## Décisions actées\nLe contact de livraison fait foi.')
            self.assertIn('Le contact de livraison fait foi.', b.hand_written(path))
