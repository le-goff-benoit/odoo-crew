"""Memory during work, raw document exceptions and source/receipt invalidation."""
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
import json
from pathlib import Path
import sys
import tempfile
import unittest
import zipfile
import subprocess

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts'))
import odoo_context as context
import odoo_documents as documents
import odoo_knowledge as knowledge
import odoo_plan as plan
import odoo_source_index as source_index
import odoo_bench_knowledge as bench
from tests.pilotage import test_odoo_release_plan as fixtures


def docx(path, text):
    with zipfile.ZipFile(path, 'w') as archive:
        archive.writestr('word/document.xml', '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body><w:p><w:r><w:t>' + text + '</w:t></w:r></w:p></w:body></w:document>')


def xlsx(path, text):
    with zipfile.ZipFile(path, 'w') as archive:
        archive.writestr('xl/workbook.xml', '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets><sheet name="Livraison" sheetId="1" r:id="rId1"/></sheets></workbook>')
        archive.writestr('xl/_rels/workbook.xml.rels', '<Relationships><Relationship Id="rId1" Target="worksheets/sheet1.xml"/></Relationships>')
        archive.writestr('xl/worksheets/sheet1.xml', '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData><row r="9"><c r="B9" t="inlineStr"><is><t>' + text + '</t></is></c></row></sheetData></worksheet>')


