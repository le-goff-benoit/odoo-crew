from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts'))
import odoo_pack as p


class FakeTarget:
    label = 'synthetic'

    def __init__(self):
        self.ids = {}
        self.rows = {}
        self.mutations = []
        self.fail_response = False

    def id_of(self, ref, expected_model=None):
        return self.ids.get(ref)

    def call(self, model, method, *args, **kwargs):
        if model == 'ir.module.module': return [{'latest_version': '19.0.1.0'}]
        if method == 'fields_get': return {'name': {'type': 'char'}, 'parent_id': {'type': 'many2one'}}
        if method == 'read': return [self.rows[args[0][0]]]
        if method == 'load':
            columns, rows = args
            ref = rows[0][0]
            rid = len(self.rows) + 1
            self.ids[ref] = rid
            self.rows[rid] = {'name': rows[0][columns.index('name')]}
            self.mutations.append(('load', ref))
            if self.fail_response:
                self.fail_response = False
                raise ConnectionError('response lost after committed import')
            return {'ids': [rid], 'messages': []}
        if method == 'write':
            self.rows[args[0][0]].update(args[1]); self.mutations.append(('write', args[0]))
            return True
        raise AssertionError((model, method))


class PackTests(unittest.TestCase):
    def setUp(self):
        self.target = FakeTarget()
        self.pack = {'format': 'odoo-pack/1', 'series': '19.0.1.0', 'records': [
            {'model': 'x.synthetic', 'xml_id': 'studio_customization.one', 'values': {'name': 'One'}}]}

    def test_all_records_prevalidated_before_first_write(self):
        self.pack['records'].append({'model': 'x.synthetic', 'xml_id': 'studio_customization.two', 'values': {'missing': 'value'}})
        with self.assertRaises(ValueError): p.apply(self.target, self.pack, False, False)
        self.assertEqual(self.target.mutations, [])

    def test_wrong_series_or_unresolved_ref_is_not_silent(self):
        self.pack['series'] = '18.0.1.0'
        with self.assertRaises(ValueError): p.apply(self.target, self.pack, False, False)
        self.pack['series'] = '19.0.1.0'
        self.pack['records'][0]['values']['parent_id'] = {'unresolved': 'x.synthetic', 'id': 3}
        with self.assertRaises(ValueError): p.apply(self.target, self.pack, False, False)
        self.assertEqual(self.target.mutations, [])

    def test_import_and_second_application_are_idempotent(self):
        p.apply(self.target, self.pack, False, False)
        p.apply(self.target, self.pack, False, False)
        self.assertEqual(self.target.mutations, [('load', 'studio_customization.one')])

    def test_lost_response_after_creation_does_not_duplicate_on_retry(self):
        self.target.fail_response = True
        with self.assertRaises(ConnectionError): p.apply(self.target, self.pack, False, False)
        p.apply(self.target, self.pack, False, False)
        self.assertEqual(len(self.target.rows), 1)
        self.assertEqual(len(self.target.mutations), 1)

    def test_dry_run_has_no_mutation(self):
        p.apply(self.target, self.pack, True, False)
        self.assertEqual(self.target.mutations, [])

    def test_malformed_record_is_refused_before_writes(self):
        self.pack['records'].append({'model': 'ir.model.fields', 'xml_id': 'studio_customization.bad',
                                     'values': {'name': 'x_bad', 'ttype': 'char', 'model_id': 7}})
        with self.assertRaises(ValueError): p.apply(self.target, self.pack, False, False)
        self.assertEqual(self.target.mutations, [])
