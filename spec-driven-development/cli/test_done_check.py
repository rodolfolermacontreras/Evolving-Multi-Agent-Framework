#!/usr/bin/env python3
"""Tests for the DONE-completeness check (SDD-046 / B-2 rule 2).

Both polarities per R-B2-4: fixtures that catch real violations (missing retro;
unchecked REQUIRED box) and a fixture proving a complete dir passes.

Stdlib only (LESSON-001 / Article V).
"""

import io
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

THIS = Path(__file__).resolve()
CLI_DIR = THIS.parent
sys.path.insert(0, str(CLI_DIR))

import done_check  # noqa: E402


def run_main(argv):
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        rc = done_check.main(argv)
    return rc, buffer.getvalue()


VALIDATION_COMPLETE = """\
# VALIDATION: demo

## Required Items

- [x] R-1: first item.
- [x] R-2: second item.

## Optional Items

- [ ] O-1: optional, not required.
"""

VALIDATION_UNCHECKED = """\
# VALIDATION: demo

## Required Items

- [x] R-1: first item.
- [ ] R-2: second item still open.

## Optional Items

- [ ] O-1: optional, not required.
"""


def _make_dir(parent, name, *, validation, spec=True, retro=True):
    feature = parent / name
    feature.mkdir(parents=True)
    if spec:
        (feature / "spec.md").write_text("# spec\n", encoding="utf-8")
    (feature / "validation.md").write_text(validation, encoding="utf-8")
    if retro:
        (feature / "RETRO.md").write_text("# retro\n", encoding="utf-8")
    return feature


class TestDoneCheck(unittest.TestCase):
    def test_missing_retro_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            feature = _make_dir(Path(tmp), "feat", validation=VALIDATION_COMPLETE, retro=False)
            rc, out = run_main([str(feature)])
            self.assertEqual(rc, 1)
            self.assertIn("RETRO", out.upper())

    def test_unchecked_required_box_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            feature = _make_dir(Path(tmp), "feat", validation=VALIDATION_UNCHECKED)
            rc, out = run_main([str(feature)])
            self.assertEqual(rc, 1)
            self.assertIn("R-2", out)

    def test_complete_dir_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            feature = _make_dir(Path(tmp), "feat", validation=VALIDATION_COMPLETE)
            rc, out = run_main([str(feature)])
            self.assertEqual(rc, 0)
            self.assertIn("PASS", out)

    def test_optional_unchecked_does_not_fail(self):
        with tempfile.TemporaryDirectory() as tmp:
            feature = _make_dir(Path(tmp), "feat", validation=VALIDATION_COMPLETE)
            problems = done_check.check_feature_dir(feature)
            self.assertEqual(problems, [])

    def test_audit_pi_only_includes_done_dirs_referencing_pi(self):
        with tempfile.TemporaryDirectory() as tmp:
            specs = Path(tmp)
            # Claims done + references PI-9 -> audited (and it is complete -> no problem).
            done_pi = _make_dir(specs, "done-pi9", validation=VALIDATION_COMPLETE)
            (done_pi / "spec.md").write_text("targets PI-9\n", encoding="utf-8")
            # In-progress (no retro) -> excluded even though it references PI-9.
            wip = _make_dir(specs, "wip-pi9", validation=VALIDATION_UNCHECKED, retro=False)
            (wip / "spec.md").write_text("targets PI-9\n", encoding="utf-8")
            # Done but references a different PI -> excluded.
            other = _make_dir(specs, "done-pi3", validation=VALIDATION_UNCHECKED)
            (other / "spec.md").write_text("targets PI-3\n", encoding="utf-8")

            problems = done_check.audit_pi(specs, "PI-9")
            self.assertEqual(problems, [])


if __name__ == "__main__":
    unittest.main()