class KnowledgeTests(unittest.TestCase):
    setUp = fixtures.ReleasePlanTests.setUp
    task = fixtures.ReleasePlanTests.task
    init = fixtures.ReleasePlanTests.init
    proof = fixtures.ReleasePlanTests.proof
    finish_a = fixtures.ReleasePlanTests.finish_a

    def row(self, identifier='K1', **extra):
        return {'schema': 1, 'id': identifier, 'kind': 'discovery', 'state': 'proposed',
                'statement': 'Les inter-sociétés sont exclues.', 'author': 'analyste', 'scope': [],
                'sources': [documents.reference(self.root, 'request.md')], **extra}

    def test_document_only_exception_and_citation_survive_context(self):
        path = self.root / 'regles.xlsx'; xlsx(path, 'Exception : ne jamais regrouper les livraisons inter-sociétés.')
        before = path.read_bytes()
        documents.register(self.root, 'regles.xlsx', 'regles', '1')
        result = context.context(self.root, 'livraisons')
        self.assertIn('inter-sociétés', result['text']); self.assertIn('Livraison!B9', result['text'])
        self.assertNotIn('DOCUMENTS.json · L', result['text'])
        self.assertTrue(all(r['start_line'] is None for r in result['sections'] if r['path'].endswith('DOCUMENTS.json')))
        self.assertEqual(path.read_bytes(), before)
        self.assertFalse((self.root / '.odoo-agents/DECISIONS.json').exists())
        context.verify_context(result, self.root)
        xlsx(path, 'Nouvelle règle à arbitrer')
        with self.assertRaises(ValueError): context.verify_context(result, self.root)
        self.assertNotIn('inter-sociétés', documents.render(self.root))
        self.assertEqual(documents.catalogue(self.root)[0]['freshness'], 'stale')

    def test_docx_original_version_and_manual_image(self):
        docx(self.root / 'piece.docx', 'Exception : les factures comptabilisées restent figées.')
        documents.register(self.root, 'piece.docx', 'piece', '1', 'historical')
        row = documents.catalogue(self.root)[0]
        self.assertEqual(row['status'], 'historical'); self.assertEqual(row['chunks'][0]['location'], 'paragraphe 1')
        documents.register(self.root, 'piece.docx', 'piece', '1', 'historical')
        docx(self.root / 'piece.docx', 'AUTRE TEXTE')
        with self.assertRaises(ValueError): documents.register(self.root, 'piece.docx', 'piece', '1')
        (self.root / 'image.png').write_bytes(b'synthetic-image')
        documents.register(self.root, 'image.png', 'image', '1')
        self.assertEqual(documents.catalogue(self.root)[1]['extraction_status'], 'manual_read_required')

    def test_outside_symlink_and_tampered_extraction_refused(self):
        with tempfile.TemporaryDirectory() as outside:
            target = Path(outside) / 'secret.txt'; target.write_text('NE PAS LIRE')
            (self.root / 'lien.txt').symlink_to(target)
            with self.assertRaises(ValueError): documents.register(self.root, 'lien.txt', 'bad', '1')
        documents.register(self.root, 'request.md', 'request', '1')
        path = self.root / '.odoo-agents/DOCUMENTS.json'; data = documents.read_json(path)
        data['documents'][0]['chunks'][0]['text'] = 'RÈGLE INVENTÉE'; documents.atomic(path, data)
        self.assertNotIn('RÈGLE INVENTÉE', documents.render(self.root))

    def test_live_contribution_invalidates_reading_and_idempotent_publication(self):
        first = knowledge.brief(self.root, 'test', 'B', 'developer')
        row = self.row()
        path = knowledge.publish(self.root, 'test', row)
        knowledge.publish(self.root, 'test', row)
        self.assertEqual(len(list(path.parent.glob('*.json'))), 1)
        with self.assertRaises(ValueError): knowledge.verify_brief(self.root, first)
        second = knowledge.brief(self.root, 'test', 'B', 'developer')
        self.assertIn('inter-sociétés', second['text']); self.assertIn('proposed', second['text'])
        knowledge.verify_brief(self.root, second)
        with self.assertRaises(ValueError): knowledge.publish(self.root, 'test', dict(row, statement='AUTRE'))

    def test_concurrent_publications_preserved(self):
        with ThreadPoolExecutor(max_workers=4) as pool:
            list(pool.map(lambda i: knowledge.publish(self.root, 'test', self.row('K' + str(i))), range(8)))
        self.assertEqual(len(knowledge.contributions(self.root)), 8)

    def test_stale_successor_never_resurrects_old_rule(self):
        knowledge.publish(self.root, 'test', self.row())
        (self.root / 'review.md').write_text('Arbitrage : exception maintenue')
        successor = self.row('K2', state='accepted', reviewed_by='Alice',
                             review=documents.reference(self.root, 'review.md'), supersedes='K1')
        knowledge.publish(self.root, 'test', successor)
        with self.assertRaises(ValueError): knowledge.publish(self.root, 'test', dict(successor, id='K3'))
        (self.root / 'review.md').write_text('Arbitrage changé')
        rows = knowledge.contributions(self.root)
        self.assertFalse(rows[0]['current']); self.assertEqual(rows[1]['freshness'], 'stale')
        self.assertNotIn('inter-sociétés', knowledge.brief(self.root, 'test')['text'])

    def test_receipt_shared_then_deferred_not_an_acquired_feature(self):
        self.init(); self.finish_a()
        acquired = knowledge.snapshot(self.root, 'test')['receipts'][0]
        self.assertEqual(acquired['state'], 'validated'); self.assertTrue(acquired['text'])
        row = self.row(kind='implementation', state='accepted', task='A',
                       reviewed_by='QA', review=documents.reference(self.root, 'acceptance.md'),
                       receipt_sha256=acquired['result_sha256'])
        knowledge.publish(self.root, 'test', row)
        self.assertIn('preuve de réception', knowledge.brief(self.root, 'test', 'B')['text'])
        plan.mutate(self.release, 'defer', 'A', reason='Report demandé')
        self.assertEqual(knowledge.contributions(self.root)[0]['freshness'], 'stale')
        self.assertEqual(knowledge.snapshot(self.root, 'test')['receipts'][0]['text'], '')

    def test_local_receipt_cannot_prove_deployment(self):
        row = self.row(kind='deployment', state='accepted', reviewed_by='QA',
                       review=documents.reference(self.root, 'request.md'))
        with self.assertRaises((ValueError, KeyError)): knowledge.publish(self.root, 'test', row)

    def test_plan_requires_fresh_memory_at_receipt(self):
        self.definition['shared_memory'] = True; self.init()
        launched = plan.mutate(self.release, 'start', 'A')
        self.assertIn('Mémoire partagée', launched)
        statefile = Path(launched.splitlines()[0]); state = json.loads(statefile.read_text())
        state['status'] = 'complete'; statefile.write_text(json.dumps(state))
        for name in ('acceptance.md', 'memory.md'): (self.root / name).write_text('Résultat vérifié, exception conservée.')
        reading = knowledge.brief(self.root, 'test', 'A')
        documents.atomic(self.root / 'read.json', reading)
        knowledge.publish(self.root, 'test', self.row())
        args = dict(proof=self.proof(), acceptance='acceptance.md', memory='memory.md')
        with self.assertRaises(ValueError): plan.mutate(self.release, 'finish', 'A', **args)
        with self.assertRaises(ValueError): plan.mutate(self.release, 'finish', 'A', knowledge='read.json', **args)
        documents.atomic(self.root / 'read.json', knowledge.brief(self.root, 'test', 'A'))
        plan.mutate(self.release, 'finish', 'A', knowledge='read.json', **args)
        self.assertEqual(knowledge.snapshot(self.root, 'test')['receipts'][0]['state'], 'validated')
        decision = self.row('D1', kind='decision', state='accepted', reviewed_by='Chef de projet',
                            review=documents.reference(self.root, 'acceptance.md'),
                            affects_tasks=['A'], impact_reason='La règle modifie le résultat de A')
        knowledge.publish(self.root, 'test', decision)
        current, _ = plan.read(self.release)
        self.assertEqual(plan.statuses(current, self.root)['A'][0], 'stale')
        self.assertEqual(knowledge.snapshot(self.root, 'test')['receipts'][0]['text'], '')

    def test_document_lexical_accents_and_plural_do_not_hide_exception(self):
        path = self.root / 'regles.xlsx'; xlsx(path, 'Les livraisons inter-sociétés ne doivent jamais être regroupées.')
        documents.register(self.root, 'regles.xlsx', 'regles', '1')
        for query in ('societe', 'société', 'sociétés'):
            self.assertIn('inter-sociétés', context.context(self.root, query)['text'])

    def test_release_context_cannot_omit_shared_memory(self):
        knowledge.publish(self.root, 'test', self.row())
        result = context.context(self.root, 'sans rapport', 1000, 'test', 'B', 'tester')
        self.assertIn('inter-sociétés', result['text'])
        context.verify_context(result, self.root)
        (self.root / 'request.md').write_text('Source changée')
        with self.assertRaises(ValueError): context.verify_context(result, self.root)

    def test_source_index_exact_series_custom_and_new_files(self):
        (self.root / '.odoo-agents').mkdir(exist_ok=True)
        (self.root / '.odoo-agents/config').write_text('series = 18.0\n')
        library = self.root / 'sources'
        for series in ('18.0', '19.0'):
            folder = library / series / 'addons/stock'; folder.mkdir(parents=True)
            (folder / '__manifest__.py').write_text("{'name':'stock'}")
            (folder / 'model.py').write_text("class Picking:\n    _name = 'stock.picking'\n    code = fields.Char()\n    def action_" + series.replace('.', '_') + "(self): pass\n")
        (self.root / 'a/__manifest__.py').write_text("{'name':'a','version':'18.0.1.0.0'}")
        result = source_index.build(self.root, ['stock'], library, self.root / 'cache')
        self.assertEqual(result['series'], '18.0')
        symbols = result['layers'][0]['symbols']
        self.assertTrue(any(s['name'] == 'action_18_0' for s in symbols))
        self.assertFalse(any(s['name'] == 'action_19_0' for s in symbols))
        self.assertEqual(result['layers'][-1]['modules'], ['a'])
        source_index.verify(result)
        (library / '18.0/addons/stock/new.py').write_text('x=1')
        with self.assertRaises(ValueError): source_index.verify(result)
        (self.root / '.odoo-agents/config').write_text('series = 17.0\n')
        with self.assertRaises(ValueError): source_index.build(self.root, ['stock'], library)

    def test_consolidation_frozen_and_stale_sources_refused(self):
        knowledge.publish(self.root, 'test', self.row())
        value = knowledge.consolidate(self.root, 'test')
        self.assertEqual(value['snapshot']['contributions'][0]['statement'], self.row()['statement'])
        (self.root / 'request.md').write_text('Source modifiée')
        with self.assertRaises(ValueError): knowledge.consolidate(self.root, 'test')
        with self.assertRaises(ValueError): knowledge.verify_brief(self.root, knowledge.brief(self.root, 'test'))
        (self.release / 'closure.json').write_text('{}')
        with self.assertRaisesRegex(ValueError, 'scellée'): knowledge.consolidate(self.root, 'test')

    def test_native_oracle_accepts_positive_and_kills_critical_mutations(self):
        for name, case in bench.CASES.items():
            value = {'current_rule': case['current_rule'], 'proposal_confirmed': False,
                     'deployment_verified': False, 'task_deferred': name == 'K06',
                     'references': [{'path': case['file'], 'location': case['location'], 'quote': case['exception']}],
                     'explanation': 'Règle source conservée ; proposition non arbitrée.'}
            self.assertEqual(bench.judge(value, name), [])
            for key, wrong in [('current_rule', 'no_exception'), ('proposal_confirmed', True),
                               ('deployment_verified', True), ('references', [])]:
                self.assertTrue(bench.judge(dict(value, **{key: wrong}), name))

    def test_missing_verify_file_has_actionable_cli_error(self):
        result = subprocess.run([sys.executable, str(Path(knowledge.__file__)), 'verify', str(self.root)],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn('--file requis', result.stderr); self.assertNotIn('Traceback', result.stderr)

    def test_decision_exceptions_and_open_questions_are_shared(self):
        documents.atomic(self.root / '.odoo-agents/DECISIONS.json', {'schema': 1,
            'decisions': [{'id': 'D1', 'status': 'confirmed', 'statement': 'Regrouper par partenaire',
                           'exceptions': ['Ne pas mélanger les sociétés'], 'scope': ['stock.picking'],
                           'sources': [documents.reference(self.root, 'request.md')], 'confirmed_by': 'Alice',
                           'implementation': {'status': 'not_started'}}],
            'questions': [{'id': 'Q1', 'status': 'open', 'question': 'Quelle date de référence ?',
                           'source': documents.reference(self.root, 'request.md')}]})
        text = knowledge.brief(self.root, 'test')['text']
        self.assertIn('Ne pas mélanger les sociétés', text); self.assertIn('Quelle date de référence', text)
        self.assertIn('not_started', text)


if __name__ == '__main__':
    unittest.main()
