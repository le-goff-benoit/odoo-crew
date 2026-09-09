"""Independent behavioral oracle: injected only after candidate output is frozen."""
import logging
import unittest
from psycopg2.errors import CheckViolation
from odoo.exceptions import ValidationError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase

_logger = logging.getLogger(__name__)


@tagged("post_install", "-at_install", "delegation_oracle")
class TestDelegationOracle(TransactionCase):
    def _reject(self, operation):
        with unittest.TestCase.assertRaises(self, (CheckViolation, ValidationError)), self.env.cr.savepoint():
            operation()
            self.env.flush_all()

    def test_negative_create_and_write(self):
        model = self.env['lab.qualification']
        self._reject(lambda: model.create({'name': 'oracle negative', 'quantity': 2, 'unit_price': -0.01}))
        record = model.create({'name': 'oracle preserve', 'quantity': 3, 'unit_price': 12})
        self.env.flush_all()
        self._reject(lambda: record.write({'unit_price': -2}))
        record.invalidate_recordset()
        self.assertEqual((record.quantity, record.unit_price, record.amount, record.state), (3, 12, 36, 'draft'))
        _logger.info('DELEGATION_ORACLE_PASS negative_create_and_write')

    def test_free_and_zero_quantity(self):
        model = self.env['lab.qualification']
        free = model.create({'name': 'oracle free', 'quantity': 4, 'unit_price': 0})
        empty = model.create({'name': 'oracle empty', 'quantity': 0, 'unit_price': 11})
        self.env.flush_all()
        self.assertEqual((free.amount, empty.amount), (0, 0))
        self._reject(lambda: empty.write({'unit_price': -1}))
        self._reject(lambda: model.create({'name': 'oracle empty negative', 'quantity': 0, 'unit_price': -1}))
        free.write({'unit_price': 2.5})
        self.env.flush_all()
        self.assertEqual(free.amount, 10)
        _logger.info('DELEGATION_ORACLE_PASS free_and_zero_quantity')

    def test_quantity_amount_and_button(self):
        model = self.env['lab.qualification']
        self._reject(lambda: model.create({'name': 'oracle bad quantity', 'quantity': -1, 'unit_price': 10}))
        record = model.create({'name': 'oracle confirm', 'quantity': 3, 'unit_price': 10})
        record.write({'unit_price': 12})
        self.env.flush_all()
        self.assertEqual(record.amount, 36)
        record.write({'quantity': 4})
        record.action_confirm()
        self.env.flush_all()
        self.assertEqual((record.quantity, record.unit_price, record.amount, record.state), (4, 12, 48, 'confirmed'))
        self._reject(lambda: record.write({'quantity': -2}))
        record.invalidate_recordset()
        self.assertEqual((record.quantity, record.amount, record.state), (4, 48, 'confirmed'))
        _logger.info('DELEGATION_ORACLE_PASS quantity_amount_and_button')

    def test_batch_atomicity(self):
        model = self.env['lab.qualification']
        self._reject(lambda: model.create([
            {'name': 'oracle batch valid', 'quantity': 3, 'unit_price': 10},
            {'name': 'oracle batch invalid', 'quantity': 2, 'unit_price': -2},
        ]))
        self.assertFalse(model.search([('name', 'in', ['oracle batch valid', 'oracle batch invalid'])]))
        records = model.create([
            {'name': 'oracle multiwrite a', 'quantity': 3, 'unit_price': 5},
            {'name': 'oracle multiwrite b', 'quantity': 2, 'unit_price': 8},
        ])
        self.env.flush_all()
        before = [(r.quantity, r.unit_price, r.amount) for r in records]
        self._reject(lambda: records.write({'unit_price': -0.5}))
        records.invalidate_recordset()
        self.assertEqual([(r.quantity, r.unit_price, r.amount) for r in records], before)
        _logger.info('DELEGATION_ORACLE_PASS batch_atomicity')

    def test_import_load(self):
        model = self.env['lab.qualification']
        bad = model.load(['name', 'quantity', 'unit_price'], [
            ['oracle import valid row', '2', '6'],
            ['oracle import negative row', '2', '-1'],
        ])
        self.assertTrue(any(m.get('type') == 'error' for m in bad.get('messages', [])))
        self.assertFalse(model.search([('name', 'in', ['oracle import valid row', 'oracle import negative row'])]))
        good = model.load(['name', 'quantity', 'unit_price'], [['oracle import free', '2', '0']])
        self.assertFalse(any(m.get('type') == 'error' for m in good.get('messages', [])))
        self.assertTrue(good.get('ids'))
        self.env.flush_all()
        self.assertEqual(model.browse(good['ids']).amount, 0)
        _logger.info('DELEGATION_ORACLE_PASS import_load')
