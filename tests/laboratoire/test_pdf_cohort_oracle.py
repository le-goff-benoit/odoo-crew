import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
PATH = ROOT / "benchmarks/workflow_regressions/addons/workflow_oracle/tests/pdf_assertions.py"
spec = importlib.util.spec_from_file_location("pdf_assertions", PATH)
oracle = importlib.util.module_from_spec(spec)
spec.loader.exec_module(oracle)


class PdfCohortOracleTests(unittest.TestCase):
    def test_pdf_reference_and_three_mutations(self):
        good = "Facture Prestation Forfait Explication gratuite 49"
        labels = ["Prestation", "Forfait", "Explication gratuite"]
        oracle.assert_pdf_cohort(good, labels, ["Technique"], "Facture")
        for bad, marker in (
            (good.replace("Explication gratuite", ""), "WORKFLOW_INVOICE_LINE"),
            (good + " Technique", "WORKFLOW_INVOICE_LINE_TECHNICAL"),
            (good.replace("Facture", "Invoice"), "WORKFLOW_INVOICE_LANGUAGE"),
        ):
            with self.subTest(marker=marker), self.assertRaisesRegex(AssertionError, marker):
                oracle.assert_pdf_cohort(bad, labels, ["Technique"], "Facture")

    def test_accounting_write_guard_distinguishes_tables_and_reads(self):
        for statement in (
            "UPDATE account_move SET amount_total=0",
            'INSERT INTO "account_move_line" (id) VALUES (1)',
            "DELETE FROM account_move WHERE id=1",
            "WITH ids AS (SELECT 1) UPDATE account_move_line SET debit=0",
        ):
            self.assertTrue(oracle.accounting_write(statement), statement)
        for statement in (
            "SELECT * FROM account_move",
            "UPDATE account_move_send SET foo=1",
            "INSERT INTO ir_attachment (id) VALUES (1)",
        ):
            self.assertFalse(oracle.accounting_write(statement), statement)
        query = type("SQL", (), {"code": "UPDATE account_move SET name='x'"})()
        self.assertTrue(oracle.accounting_write(query))
