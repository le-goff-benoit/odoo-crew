import contextlib
import io
import json
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
    def test_recent_entries_use_dates_when_newer_work_is_prepended(self):
        entries = ['## 2026-09-12 — Incident de livraison\nVérifier le build.',
                   '## 2026-09-11 — Ancien plan\nPréparer le travail.']
        text = b.journal_summary(entries, 1, False)
        self.assertIn(entries[0], text)
        self.assertNotIn(entries[1], text)

    def test_mixed_journal_keeps_recent_facts_and_older_lessons(self):
        entries = ['## 2026-08-30 — Correction\nCorrection récente.',
                   '## 2026-08-20 — Archive\n**Appris** : préserver les données.',
                   '## 2026-08-31 — Déploiement\nRésultat observé.',
                   '## 2026-08-21 — Plan\nPlan ancien.']
        text = b.journal_summary(entries, 2, False)
        self.assertIn(entries[0], text)
        self.assertIn(entries[2], text)
        self.assertNotIn(entries[3], text)
        self.assertIn('préserver les données.', text)

    def test_full_journal_and_same_day_preserve_source_order(self):
        entries = ['## 2026-09-12 — Premier\nA', '## 2026-09-11 — Archive\nB',
                   '## 2026-09-12 — Second\nC']
        full = b.journal_summary(entries, 1, True)
        self.assertLess(full.index(entries[0]), full.index(entries[1]))
        self.assertLess(full.index(entries[1]), full.index(entries[2]))
        recent = b.journal_summary(entries, 2, False)
        self.assertLess(recent.index(entries[0]), recent.index(entries[2]))
        one = b.journal_summary(entries, 1, False)
        self.assertIn('2026-09-12 — Premier', one)
        self.assertNotIn(entries[0], one)
        self.assertIn('ordre intrajournalier inconnu', one)

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


class TargetedBriefingTests(unittest.TestCase):
    def test_targeted_memory_keeps_exception_and_provenance_without_full_archive(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            metadata = root / '.odoo-agents'
            metadata.mkdir()
            (metadata / 'config').write_text('series = 18.0\n')
            (metadata / 'PROJECT.md').write_text(
                '# Projet synthétique\n## Documentation archivée\n' + 'Ancien catalogue. ' * 700
                + '\n## Livraison\nLivrer au contact retenu.\n### Exception\nSauf refus du destinataire.\n')
            output = root / 'context.json'
            stdout, stderr = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr), patch.object(b, 'run', return_value=''):
                result = b.main(['briefing', str(root), '--offline', '--query', 'livraison',
                                 '--budget', '1800', '--context-output', str(output)])
            self.assertEqual(result, 0)
            self.assertIn('Sauf refus du destinataire.', stdout.getvalue())
            self.assertNotIn('Ancien catalogue.', stdout.getvalue())
            self.assertIn('18.0', stdout.getvalue())
            record = json.loads(output.read_text())
            self.assertIn('.odoo-agents/PROJECT.md', record['catalog_paths'])
            self.assertTrue(any(not section['included'] for section in record['sections']))
            self.assertLessEqual(record['actual_characters'], 1800)

    def test_full_archive_and_targeted_mode_are_not_silently_combined(self):
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as error:
            b.main(['briefing', '/tmp', '--query', 'livraison', '--full-journal'])
        self.assertEqual(error.exception.code, 2)
