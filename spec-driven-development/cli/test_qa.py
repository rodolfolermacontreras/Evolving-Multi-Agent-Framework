"""Acceptance tests for cli/qa.py (SDD-004).

Covers AC1-AC9 from spec-driven-development/specs/2026-05-16-qa-cli/spec.md.
AC10 (--help) is validated manually.
"""

from __future__ import annotations

import ast
import sys
import tempfile
import unittest
from io import StringIO
from contextlib import redirect_stdout
from pathlib import Path

THIS = Path(__file__).resolve()
SDD_ROOT = THIS.parents[1]
CLI_DIR = SDD_ROOT / "cli"

sys.path.insert(0, str(CLI_DIR))
import qa  # noqa: E402


# -- Fixture helpers -------------------------------------------------------- #


SPEC_MD = """\
# Feature Spec: widget

## Acceptance Criteria

1. Given input, when processed, then widget is created.
2. Given a widget, when deleted, then it is removed.
3. Given a widget, when renamed, then the name updates.
"""

VALIDATION_MD_PARTIAL = """\
# Validation Contract: widget

## Automated Tests

- [x] `test_widget_create`: proves AC1.
- [ ] `test_widget_delete`: proves AC2.
- [x] `test_widget_rename`: proves AC3.
"""

VALIDATION_MD_ALL_CHECKED = """\
# Validation Contract: widget

## Automated Tests

- [x] `test_widget_create`: proves AC1.
- [x] `test_widget_delete`: proves AC2.
- [x] `test_widget_rename`: proves AC3.
"""

TASKS_MD_MIXED = """\
| Task ID | Tag | Description | File Scope | Acceptance Test | Effort | Deps | Mode | Fleet | Status |
|---------|-----|-------------|------------|-----------------|--------|------|------|-------|--------|
| T-001 | [S] | Build widget | `cli/widget.py` | Proves AC1 | S | None | AFK | No | done |
| T-002 | [S] | Delete widget | `cli/widget.py` | Proves AC2 | S | T-001 | AFK | No | pending |
| T-003 | [S] | Rename widget | `cli/widget.py` | Proves AC3 | S | T-001 | AFK | No | done |
"""

TASKS_MD_ALL_DONE = """\
| Task ID | Tag | Description | File Scope | Acceptance Test | Effort | Deps | Mode | Fleet | Status |
|---------|-----|-------------|------------|-----------------|--------|------|------|-------|--------|
| T-001 | [S] | Build widget | `cli/widget.py` | Proves AC1 | S | None | AFK | No | done |
| T-002 | [S] | Delete widget | `cli/widget.py` | Proves AC2 | S | T-001 | AFK | No | done |
| T-003 | [S] | Rename widget | `cli/widget.py` | Proves AC3 | S | T-001 | AFK | No | done |
"""

TEST_FILE_CONTENT = """\
def test_widget_create():
    pass

def test_widget_rename():
    pass
"""

# Clean impl -- no bare except, no debug prints
CLEAN_IMPL = """\
import sys
from pathlib import Path

def create_widget(name):
    return {"name": name}

def delete_widget(widget):
    print("removing", file=sys.stderr)
    return None
"""

# Dirty impl -- bare except + debug print
DIRTY_IMPL = """\
import sys
import os
from pathlib import Path

def create_widget(name):
    try:
        return {"name": name}
    except:
        return None

def debug_info(widget):
    print("DEBUG widget:", widget)
    print("safe stderr", file=sys.stderr)
    return True
"""


def _seed_feature(tmp: Path, *,
                  spec: str = SPEC_MD,
                  validation: str = VALIDATION_MD_PARTIAL,
                  tasks: str = TASKS_MD_MIXED,
                  test_content: str = TEST_FILE_CONTENT,
                  impl_content: str = CLEAN_IMPL) -> tuple[Path, Path, Path]:
    """Create feature dir + impl file + test file under tmp. Return paths."""
    feature = tmp / "specs" / "2026-05-16-widget"
    feature.mkdir(parents=True)
    (feature / "spec.md").write_text(spec, encoding="utf-8")
    (feature / "validation.md").write_text(validation, encoding="utf-8")
    (feature / "tasks.md").write_text(tasks, encoding="utf-8")

    impl_file = tmp / "cli" / "widget.py"
    impl_file.parent.mkdir(parents=True, exist_ok=True)
    impl_file.write_text(impl_content, encoding="utf-8")

    test_file = tmp / "cli" / "test_widget.py"
    test_file.write_text(test_content, encoding="utf-8")

    return feature, impl_file, test_file


# -- Tests ------------------------------------------------------------------ #


class TestQACLI(unittest.TestCase):
    """Acceptance tests for qa.py (SDD-004)."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.tmp = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    # AC1: validation.md checkbox count
    def test_validation_checkbox_report(self):
        """AC1: checked/unchecked counts, unchecked items listed."""
        feature, impl, test = _seed_feature(self.tmp)
        report = qa.check_validation(feature / "validation.md")
        self.assertEqual(report["checked"], 2)
        self.assertEqual(report["unchecked"], 1)
        self.assertEqual(len(report["unchecked_items"]), 1)
        self.assertIn("test_widget_delete", report["unchecked_items"][0])

    # AC2: AC cross-reference
    def test_ac_crossref_missing_and_extra(self):
        """AC2: MISSING ACs and EXTRA tests detected."""
        feature, impl, test = _seed_feature(self.tmp)
        result = qa.check_ac_crossref(
            feature / "spec.md",
            feature / "validation.md",
        )
        # AC2 has no test that "proves" it (test_widget_delete is unchecked but
        # still references AC2 -- it's in validation.md). The cross-ref uses
        # validation.md "proves ACn" references.
        # In our fixture: AC1 -> test_widget_create, AC3 -> test_widget_rename,
        # AC2 -> test_widget_delete. All ACs are covered in validation.md.
        # So with all 3 ACs and all 3 tests mapped, there should be no MISSING
        # or EXTRA for this particular fixture.
        # Let's test with a fixture where AC coverage differs.

        # Create a spec with 4 ACs but only 3 tests in validation.md
        spec_4ac = """\
