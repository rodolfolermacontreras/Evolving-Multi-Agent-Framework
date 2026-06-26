#!/usr/bin/env python3
"""Tests for the TDD-gate mechanical check (SDD-046 / B-2 rule 1).

Both polarities per R-B2-4: a fixture that catches a real violation (FAIL) and
fixtures that prove clean cases pass (PASS).

Stdlib only (LESSON-001 / Article V).
"""

import io
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path

THIS = Path(__file__).resolve()
CLI_DIR = THIS.parent
sys.path.insert(0, str(CLI_DIR))

import tdd_gate_check  # noqa: E402


def run_main(argv):
    """Invoke main(argv); return (rc, stdout)."""
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        rc = tdd_gate_check.main(argv)
    return rc, buffer.getvalue()


PROD = "spec-driven-development/cli/widget.py"
TESTF = "spec-driven-development/cli/test_widget.py"


class TestTddGateCheck(unittest.TestCase):
    def test_prod_change_no_test_no_tag_fails(self):
        rc, out = run_main(["--files", PROD])
        self.assertEqual(rc, 1)
        self.assertIn("widget.py", out)
        self.assertIn("FAIL", out)

    def test_prod_change_with_test_passes(self):
        rc, out = run_main(["--files", PROD, TESTF])
        self.assertEqual(rc, 0)
        self.assertIn("PASS", out)

    def test_empty_diff_passes(self):
        rc, out = run_main(["--files"])
        self.assertEqual(rc, 0)
        self.assertIn("PASS", out)

    def test_no_test_needed_tag_passes(self):
        rc, out = run_main(
            ["--files", PROD, "--tag-text", "T-1 [NO-TEST-NEEDED] generated metadata"]
        )
        self.assertEqual(rc, 0)
        self.assertIn("PASS", out)

    def test_docs_only_change_passes(self):
        rc, out = run_main(["--files", "spec-driven-development/docs/notes.md"])
        self.assertEqual(rc, 0)

    def test_evaluate_classifies_prod_and_test(self):
        ok, offenders = tdd_gate_check.evaluate([PROD])
        self.assertFalse(ok)
        self.assertEqual(offenders, [PROD])
        ok, offenders = tdd_gate_check.evaluate([PROD, TESTF])
        self.assertTrue(ok)
        self.assertEqual(offenders, [])


if __name__ == "__main__":
    unittest.main()
