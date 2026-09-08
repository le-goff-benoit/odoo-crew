from odoo.tests.common import TransactionCase, tagged
from odoo.service.model import call_kw
from . import pack_driver


class EnvTarget(pack_driver.Target):
    """Même interface que le transport, exécutée dans la transaction Odoo du test."""
    def __init__(self, env):
        self.env = env
        self.label = 'synthetic ORM oracle'

    def call(self, model, method, *args, allow_write=False, **kwargs):
        return call_kw(self.env[model], method, list(args), kwargs)


@tagged('post_install', '-at_install')
class TestPackContract(TransactionCase):
    def setUp(self):
        super().setUp()
        self.target = EnvTarget(self.env)
        self.pack = {'format': 'odoo-pack/1', 'series': '19.0', 'records': [
            {'model': 'res.partner', 'xml_id': 'studio_customization.quality_contact',
             'values': {'name': 'Quality synthetic contact', 'email': False}}]}

    def test_import_has_identity_and_second_apply_is_unchanged(self):
        pack_driver.apply(self.target, self.pack, False, False)
        rid = self.target.id_of('studio_customization.quality_contact')
        record = self.env['res.partner'].browse(rid)
        metadata = self.env['ir.model.data'].search([('model', '=', 'res.partner'), ('res_id', '=', rid), ('module', '=', 'studio_customization')])
        self.assertEqual(len(metadata), 1)
        if 'studio' in metadata._fields:
            self.assertTrue(metadata.studio)
        self.assertTrue(metadata.noupdate)
        self.assertEqual(record.name, 'Quality synthetic contact')
        self.assertFalse(record.email)
        before = record.write_date
        pack_driver.apply(self.target, self.pack, False, False)
        self.assertEqual(self.target.id_of('studio_customization.quality_contact'), rid)
        self.assertEqual(record.write_date, before)

    def test_unknown_field_rejected_before_any_creation(self):
        self.pack['records'].append({'model': 'res.partner', 'xml_id': 'studio_customization.bad',
                                     'values': {'unknown_quality_column': 'bad'}})
        with self.assertRaises(ValueError):
            pack_driver.apply(self.target, self.pack, False, False)
        self.assertIsNone(self.target.id_of('studio_customization.quality_contact'))

    def test_failed_import_does_not_leave_xmlid_or_row(self):
        # An invalid parent ID fails import conversion in the same RPC transaction.
        vals = {'name': 'Invalid synthetic contact', 'parent_id': 99999999}
        meta = self.target.call('res.partner', 'fields_get', attributes=['type'])
        with self.assertRaises(ValueError):
            pack_driver.create_named(self.target, 'res.partner', 'studio_customization.bad_load', vals, meta, False)
        self.assertIsNone(self.target.id_of('studio_customization.bad_load'))
        self.assertFalse(self.env['res.partner'].search([('name', '=', 'Invalid synthetic contact')]))

    def test_new_model_field_and_record_dependency_order(self):
        self.pack['records'] = [
            {'model': 'x_quality_dynamic', 'xml_id': 'studio_customization.dynamic_row',
             'values': {'x_name': 'Synthetic', 'x_quality_title': 'Proof'}},
            {'model': 'ir.model.fields', 'xml_id': 'studio_customization.dynamic_field',
             'values': {'model_id': {'ref': 'studio_customization.dynamic_model'},
                        'name': 'x_quality_title', 'field_description': 'Quality title', 'ttype': 'char'}},
            {'model': 'ir.model.fields', 'xml_id': 'studio_customization.dynamic_name',
             'values': {'model_id': {'ref': 'studio_customization.dynamic_model'},
                        'name': 'x_name', 'field_description': 'Name', 'ttype': 'char'}},
            {'model': 'ir.model', 'xml_id': 'studio_customization.dynamic_model',
             'values': {'name': 'Quality dynamic', 'model': 'x_quality_dynamic'}},
        ]
        pack_driver.apply(self.target, self.pack, True, False)
        self.assertIsNone(self.target.id_of('studio_customization.dynamic_model'))
        pack_driver.apply(self.target, self.pack, False, False)
        pack_driver.apply(self.target, self.pack, False, False)
        row = self.env['x_quality_dynamic'].browse(self.target.id_of('studio_customization.dynamic_row'))
        self.assertEqual(row.x_quality_title, 'Proof')