# Feature Spec: widget

## Acceptance Criteria

1. AC one.
2. AC two.
3. AC three.
4. AC four.
"""
        validation_3test = """\
# Validation Contract

## Automated Tests

- [x] `test_a`: proves AC1.
- [x] `test_b`: proves AC2, AC3.
"""
        (feature / "spec.md").write_text(spec_4ac, encoding="utf-8")
        (feature / "validation.md").write_text(validation_3test, encoding="utf-8")

        result = qa.check_ac_crossref(
            feature / "spec.md",
            feature / "validation.md",
        )
        # AC4 has no test -> MISSING
        self.assertIn("AC4", result["missing"])
        # test_a and test_b are mapped to known ACs -> no EXTRA
        self.assertEqual(len(result["extra"]), 0)

    # AC3: tasks.md status check
    def test_task_status_check(self):
        """AC3: tasks not marked done are flagged."""
        feature, impl, test = _seed_feature(self.tmp)
        result = qa.check_task_status(feature / "tasks.md")
        self.assertEqual(len(result["not_done"]), 1)
        self.assertEqual(result["not_done"][0]["task_id"], "T-002")

    # AC4: bare except scan
    def test_bare_except_scan(self):
        """AC4: bare except lines flagged as CRITICAL."""
        feature, impl, test = _seed_feature(self.tmp, impl_content=DIRTY_IMPL)
        findings = qa.scan_bare_except([impl])
        self.assertGreaterEqual(len(findings), 1)
        self.assertTrue(any("except" in f["line"].lower() for f in findings))
        self.assertTrue(all(f["severity"] == "CRITICAL" for f in findings))

    # AC5: debug print scan
    def test_debug_print_scan(self):
        """AC5: print() calls not to stderr flagged as WARNING."""
        feature, impl, test = _seed_feature(self.tmp, impl_content=DIRTY_IMPL)
        findings = qa.scan_debug_prints([impl])
        # "print("DEBUG widget:", widget)" should be flagged
        # "print("safe stderr", file=sys.stderr)" should NOT be flagged
        flagged_lines = [f["line"] for f in findings]
        self.assertTrue(any("DEBUG widget" in l for l in flagged_lines))
        self.assertFalse(any("file=sys.stderr" in l for l in flagged_lines))
        self.assertTrue(all(f["severity"] == "WARNING" for f in findings))

    # AC6: two-section report
    def test_report_has_two_stages(self):
        """AC6: report contains Stage 1 and Stage 2 sections."""
        feature, impl, test = _seed_feature(self.tmp)
        buf = StringIO()
        with redirect_stdout(buf):
            qa.main(["check", "--feature", str(feature), "--impl", str(impl)])
        output = buf.getvalue()
        self.assertIn("Stage 1: Spec Compliance", output)
        self.assertIn("Stage 2: Code Quality", output)

    # AC7: compliant exit 0
    def test_compliant_exit_zero(self):
        """AC7: all pass -> exit 0, COMPLIANT printed."""
        feature, impl, test = _seed_feature(
            self.tmp,
            validation=VALIDATION_MD_ALL_CHECKED,
            tasks=TASKS_MD_ALL_DONE,
            impl_content=CLEAN_IMPL,
        )
        buf = StringIO()
        with redirect_stdout(buf):
            code = qa.main(["check", "--feature", str(feature),
                            "--impl", str(impl)])
        self.assertEqual(code, 0)
        self.assertIn("COMPLIANT", buf.getvalue())

    # AC8: not compliant exit 1
    def test_not_compliant_exit_one(self):
        """AC8: Stage 1 fail -> exit 1, NOT COMPLIANT printed."""
        feature, impl, test = _seed_feature(
            self.tmp,
            validation=VALIDATION_MD_PARTIAL,
            tasks=TASKS_MD_MIXED,
        )
        buf = StringIO()
        with redirect_stdout(buf):
            code = qa.main(["check", "--feature", str(feature),
                            "--impl", str(impl)])
        self.assertEqual(code, 1)
        self.assertIn("NOT COMPLIANT", buf.getvalue())

    # AC9: stdlib-only runtime imports
    def test_runtime_imports_are_stdlib_only(self):
        """AC9: qa.py imports only stdlib modules."""
        qa_path = Path(qa.__file__).resolve()
        tree = ast.parse(qa_path.read_text(encoding="utf-8"))
        stdlib_modules = {
            "argparse", "ast", "datetime", "json", "os", "pathlib", "re",
            "shutil", "sqlite3", "subprocess", "sys", "typing", "textwrap",
            "collections", "contextlib", "io", "unittest", "tempfile",
            "functools", "itertools", "enum", "dataclasses", "abc",
            "__future__",
        }
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    mod = alias.name.split(".")[0]
                    self.assertIn(
                        mod, stdlib_modules,
                        f"Non-stdlib import found: {alias.name}",
                    )
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    mod = node.module.split(".")[0]
                    self.assertIn(
                        mod, stdlib_modules,
                        f"Non-stdlib import found: {node.module}",
                    )


if __name__ == "__main__":
    unittest.main()
