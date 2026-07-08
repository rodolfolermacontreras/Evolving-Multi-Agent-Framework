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


# ---------------------------------------------------------------------------
# SDD-050 (Dashboard truth): split-validation support + shared completeness
# helper. done_check and state_builder must agree on "is this dir DONE?".
# ---------------------------------------------------------------------------

def _make_split_dir(parent, name, *, files, spec=True, retro=True):
    """Write a feature dir with one or more validation*.md files.

    files: dict of {filename: contents}. Enables validation-a.md / validation-b.md
    split-file fixtures the single-file _make_dir cannot express.
    """
    feature = parent / name
    feature.mkdir(parents=True)
    if spec:
        (feature / "spec.md").write_text("# spec\n", encoding="utf-8")
    for fname, contents in files.items():
        (feature / fname).write_text(contents, encoding="utf-8")
    if retro:
        (feature / "RETRO.md").write_text("# retro\n", encoding="utf-8")
    return feature


class TestSdd050SharedCompleteness(unittest.TestCase):
    """SDD-050 Defect 1: shared validation_files/validation_complete helpers
    and split-file support in check_feature_dir."""

    def test_validation_files_globs_split_files_sorted(self):
        with tempfile.TemporaryDirectory() as tmp:
            feature = _make_split_dir(
                Path(tmp), "feat",
                files={
                    "validation-b.md": VALIDATION_COMPLETE,
                    "validation-a.md": VALIDATION_COMPLETE,
                },
            )
            files = done_check.validation_files(feature)
            names = [p.name for p in files]
            self.assertEqual(names, ["validation-a.md", "validation-b.md"])

    def test_validation_complete_true_single_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            feature = _make_dir(Path(tmp), "feat", validation=VALIDATION_COMPLETE)
            self.assertTrue(done_check.validation_complete(feature))

    def test_validation_complete_true_across_split_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            feature = _make_split_dir(
                Path(tmp), "feat",
                files={
                    "validation-a.md": VALIDATION_COMPLETE,
                    "validation-b.md": VALIDATION_COMPLETE,
                },
            )
            self.assertTrue(done_check.validation_complete(feature))

    def test_validation_complete_false_when_any_required_unchecked(self):
        with tempfile.TemporaryDirectory() as tmp:
            feature = _make_split_dir(
                Path(tmp), "feat",
                files={
                    "validation-a.md": VALIDATION_COMPLETE,
                    "validation-b.md": VALIDATION_UNCHECKED,
                },
            )
            self.assertFalse(done_check.validation_complete(feature))

    def test_validation_complete_false_when_no_validation_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            feature = Path(tmp) / "feat"
            feature.mkdir()
            (feature / "spec.md").write_text("# spec\n", encoding="utf-8")
            self.assertFalse(done_check.validation_complete(feature))

    def test_split_validation_unchecked_required_is_flagged(self):
        with tempfile.TemporaryDirectory() as tmp:
            feature = _make_split_dir(
                Path(tmp), "feat",
                files={
                    "validation-a.md": VALIDATION_COMPLETE,
                    "validation-b.md": VALIDATION_UNCHECKED,
                },
            )
            problems = done_check.check_feature_dir(feature)
            self.assertTrue(any("R-2" in p for p in problems), problems)

    def test_split_validation_all_complete_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            feature = _make_split_dir(
                Path(tmp), "feat",
                files={
                    "validation-a.md": VALIDATION_COMPLETE,
                    "validation-b.md": VALIDATION_COMPLETE,
                },
            )
            problems = done_check.check_feature_dir(feature)
            self.assertEqual(problems, [])


if __name__ == "__main__":
    unittest.main()
