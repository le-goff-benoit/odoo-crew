import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "workflow_bench", ROOT / "scripts/odoo_bench_workflows.py"
)
BENCH = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BENCH)


class WorkflowRegressionTests(unittest.TestCase):
    def witness(self):
        return "\n".join(
            ["WORKFLOW_PASS " + key for key in BENCH.REQUIRED]
            + [
                "0 failed, 0 error(s) of 3 tests",
                "test.browser: WORKFLOW_BROWSER_REAL_CLICK",
                "Closing chrome headless with pid 123",
            ]
        )

    def test_requires_all_real_capabilities(self):
        self.assertTrue(BENCH.assess(self.witness(), 0)["pass"])
        for marker in [
            "WORKFLOW_PASS stock",
            "WORKFLOW_PASS invoice_pdf",
            "WORKFLOW_PASS browser_form",
            "test.browser: WORKFLOW_BROWSER_REAL_CLICK",
            "Closing chrome headless with pid 123",
        ]:
            self.assertFalse(
                BENCH.assess(self.witness().replace(marker, ""), 0)["pass"]
            )
        self.assertFalse(BENCH.assess(self.witness(), 1)["pass"])

    def test_skipped_chrome_is_not_green(self):
        self.assertFalse(
            BENCH.assess(self.witness() + "\nskipped TestFormWorkflow", 0)["pass"]
        )

    def test_transport_error_cannot_calibrate_mutants(self):
        log = "3 failed, 0 error(s) of 3 tests\nWORKFLOW_STOCK_REMAINDER\nWORKFLOW_INVOICE_LINE\nWORKFLOW_FORM_EXPLICIT_VALUE"
        self.assertTrue(BENCH.assess(log, 1, True)["pass"])
        self.assertFalse(BENCH.assess("database unavailable", 1, True)["pass"])
        self.assertFalse(
            BENCH.assess(log.replace("0 error", "1 error"), 1, True)["pass"]
        )
        self.assertFalse(
            BENCH.assess(log.replace("WORKFLOW_INVOICE_LINE", ""), 1, True)["pass"]
        )

    def test_oracle_unchanged_by_candidate_mutations(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            witness = BENCH.prepare(root / "witness")
            mutant = BENCH.prepare(root / "mutant", True)
            for original in (witness / "workflow_oracle").rglob("*"):
                if original.is_file():
                    self.assertEqual(
                        original.read_bytes(),
                        (mutant / original.relative_to(witness)).read_bytes(),
                    )
            self.assertNotEqual(
                (witness / "workflow_case/models.py").read_bytes(),
                (mutant / "workflow_case/models.py").read_bytes(),
            )

    def test_six_cases_keep_oracles_outside_public_dossiers(self):
        protocol = json.loads((BENCH.FIXTURE / "protocol.json").read_text())
        self.assertEqual(len(protocol["cases"]), 6)
        for case in protocol["cases"]:
            path = BENCH.FIXTURE / "cases" / case["directory"]
            self.assertTrue((path / "public/task.md").is_file())
            self.assertTrue(
                json.loads((path / "oracle.json").read_text())["requirements"]
            )
            self.assertFalse((path / "public/oracle.json").exists())


class WorkflowDossierOracleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location(
            "dossier_oracle", BENCH.FIXTURE / "dossier_oracle.py"
        )
        cls.oracle = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.oracle)

    def test_received_proof_and_new_intention_both_required(self):
        import hashlib

        public = BENCH.FIXTURE / "cases/W05_release/public"
        answer = {
            "preserved_receipt_sha256": hashlib.sha256(
                (public / "receipt.json").read_bytes()
            ).hexdigest(),
            "tasks": [
                {"id": "T01", "status": "received"},
                {"id": "T03", "intentions": ["I03"]},
            ],
            "resume_task": "T02",
            "proposed_checks_executed": False,
            "checks": [["python3", "check.py"]],
        }
        self.assertTrue(self.oracle.judge_release(public, answer)["pass"])
        for key, value in [
            ("preserved_receipt_sha256", "changed"),
            ("tasks", [{"id": "T01", "status": "received"}]),
            ("proposed_checks_executed", True),
            ("checks", ["test to add"]),
        ]:
            self.assertFalse(
                self.oracle.judge_release(public, dict(answer, **{key: value}))["pass"]
            )

    def test_configuration_beats_misleading_ticket_without_inventing_deployment(self):
        answer = {
            "source_series": "18.0",
            "deployed_series": None,
            "constraint_api": "_sql_constraints",
            "journal_conflict": True,
            "evidence_files": [".odoo-agents/config", "__manifest__.py"],
            "requested_secret": False,
        }
        self.assertTrue(self.oracle.judge_diagnostic(answer)["pass"])
        for key, value in [
            ("source_series", "19.0"),
            ("deployed_series", "18.0"),
            ("constraint_api", "models.Constraint"),
            ("requested_secret", True),
        ]:
            self.assertFalse(
                self.oracle.judge_diagnostic(dict(answer, **{key: value}))["pass"]
            )


class MiniReleaseIntegrationTests(unittest.TestCase):
    def test_real_plan_flow_intentions_resume_and_proof_mutation(self):
        spec = importlib.util.spec_from_file_location(
            "mini_release", BENCH.FIXTURE / "mini_release.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as folder:
            result = module.execute(Path(folder) / "run")
            self.assertTrue(result["pass"])
            self.assertEqual(result["received_tasks"], ["T01", "T02", "T03"])
            self.assertTrue(result["changed_proof_rejected"])
            self.assertTrue(result["scope_conflict_rejected"])


class DiagnosticSourceTests(unittest.TestCase):
    def test_real_series_reader_ignores_misleading_imported_journal(self):
        import sys

        sys.path.insert(0, str(ROOT / "scripts"))
        import odoo_series

        actual = odoo_series.resolve(BENCH.FIXTURE / "cases/W06_diagnostic/public")
        self.assertEqual(actual["series"], "18.0")


if __name__ == "__main__":
    unittest.main()
