from psycopg2.errors import CheckViolation

from odoo.tests import tagged
from odoo.tests.common import TransactionCase
from odoo.tools import mute_logger


@tagged("post_install", "-at_install")
class TestPrice(TransactionCase):
    def test_negative_create(self):
        for state in ("draft", "confirmed"):
            for price in (-5, -0.000001):
                with self.subTest(state=state, price=price):
                    with self.assertRaises(CheckViolation), self.env.cr.savepoint():
                        self.env["lab.qualification"].create(
                            {"name": "Invalid price", "unit_price": price, "state": state}
                        )
                        self.env.flush_all()

    def test_negative_write_preserves_record(self):
        for state in ("draft", "confirmed"):
            record = self.env["lab.qualification"].create(
                {"name": "Preserved price", "quantity": 3, "unit_price": 12, "state": state}
            )
            self.env.flush_all()
            for price in (-5, -0.000001):
                with self.subTest(state=state, price=price):
                    with self.assertRaises(CheckViolation), self.env.cr.savepoint():
                        record.write({"unit_price": price, "quantity": 7})
                        self.env.flush_all()
                    record.invalidate_recordset()
                    self.assertEqual(
                        (record.quantity, record.unit_price, record.amount, record.state),
                        (3, 12, 36, state),
                    )

    def test_negative_context_default(self):
        with self.assertRaises(CheckViolation), self.env.cr.savepoint():
            self.env["lab.qualification"].with_context(default_unit_price=-1).create(
                {"name": "Invalid default"}
            )
            self.env.flush_all()

    def test_free_confirmation_and_recomputation(self):
        record = self.env["lab.qualification"].create(
            {"name": "Free", "quantity": 4, "unit_price": 0}
        )
        record.action_confirm()
        self.env.flush_all()
        record.invalidate_recordset()
        self.assertEqual((record.state, record.amount), ("confirmed", 0))
        record.write({"unit_price": 2.5})
        self.env.flush_all()
        record.invalidate_recordset()
        self.assertEqual(record.amount, 10)
        record.write({"quantity": 6})
        self.env.flush_all()
        record.invalidate_recordset()
        self.assertEqual(record.amount, 15)
        record.write({"unit_price": 0})
        self.env.flush_all()
        record.invalidate_recordset()
        self.assertEqual((record.unit_price, record.amount, record.state), (0, 0, "confirmed"))
        record.write({"quantity": 0, "unit_price": 3})
        self.env.flush_all()
        record.invalidate_recordset()
        self.assertEqual(record.amount, 0)

    def test_batch_create_atomicity(self):
        model = self.env["lab.qualification"]
        initial_ids = model.search([]).ids
        for invalid in ({"unit_price": -1}, {"quantity": -1}):
            with self.subTest(invalid=invalid):
                with self.assertRaises(CheckViolation), self.env.cr.savepoint():
                    model.create([
                        {"name": "Batch valid", "quantity": 2, "unit_price": 3},
                        {"name": "Batch invalid", **invalid},
                        {"name": "Batch free", "quantity": 4, "unit_price": 0},
                    ])
                    self.env.flush_all()
                self.assertEqual(model.search([]).ids, initial_ids)

    def test_batch_write_atomicity(self):
        records = self.env["lab.qualification"].create([
            {"name": "Batch priced", "quantity": 3, "unit_price": 12},
            {"name": "Batch free", "quantity": 4, "unit_price": 0},
        ])
        self.env.flush_all()
        fields = ["name", "quantity", "unit_price", "amount", "state"]
        before = records.read(fields)
        for invalid in ({"unit_price": -1}, {"quantity": -1}):
            with self.subTest(invalid=invalid):
                with self.assertRaises(CheckViolation), self.env.cr.savepoint():
                    records.write({"name": "Must roll back", **invalid})
                    self.env.flush_all()
                records.invalidate_recordset()
                self.assertEqual(records.read(fields), before)
        records.write({"unit_price": 0})
        records.action_confirm()
        self.env.flush_all()
        records.invalidate_recordset()
        self.assertEqual(records.mapped("amount"), [0, 0])
        self.assertEqual(records.mapped("state"), ["confirmed", "confirmed"])

    def test_transaction_batch_rollback(self):
        records = self.env["lab.qualification"].create([
            {"name": "First operation", "quantity": 2, "unit_price": 3},
            {"name": "Last operation", "quantity": 4, "unit_price": 0},
        ])
        self.env.flush_all()
        fields = ["quantity", "unit_price", "amount"]
        before = records.read(fields)
        with self.assertRaises(CheckViolation), self.env.cr.savepoint():
            records[0].write({"unit_price": 5})
            self.env.flush_all()
            records[1].write({"unit_price": -1})
            self.env.flush_all()
        records.invalidate_recordset()
        self.assertEqual(records.read(fields), before)

    def test_load_valid(self):
        model = self.env["lab.qualification"]
        result = model.load(["name", "quantity", "unit_price"], [
            ["Imported paid", "3", "2.5"],
            ["Imported free", "4", "0"],
            ["Imported empty", "0", "11"],
        ])
        self.assertFalse([m for m in result["messages"] if m["type"] == "error"])
        self.assertEqual(len(result["ids"]), 3)
        records = model.browse(result["ids"])
        records.action_confirm()
        self.env.flush_all()
        records.invalidate_recordset()
        self.assertEqual(records.mapped("amount"), [7.5, 0, 0])
        self.assertEqual(records.mapped("state"), ["confirmed"] * 3)

    @mute_logger("odoo.sql_db", "odoo.models", "odoo.orm.models")
    def test_load_create_atomicity(self):
        model = self.env["lab.qualification"]
        initial_ids = model.search([]).ids
        for quantity, price in (("3", "-0.000001"), ("-1", "5")):
            with self.subTest(quantity=quantity, price=price):
                result = model.load(["name", "quantity", "unit_price"], [
                    ["Import valid first", "2", "3"],
                    ["Import invalid", quantity, price],
                    ["Import free last", "4", "0"],
                ])
                self.assertIs(result["ids"], False)
                self.assertTrue([m for m in result["messages"] if m["type"] == "error"])
                self.assertEqual(model.search([]).ids, initial_ids)

    @mute_logger("odoo.sql_db", "odoo.models", "odoo.orm.models")
    def test_load_update_atomicity(self):
        model = self.env["lab.qualification"]
        records = model.create([
            {"name": "Import update paid", "quantity": 3, "unit_price": 12},
            {"name": "Import update free", "quantity": 4, "unit_price": 0},
        ])
        records.action_confirm()
        self.env.flush_all()
        fields = ["name", "quantity", "unit_price", "amount", "state"]
        before = records.read(fields)
        for quantity, price in (("4", "-1"), ("-1", "0")):
            with self.subTest(quantity=quantity, price=price):
                result = model.load([".id", "quantity", "unit_price"], [
                    [str(records[0].id), "8", "5"],
                    [str(records[1].id), quantity, price],
                ])
                self.assertIs(result["ids"], False)
                self.assertTrue([m for m in result["messages"] if m["type"] == "error"])
                records.invalidate_recordset()
                self.assertEqual(records.read(fields), before)
        result = model.load([".id", "quantity", "unit_price"], [
            [str(records[0].id), "3", "0"],
            [str(records[1].id), "4", "2.5"],
        ])
        self.assertEqual(result["ids"], records.ids)
        self.env.flush_all()
        records.invalidate_recordset()
        self.assertEqual(records.mapped("amount"), [0, 10])
        self.assertEqual(records.mapped("state"), ["confirmed", "confirmed"])
