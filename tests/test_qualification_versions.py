import importlib.util
import unittest
from pathlib import Path

SPEC = importlib.util.spec_from_file_location(
    "odoo_qualify_versions", Path(__file__).resolve().parents[1] / "scripts/odoo_qualify_versions.py"
)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class TestVersionQualificationOracle(unittest.TestCase):
    def good_log(self):
        return "\n".join(
            [f"QUALIFICATION_PASS {key}" for key in MODULE.ORM_MARKERS]
            + ["0 failed, 0 error(s) of 5 tests", "Closing chrome headless with pid 123",
               "test.browser: QUALIFICATION_BROWSER_CLICK_OK", "QUALIFICATION_PASS browser_server"]
        )

    def test_real_browser_evidence_required(self):
        self.assertTrue(MODULE.assess(self.good_log(), 0, True)["pass"])
        self.assertFalse(MODULE.assess(self.good_log().replace("Closing chrome headless with pid 123", "HTTP 200"), 0, True)["pass"])
        self.assertFalse(MODULE.assess(self.good_log().replace("QUALIFICATION_PASS browser_server", ""), 0, True)["pass"])
        self.assertFalse(MODULE.assess(self.good_log().replace("test.browser: QUALIFICATION_BROWSER_CLICK_OK", "console.log('QUALIFICATION_BROWSER_CLICK_OK');"), 0, True)["pass"])

    def test_skipped_and_red_never_pass(self):
        self.assertFalse(MODULE.assess(self.good_log() + "\nChrome executable not found", 0, True)["pass"])
        self.assertFalse(MODULE.assess(self.good_log().replace("0 failed", "1 failed"), 0, True)["pass"])
        self.assertFalse(MODULE.assess(self.good_log(), 1, True)["pass"])

    def test_odoo_silent_skip_is_an_infrastructure_failure(self):
        log = "\n".join(
            [f"QUALIFICATION_PASS {key}" for key in MODULE.ORM_MARKERS]
            + ["0 failed, 0 error(s) of 5 tests", "Chrome headless failed to start:",
               "skipped TestBrowserConfirmation.test_browser_confirmation : Failed to detect chrome devtools port after 10.0s."]
        )
        verdict = MODULE.assess(log, 0, True)
        self.assertFalse(verdict["pass"])
        self.assertTrue(verdict["skip_observed"])
        self.assertEqual(len(verdict["skip_reasons"]), 1)

    def test_mutant_requires_specific_server_failure_after_browser(self):
        log = self.good_log().replace("0 failed", "1 failed").replace("QUALIFICATION_PASS browser_server", "AssertionError QUALIFICATION_SERVER_STATE")
        self.assertTrue(MODULE.assess(log, 1, True, True)["pass"])
        self.assertFalse(MODULE.assess(log.replace("QUALIFICATION_BROWSER_CLICK_OK", ""), 1, True, True)["pass"])
        self.assertFalse(MODULE.assess("Database connection refused", 1, True, True)["pass"])


if __name__ == "__main__":
    unittest.main()
