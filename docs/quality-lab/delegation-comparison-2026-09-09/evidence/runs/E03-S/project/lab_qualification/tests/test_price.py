from psycopg2.errors import CheckViolation

from odoo.tests import tagged
from odoo.tests.common import TransactionCase
from odoo.tools import mute_logger


@tagged("post_install", "-at_install")
class TestPrice(TransactionCase):
    @classmethod
    def setUpClass(cls):
        """Prepare the model used by all price scenarios."""
        super().setUpClass()
        cls.Qualification = cls.env["lab.qualification"]

    def test_negative_price_create(self):
        """Reject every negative price, including on zero quantity."""
        for quantity, price in [(3, -1), (0, -1), (2, -0.000001)]:
            with self.subTest(quantity=quantity, price=price):
                with self.assertRaises(CheckViolation), self.env.cr.savepoint(), mute_logger("odoo.sql_db"):
                    self.Qualification.create({
                        "name": "Invalid price", "quantity": quantity, "unit_price": price,
                    })
                    self.env.flush_all()
                self.assertFalse(self.Qualification.search([("name", "=", "Invalid price")]))

    def test_negative_price_context_default(self):
        """Validate effective defaults as well as explicit field values."""
        with self.assertRaises(CheckViolation), self.env.cr.savepoint(), mute_logger("odoo.sql_db"):
            self.Qualification.with_context(default_unit_price=-1).create({"name": "Default price"})
            self.env.flush_all()

    def test_negative_price_write(self):
        """A rejected edit preserves a confirmed line and its amount."""
        record = self.Qualification.create({"name": "Preserved", "quantity": 3, "unit_price": 12})
        record.action_confirm()
        self.env.flush_all()
        with self.assertRaises(CheckViolation), self.env.cr.savepoint(), mute_logger("odoo.sql_db"):
            record.write({"unit_price": -1, "quantity": 8, "name": "Rejected"})
            self.env.flush_all()
        record.invalidate_recordset()
        self.assertEqual(
            (record.name, record.quantity, record.unit_price, record.amount, record.state),
            ("Preserved", 3, 12, 36, "confirmed"),
        )

    def test_free_and_positive_confirmation(self):
        """Free, empty and priced lines retain the original confirmation behavior."""
        records = self.Qualification.create([
            {"name": "Free", "quantity": 4, "unit_price": 0},
            {"name": "Empty", "quantity": 0, "unit_price": 11},
            {"name": "Priced", "quantity": 3, "unit_price": 12.5},
        ])
        records.action_confirm()
        self.env.flush_all()
        records.invalidate_recordset()
        self.assertEqual(records.mapped("state"), ["confirmed"] * 3)
        self.assertEqual(records.mapped("amount"), [0, 0, 37.5])

    def test_amount_recomputed_on_edits(self):
        """Both factors update the stored amount, including a free confirmed line."""
        record = self.Qualification.create({"name": "Edits", "quantity": 2, "unit_price": 12.5})
        record.action_confirm()
        for values, expected in [({"quantity": 4}, 50), ({"unit_price": 3}, 12), ({"unit_price": 0}, 0)]:
            record.write(values)
            self.env.flush_all()
            record.invalidate_recordset()
            self.assertEqual((record.amount, record.state), (expected, "confirmed"))

    def test_mixed_create_batch_rollback(self):
        """Neither a valid nor an invalid row survives a rejected create batch."""
        before = self.Qualification.search([]).ids
        for invalid in [{"unit_price": -2}, {"quantity": -2}]:
            with self.subTest(invalid=invalid):
                with self.assertRaises(CheckViolation), self.env.cr.savepoint(), mute_logger("odoo.sql_db"):
                    self.Qualification.create([
                        {"name": "Batch valid", "quantity": 2, "unit_price": 8},
                        {"name": "Batch invalid", **invalid},
                        {"name": "Batch free", "quantity": 2, "unit_price": 0},
                    ])
                    self.env.flush_all()
                self.assertEqual(self.Qualification.search([]).ids, before)

    def test_write_batch_rollback(self):
        """A rejected multi-record write preserves every original value."""
        records = self.Qualification.create([
            {"name": "Batch priced", "quantity": 3, "unit_price": 12},
            {"name": "Batch free", "quantity": 4, "unit_price": 0},
        ])
        self.env.flush_all()
        for invalid in [{"unit_price": -1}, {"quantity": -1}]:
            with self.subTest(invalid=invalid):
                with self.assertRaises(CheckViolation), self.env.cr.savepoint(), mute_logger("odoo.sql_db"):
                    records.write(invalid)
                    self.env.flush_all()
                records.invalidate_recordset()
                self.assertEqual(records.mapped("unit_price"), [12, 0])
                self.assertEqual(records.mapped("quantity"), [3, 4])
                self.assertEqual(records.mapped("amount"), [36, 0])

    def test_transaction_batch_rollback(self):
        """A later invalid operation rolls back earlier edits in the same transaction."""
        record = self.Qualification.create({"name": "Transaction", "quantity": 3, "unit_price": 12})
        self.env.flush_all()
        with self.assertRaises(CheckViolation), self.env.cr.savepoint(), mute_logger("odoo.sql_db"):
            record.write({"unit_price": 15})
            self.env.flush_all()
            self.Qualification.create({"name": "Later invalid", "unit_price": -1})
            self.env.flush_all()
        record.invalidate_recordset()
        self.assertEqual((record.unit_price, record.amount), (12, 36))
        self.assertFalse(self.Qualification.search([("name", "=", "Later invalid")]))

    def test_load_valid_batch(self):
        """Import accepts paid, free and empty lines and computes their amounts."""
        result = self.Qualification.load(
            ["name", "quantity", "unit_price"],
            [["Import priced", "3", "12.5"], ["Import free", "4", "0"], ["Import empty", "0", "10"]],
        )
        self.assertFalse(result["messages"])
        self.assertEqual(len(result["ids"]), 3)
        records = self.Qualification.browse(result["ids"])
        records.action_confirm()
        self.env.flush_all()
        records.invalidate_recordset()
        self.assertEqual(records.mapped("amount"), [37.5, 0, 0])
        self.assertEqual(records.mapped("state"), ["confirmed"] * 3)

    def test_load_invalid_create_batch(self):
        """Import reports the error and cancels all rows, regardless of their order."""
        before = self.Qualification.search([]).ids
        for quantity, price in [("2", "-1"), ("0", "-0.000001"), ("-1", "5")]:
            with self.subTest(quantity=quantity, price=price), mute_logger("odoo.sql_db"):
                result = self.Qualification.load(
                    ["name", "quantity", "unit_price"],
                    [["Import valid", "2", "8"], ["Import invalid", quantity, price], ["Import free", "3", "0"]],
                )
                self.assertFalse(result["ids"])
                self.assertTrue(any(message["type"] == "error" for message in result["messages"]))
                self.assertEqual(self.Qualification.search([]).ids, before)

    def test_load_invalid_update_batch(self):
        """Import rollback restores earlier valid edits when another row is invalid."""
        records = self.Qualification.create([
            {"name": "Import keep priced", "quantity": 3, "unit_price": 12},
            {"name": "Import keep free", "quantity": 4, "unit_price": 0},
        ])
        records.action_confirm()
        self.env.flush_all()
        for quantity, price in [("4", "-1"), ("-1", "5")]:
            with self.subTest(quantity=quantity, price=price), mute_logger("odoo.sql_db"):
                result = self.Qualification.load(
                    [".id", "quantity", "unit_price"],
                    [[str(records[0].id), "6", "15"], [str(records[1].id), quantity, price]],
                )
                self.assertFalse(result["ids"])
                self.assertTrue(any(message["type"] == "error" for message in result["messages"]))
                records.invalidate_recordset()
                self.assertEqual(records.mapped("quantity"), [3, 4])
                self.assertEqual(records.mapped("unit_price"), [12, 0])
                self.assertEqual(records.mapped("amount"), [36, 0])
                self.assertEqual(records.mapped("state"), ["confirmed", "confirmed"])
