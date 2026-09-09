import logging

from psycopg2.errors import CheckViolation

from odoo.tests import tagged
from odoo.tests.common import TransactionCase

_logger = logging.getLogger(__name__)


@tagged("post_install", "-at_install")
class TestQuantity(TransactionCase):
    def test_zero(self):
        record = self.env["lab.qualification"].create({"name": "Zero", "quantity": 0})
        self.env.flush_all()
        self.assertEqual((record.quantity, record.amount), (0, 0))
        _logger.info("QUALIFICATION_PASS zero")

    def test_negative_create(self):
        with self.assertRaises(CheckViolation), self.cr.savepoint():
            self.env["lab.qualification"].create({"name": "Negative", "quantity": -1})
            self.env.flush_all()
        _logger.info("QUALIFICATION_PASS negative_create")

    def test_negative_write(self):
        record = self.env["lab.qualification"].create({"name": "Preserve", "quantity": 3})
        self.env.flush_all()
        with self.assertRaises(CheckViolation), self.cr.savepoint():
            record.write({"quantity": -1})
            self.env.flush_all()
        record.invalidate_recordset()
        self.assertEqual((record.quantity, record.amount), (3, 30))
        _logger.info("QUALIFICATION_PASS negative_write")

    def test_confirmation(self):
        record = self.env["lab.qualification"].create({"name": "Confirm", "quantity": 3})
        self.assertEqual(record.state, "draft")
        record.action_confirm()
        self.env.flush_all()
        record.invalidate_recordset()
        self.assertEqual((record.state, record.amount), ("confirmed", 30))
        _logger.info("QUALIFICATION_PASS confirmation")
