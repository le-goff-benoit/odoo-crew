from psycopg2.errors import CheckViolation

from odoo import SUPERUSER_ID
from odoo.tests import tagged
from odoo.tools import mute_logger

from .common import LabQualificationCommon


@tagged("post_install", "-at_install")
class TestConfirmation(LabQualificationCommon):
    def test_draft_zero_explicit_and_default(self):
        """AC01: zero remains a valid preparation quantity, including its default."""
        explicit = self.Qualification.create({"name": "Explicit zero", "quantity": 0})
        default = self.Qualification.create({"name": "Default zero"})
        self.assert_record_values(explicit, "draft", 0, 0)
        self.assert_record_values(default, "draft", 0, 0)

    def test_draft_write_zero(self):
        """AC01: a prepared positive line may return to zero."""
        record = self.Qualification.create({"name": "Draft zero", "quantity": 3})
        record.write({"quantity": 0})
        self.assert_record_values(record, "draft", 0, 0)

    def test_positive_boundary_confirmation(self):
        """AC02/AC09: an ordinary internal user can confirm quantity one."""
        self.assertNotEqual(self.Qualification.env.uid, SUPERUSER_ID)
        self.assertFalse(self.Qualification.env.su)
        self.assertTrue(self.internal_user.has_group("base.group_user"))
        record = self.Qualification.create({"name": "Boundary", "quantity": 1})
        record.action_confirm()
        self.assert_record_values(record, "confirmed", 1, 10)

    def test_zero_confirmation_rejected(self):
        """AC03/AC09: failed confirmation preserves the internal user's draft."""
        self.assertFalse(self.Qualification.env.su)
        record = self.Qualification.create({"name": "Zero confirmation", "quantity": 0})
        self.env.flush_all()
        with self.assertRaises(CheckViolation), self.cr.savepoint(), mute_logger("odoo.sql_db"):
            record.action_confirm()
            self.env.flush_all()
        self.assert_record_values(record, "draft", 0, 0)

    def test_mixed_confirmation_atomic(self):
        """AC04: the positive first line is rolled back with the invalid second line."""
        records = self.Qualification.create([
            {"name": "Positive first", "quantity": 3},
            {"name": "Zero second", "quantity": 0},
        ])
        self.env.flush_all()
        self.assertEqual(records.mapped("quantity"), [3, 0])
        with self.assertRaises(CheckViolation), self.cr.savepoint(), mute_logger("odoo.sql_db"):
            records.action_confirm()
            self.env.flush_all()
        self.assert_record_values(records[0], "draft", 3, 30)
        self.assert_record_values(records[1], "draft", 0, 0)

    def test_create_confirmed_zero_rejected(self):
        """AC05: direct creation cannot persist a zero confirmed line."""
        count = self.Qualification.search_count([])
        with self.assertRaises(CheckViolation), self.cr.savepoint(), mute_logger("odoo.sql_db"):
            self.Qualification.create({"name": "Invalid confirmed", "state": "confirmed", "quantity": 0})
            self.env.flush_all()
        self.assertEqual(self.Qualification.search_count([]), count)

    def test_create_confirmed_default_zero_rejected(self):
        """AC05: the quantity default cannot bypass the invariant."""
        count = self.Qualification.search_count([])
        with self.assertRaises(CheckViolation), self.cr.savepoint(), mute_logger("odoo.sql_db"):
            self.Qualification.create({"name": "Invalid default", "state": "confirmed"})
            self.env.flush_all()
        self.assertEqual(self.Qualification.search_count([]), count)

    def test_create_confirmed_positive(self):
        """AC05: direct creation accepts the smallest positive integer."""
        record = self.Qualification.create({"name": "Direct positive", "state": "confirmed", "quantity": 1})
        self.assert_record_values(record, "confirmed", 1, 10)

    def test_write_state_zero_rejected(self):
        """AC06: writing the state directly cannot confirm a zero line."""
        record = self.Qualification.create({"name": "Direct state", "quantity": 0})
        self.env.flush_all()
        with self.assertRaises(CheckViolation), self.cr.savepoint(), mute_logger("odoo.sql_db"):
            record.write({"state": "confirmed"})
            self.env.flush_all()
        self.assert_record_values(record, "draft", 0, 0)

    def test_write_confirmed_quantity_zero_rejected(self):
        """AC06: an existing confirmation keeps its positive quantity after rejection."""
        record = self.Qualification.create({"name": "Keep confirmed", "state": "confirmed", "quantity": 3})
        self.env.flush_all()
        with self.assertRaises(CheckViolation), self.cr.savepoint(), mute_logger("odoo.sql_db"):
            record.write({"quantity": 0})
            self.env.flush_all()
        self.assert_record_values(record, "confirmed", 3, 30)

    def test_write_state_and_positive_quantity(self):
        """AC06: a simultaneous positive quantity and confirmation is accepted."""
        record = self.Qualification.create({"name": "Simultaneous", "quantity": 0})
        record.write({"state": "confirmed", "quantity": 1})
        self.assert_record_values(record, "confirmed", 1, 10)
        record.write({"quantity": 3})
        self.assert_record_values(record, "confirmed", 3, 30)

    def test_load_valid_records(self):
        """AC07: real ORM import accepts zero drafts and positive confirmations."""
        result = self.Qualification.load(
            ["name", "state", "quantity", "unit_price"],
            [["Imported draft", "draft", "0", "10"], ["Imported confirmed", "confirmed", "1", "10"]],
        )
        self.assertFalse(result["messages"])
        self.assertEqual(len(result["ids"]), 2)
        records = self.Qualification.browse(result["ids"])
        self.assert_record_values(records[0], "draft", 0, 0)
        self.assert_record_values(records[1], "confirmed", 1, 10)

    def test_load_create_zero_confirmed_rejected(self):
        """AC07: a rejected real import leaves no invalid creation."""
        count = self.Qualification.search_count([])
        with mute_logger("odoo.sql_db"):
            result = self.Qualification.load(
                ["name", "state", "quantity"], [["Invalid import", "confirmed", "0"]],
            )
        self.assertFalse(result["ids"])
        self.assertTrue(any(message["type"] == "error" for message in result["messages"]))
        self.assertEqual(self.Qualification.search_count([]), count)
        self.assertFalse(self.Qualification.search([("name", "=", "Invalid import")]))

    def test_load_update_zero_confirmed_rejected(self):
        """AC07: a failed real import update preserves identity and previous values."""
        record = self.Qualification.create({"name": "Imported update", "state": "confirmed", "quantity": 3})
        self.env.flush_all()
        record_id = record.id
        with mute_logger("odoo.sql_db"):
            result = self.Qualification.load([".id", "quantity"], [[str(record_id), "0"]])
        self.assertFalse(result["ids"])
        self.assertTrue(any(message["type"] == "error" for message in result["messages"]))
        self.assertEqual(record.exists().id, record_id)
        self.assertEqual(record.name, "Imported update")
        self.assert_record_values(record, "confirmed", 3, 30)

    def test_negative_create_internal_user(self):
        """AC08/AC09: the existing negative constraint also applies to internal users."""
        count = self.Qualification.search_count([])
        with self.assertRaises(CheckViolation), self.cr.savepoint(), mute_logger("odoo.sql_db"):
            self.Qualification.create({"name": "Negative internal", "quantity": -1})
            self.env.flush_all()
        self.assertEqual(self.Qualification.search_count([]), count)

    def test_negative_write_internal_user_preserved(self):
        """AC08: rejected negative edits preserve the positive quantity and amount."""
        record = self.Qualification.create({"name": "Preserve internal", "quantity": 3})
        self.env.flush_all()
        with self.assertRaises(CheckViolation), self.cr.savepoint(), mute_logger("odoo.sql_db"):
            record.write({"quantity": -1})
            self.env.flush_all()
        self.assert_record_values(record, "draft", 3, 30)
