"""Tests for cli/schema_lint.py UI Lifecycle Variant (SDD-018).

Covers:

- AC-1 / R-1  -- `UIVariantMarkerRecognition`
- AC-2 / R-2  -- `DeltaEntrySchema`
- AC-3 / R-3  -- `DeltaAppendOnlyAndErrorPrefix` (append-only via git heuristic)
- AC-4 / R-4  -- `DeltaAppendOnlyAndErrorPrefix` (`[delta]` prefix in human +
                 JSON; non-variant spec dirs unaffected)
- AC-5 / R-5  -- `RetroactiveDemoPathAllowlist`
- AC-6 / R-6  -- `StateDashboardDemoMigration` (real-repo spot check)
- AC-7 / R-7  -- `ADR014ExistsAndShapeChecks`
- AC-9 / R-9  -- `DocsPageExistsAndCrossLinks`

Stdlib only. Pattern mirrors test_schema_lint.py: tempfile sandbox +
direct invocation of schema_lint.scan() / check_validation_variant().
"""

from __future__ import annotations

import gc
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

THIS = Path(__file__).resolve()
SDD_ROOT = THIS.parents[1]
CLI_DIR = SDD_ROOT / "cli"
SCHEMA_LINT = CLI_DIR / "schema_lint.py"
REPO_ROOT = SDD_ROOT.parent

sys.path.insert(0, str(CLI_DIR))
import schema_lint  # noqa: E402


# ----------------------------------------------------------------------- #
# Helpers
# ----------------------------------------------------------------------- #

GOOD_SPEC = """---
id: SDD-X
type: spec
status: active
owner: principal-architect
updated: 2026-06-08
---
# body
"""

GOOD_VALIDATION = """---
id: SDD-X-val
type: validation
status: active
owner: principal-architect
updated: 2026-06-08
---
# body
"""


def _write(p: Path, content: str) -> Path:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return p


def _spec_with_marker(marker_value: str | None) -> str:
    if marker_value is None:
        return GOOD_SPEC
    return (
        "---\n"
        "id: SDD-X\n"
        "type: spec\n"
        "status: active\n"
        "owner: principal-architect\n"
        "updated: 2026-06-08\n"
        f"ui-variant: {marker_value}\n"
        "---\n# body\n"
    )


def _validation_with_delta(delta_section: str) -> str:
    return (
        "---\n"
        "id: SDD-X-val\n"
        "type: validation\n"
        "status: active\n"
        "owner: principal-architect\n"
        "updated: 2026-06-08\n"
        "---\n"
        "# Validation Contract\n\n"
        "- [x] R-1 -- placeholder REQUIRED\n\n"
        f"{delta_section}\n"
    )


WELL_FORMED_DELTA = (
    "## Delta Entries\n\n"
    "### Delta DE-01 -- example\n\n"
    "- timestamp: 2026-06-08T12:00:00Z\n"
    "- author: principal-software-developer\n"
    "- rationale: example rationale text\n"
    "- item-type: add\n\n"
    "Body of the delta entry.\n"
)


def _has_delta(findings, substr: str) -> bool:
    return any(
        f.kind == "delta" and substr in f.issue
        for f in findings
    )


# ----------------------------------------------------------------------- #
# AC-1 / R-1: UIVariantMarkerRecognition
# ----------------------------------------------------------------------- #

class UIVariantMarkerRecognition(unittest.TestCase):
    """The marker on spec.md dispatches validation.md to the variant
    validator. Absent or False keeps strict behavior."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.tmp = Path(self._tmp.name)
        self.specs = self.tmp / "specs" / "demo-feature"
        self.specs.mkdir(parents=True)

    def tearDown(self):
        gc.collect()
        self._tmp.cleanup()

    def test_marker_true_dispatches_to_variant_validator(self):
        _write(self.specs / "spec.md", _spec_with_marker("true"))
        # Validation has a well-formed delta entry -- only the variant
        # validator parses it; strict mode would still pass (no schema
        # complaint) because the base contract is satisfied.
        _write(self.specs / "validation.md",
               _validation_with_delta(WELL_FORMED_DELTA))
        findings = schema_lint.scan(self.tmp, paths=[self.specs])
        self.assertEqual(findings, [],
                         f"unexpected findings: {[(f.kind, f.issue) for f in findings]}")

        # Now break the entry; strict mode would not catch this, so the
        # appearance of a `[delta]` finding proves variant dispatch.
        bad_delta = (
            "## Delta Entries\n\n"
            "### Delta DE-01 -- broken\n\n"
            "- timestamp: 2026-06-08T12:00:00Z\n"
            "- author: principal-software-developer\n"
            "- item-type: add\n\n"
            "Body.\n"
        )
        _write(self.specs / "validation.md",
               _validation_with_delta(bad_delta))
        findings = schema_lint.scan(self.tmp, paths=[self.specs])
        self.assertTrue(_has_delta(findings, "rationale"),
                        f"expected [delta] rationale finding; got {findings}")

    def test_marker_false_keeps_strict_behavior(self):
        _write(self.specs / "spec.md", _spec_with_marker("false"))
        # Place a malformed delta section -- strict mode does NOT parse it,
        # so no [delta] findings should fire.
        bad_delta = (
            "## Delta Entries\n\n"
            "### Delta DE-01 -- ignored\n\n"
            "- item-type: bogus-type\n\n"
            "Body.\n"
        )
        _write(self.specs / "validation.md",
               _validation_with_delta(bad_delta))
        findings = schema_lint.scan(self.tmp, paths=[self.specs])
        delta_findings = [f for f in findings if f.kind == "delta"]
        self.assertEqual(delta_findings, [],
                         f"strict mode must not run delta validator: {delta_findings}")

    def test_marker_absent_keeps_strict_behavior(self):
        _write(self.specs / "spec.md", GOOD_SPEC)  # no marker key
        bad_delta = (
            "## Delta Entries\n\n"
            "### Delta DE-01 -- ignored\n\n"
            "- item-type: bogus-type\n\n"
            "Body.\n"
        )
        _write(self.specs / "validation.md",
               _validation_with_delta(bad_delta))
        findings = schema_lint.scan(self.tmp, paths=[self.specs])
        delta_findings = [f for f in findings if f.kind == "delta"]
        self.assertEqual(delta_findings, [],
                         f"absent marker must keep strict mode: {delta_findings}")

    def test_marker_malformed_value_is_lint_error(self):
        _write(self.specs / "spec.md", _spec_with_marker("yes"))
        _write(self.specs / "validation.md", GOOD_VALIDATION)
        findings = schema_lint.scan(self.tmp, paths=[self.specs])
        self.assertTrue(_has_delta(findings, "ui-variant marker must be"),
                        f"expected malformed-marker finding; got {findings}")


# ----------------------------------------------------------------------- #
# AC-2 / R-2: DeltaEntrySchema
# ----------------------------------------------------------------------- #

class DeltaEntrySchema(unittest.TestCase):
    """Mandatory-field presence, enum membership, monotonic IDs."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.tmp = Path(self._tmp.name)
        self.specs = self.tmp / "specs" / "demo-feature"
        self.specs.mkdir(parents=True)
        _write(self.specs / "spec.md", _spec_with_marker("true"))

    def tearDown(self):
        gc.collect()
        self._tmp.cleanup()

    def _scan_with_delta(self, delta: str):
        _write(self.specs / "validation.md", _validation_with_delta(delta))
        return schema_lint.scan(self.tmp, paths=[self.specs])

    def test_well_formed_entry_passes(self):
        findings = self._scan_with_delta(WELL_FORMED_DELTA)
        delta_findings = [f for f in findings if f.kind == "delta"]
        self.assertEqual(delta_findings, [],
                         f"well-formed entry should pass: {delta_findings}")

    def test_missing_timestamp_yields_delta_error(self):
        delta = (
            "## Delta Entries\n\n"
            "### Delta DE-01 -- no-ts\n\n"
            "- author: principal-software-developer\n"
            "- rationale: x\n"
            "- item-type: add\n\nBody.\n"
        )
        findings = self._scan_with_delta(delta)
        self.assertTrue(_has_delta(findings, "missing mandatory field 'timestamp'"),
                        findings)

    def test_missing_author_yields_delta_error(self):
        delta = (
            "## Delta Entries\n\n"
            "### Delta DE-01 -- no-author\n\n"
            "- timestamp: 2026-06-08T12:00:00Z\n"
            "- rationale: x\n"
            "- item-type: add\n\nBody.\n"
        )
        findings = self._scan_with_delta(delta)
        self.assertTrue(_has_delta(findings, "missing mandatory field 'author'"),
                        findings)

    def test_missing_item_type_yields_delta_error(self):
        delta = (
            "## Delta Entries\n\n"
            "### Delta DE-01 -- no-type\n\n"
            "- timestamp: 2026-06-08T12:00:00Z\n"
            "- author: x\n"
            "- rationale: x\n\nBody.\n"
        )
        findings = self._scan_with_delta(delta)
        self.assertTrue(_has_delta(findings, "missing mandatory field 'item-type'"),
                        findings)

    def test_missing_rationale_yields_delta_error(self):
        delta = (
            "## Delta Entries\n\n"
            "### Delta DE-01 -- no-rationale\n\n"
            "- timestamp: 2026-06-08T12:00:00Z\n"
            "- author: x\n"
            "- item-type: add\n\nBody.\n"
        )
        findings = self._scan_with_delta(delta)
        self.assertTrue(_has_delta(findings, "missing mandatory field 'rationale'"),
                        findings)

    def test_item_type_outside_enum_yields_delta_error(self):
        delta = (
            "## Delta Entries\n\n"
            "### Delta DE-01 -- bogus\n\n"
            "- timestamp: 2026-06-08T12:00:00Z\n"
            "- author: x\n"
            "- rationale: x\n"
            "- item-type: not-a-real-type\n\nBody.\n"
        )
        findings = self._scan_with_delta(delta)
        self.assertTrue(_has_delta(findings, "item-type 'not-a-real-type' not in enum"),
                        findings)

    def test_de_id_non_monotonic_yields_delta_error(self):
        delta = (
            "## Delta Entries\n\n"
            "### Delta DE-02 -- first\n\n"
            "- timestamp: 2026-06-08T12:00:00Z\n"
            "- author: x\n"
            "- rationale: x\n"
            "- item-type: add\n\nBody.\n\n"
            "### Delta DE-01 -- second\n\n"
            "- timestamp: 2026-06-08T13:00:00Z\n"
            "- author: x\n"
            "- rationale: x\n"
            "- item-type: add\n\nBody.\n"
        )
        findings = self._scan_with_delta(delta)
        self.assertTrue(_has_delta(findings, "not monotonically increasing"),
                        findings)

    def test_bad_timestamp_format_yields_delta_error(self):
        delta = (
            "## Delta Entries\n\n"
            "### Delta DE-01 -- bad-ts\n\n"
            "- timestamp: 2026/06/08 noon\n"
            "- author: x\n"
            "- rationale: x\n"
            "- item-type: add\n\nBody.\n"
        )
        findings = self._scan_with_delta(delta)
        self.assertTrue(_has_delta(findings, "not ISO 8601"), findings)

    def test_empty_delta_section_is_valid(self):
        """R-16 edge case: zero entries is a valid state."""
        delta = "## Delta Entries\n\n(no entries yet)\n"
        findings = self._scan_with_delta(delta)
        delta_findings = [f for f in findings if f.kind == "delta"]
        self.assertEqual(delta_findings, [],
                         f"empty section must be valid: {delta_findings}")


# ----------------------------------------------------------------------- #
# AC-3 + AC-4 / R-3 + R-4: DeltaAppendOnlyAndErrorPrefix
# ----------------------------------------------------------------------- #

class DeltaAppendOnlyAndErrorPrefix(unittest.TestCase):
    """[delta] prefix in human + JSON output; non-variant unaffected;
    append-only enforcement via in-memory + git heuristic."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.tmp = Path(self._tmp.name)
        self.specs = self.tmp / "specs" / "demo-feature"
        self.specs.mkdir(parents=True)
        _write(self.specs / "spec.md", _spec_with_marker("true"))

    def tearDown(self):
        gc.collect()
        self._tmp.cleanup()

    def test_delta_findings_carry_delta_prefix_in_human_output(self):
        bad = (
            "## Delta Entries\n\n"
            "### Delta DE-01 -- bad\n\n"
            "- timestamp: 2026-06-08T12:00:00Z\n"
            "- author: x\n"
            "- item-type: add\n\nBody.\n"
        )
        _write(self.specs / "validation.md", _validation_with_delta(bad))
        findings = schema_lint.scan(self.tmp, paths=[self.specs])
        human = schema_lint.render_human(findings, self.tmp)
        self.assertIn("[delta]", human, human)

    def test_delta_findings_carry_delta_prefix_in_json_output(self):
        bad = (
            "## Delta Entries\n\n"
            "### Delta DE-01 -- bad\n\n"
            "- timestamp: 2026-06-08T12:00:00Z\n"
            "- author: x\n"
            "- item-type: add\n\nBody.\n"
        )
        _write(self.specs / "validation.md", _validation_with_delta(bad))
        findings = schema_lint.scan(self.tmp, paths=[self.specs])
        payload = json.loads(schema_lint.render_json(findings))
        delta_items = [
            item for item in payload
            if item.get("kind") == "delta" and item.get("issue", "").startswith("[delta]")
        ]
        self.assertTrue(delta_items, payload)

    def test_non_variant_spec_dir_unaffected_by_variant_rules(self):
        """Two spec dirs: one variant (good), one strict (with a malformed
        delta section that strict mode MUST ignore). Result: strict dir
        produces zero [delta] findings."""
        strict_dir = self.tmp / "specs" / "strict-feature"
        strict_dir.mkdir(parents=True)
        _write(strict_dir / "spec.md", GOOD_SPEC)  # no marker
        bad_delta = (
            "## Delta Entries\n\n"
            "### Delta DE-01 -- ignored\n\n"
            "- item-type: bogus\n\nBody.\n"
        )
        _write(strict_dir / "validation.md",
               _validation_with_delta(bad_delta))

        _write(self.specs / "validation.md",
               _validation_with_delta(WELL_FORMED_DELTA))

        findings = schema_lint.scan(self.tmp, paths=[self.tmp / "specs"])
        delta_findings_strict = [
            f for f in findings
            if f.kind == "delta" and "strict-feature" in f.path
        ]
        self.assertEqual(delta_findings_strict, [],
                         f"strict dir leaked delta findings: {delta_findings_strict}")

    def test_append_only_git_heuristic_detects_field_mutation(self):
        """Initialize a fresh git repo, commit a baseline delta, mutate
        the rationale, re-lint. Expect a [delta] append-only finding."""
        git = "git"
        try:
            r = subprocess.run([git, "--version"], capture_output=True,
                               text=True, timeout=5)
            if r.returncode != 0:
                self.skipTest("git not available")
        except (FileNotFoundError, subprocess.TimeoutExpired):
            self.skipTest("git not available")

        env = dict(os.environ)
        env["GIT_AUTHOR_NAME"] = "tester"
        env["GIT_AUTHOR_EMAIL"] = "tester@example.com"
        env["GIT_COMMITTER_NAME"] = "tester"
        env["GIT_COMMITTER_EMAIL"] = "tester@example.com"

        subprocess.run([git, "init", "-q"], cwd=str(self.tmp), env=env,
                       check=True, timeout=10)
        subprocess.run([git, "config", "user.email", "tester@example.com"],
                       cwd=str(self.tmp), env=env, check=True, timeout=5)
        subprocess.run([git, "config", "user.name", "tester"],
                       cwd=str(self.tmp), env=env, check=True, timeout=5)

        _write(self.specs / "validation.md",
               _validation_with_delta(WELL_FORMED_DELTA))
        subprocess.run([git, "add", "."], cwd=str(self.tmp), env=env,
                       check=True, timeout=10)
        subprocess.run([git, "commit", "-q", "-m", "baseline"],
                       cwd=str(self.tmp), env=env, check=True, timeout=10)

        # Mutate the rationale of DE-01
        mutated = WELL_FORMED_DELTA.replace(
            "rationale: example rationale text",
            "rationale: TOTALLY DIFFERENT TEXT",
        )
        _write(self.specs / "validation.md",
               _validation_with_delta(mutated))

        findings = schema_lint.scan(self.tmp, paths=[self.specs])
        self.assertTrue(_has_delta(findings, "field 'rationale' modified"),
                        f"expected append-only mutation finding; got {findings}")

    def test_append_only_git_heuristic_detects_deletion(self):
        """Commit two DE entries, delete the older one, expect a deletion
        violation."""
        try:
            r = subprocess.run(["git", "--version"], capture_output=True,
                               text=True, timeout=5)
            if r.returncode != 0:
                self.skipTest("git not available")
        except (FileNotFoundError, subprocess.TimeoutExpired):
            self.skipTest("git not available")

        env = dict(os.environ)
        env["GIT_AUTHOR_NAME"] = "tester"
        env["GIT_AUTHOR_EMAIL"] = "tester@example.com"
        env["GIT_COMMITTER_NAME"] = "tester"
        env["GIT_COMMITTER_EMAIL"] = "tester@example.com"

        subprocess.run(["git", "init", "-q"], cwd=str(self.tmp), env=env,
                       check=True, timeout=10)
        subprocess.run(["git", "config", "user.email", "tester@example.com"],
                       cwd=str(self.tmp), env=env, check=True, timeout=5)
        subprocess.run(["git", "config", "user.name", "tester"],
                       cwd=str(self.tmp), env=env, check=True, timeout=5)

        two_entries = (
            "## Delta Entries\n\n"
            "### Delta DE-01 -- first\n\n"
            "- timestamp: 2026-06-08T12:00:00Z\n"
            "- author: x\n"
            "- rationale: r1\n"
            "- item-type: add\n\nBody one.\n\n"
            "### Delta DE-02 -- second\n\n"
            "- timestamp: 2026-06-08T13:00:00Z\n"
            "- author: x\n"
            "- rationale: r2\n"
            "- item-type: add\n\nBody two.\n"
        )
        _write(self.specs / "validation.md",
               _validation_with_delta(two_entries))
        subprocess.run(["git", "add", "."], cwd=str(self.tmp), env=env,
                       check=True, timeout=10)
        subprocess.run(["git", "commit", "-q", "-m", "baseline"],
                       cwd=str(self.tmp), env=env, check=True, timeout=10)

        # Delete DE-01
        one_entry = (
            "## Delta Entries\n\n"
            "### Delta DE-02 -- second\n\n"
            "- timestamp: 2026-06-08T13:00:00Z\n"
            "- author: x\n"
            "- rationale: r2\n"
            "- item-type: add\n\nBody two.\n"
        )
        _write(self.specs / "validation.md",
               _validation_with_delta(one_entry))
        findings = schema_lint.scan(self.tmp, paths=[self.specs])
        self.assertTrue(_has_delta(findings, "DE-01 deleted"),
                        f"expected DE-01 deletion finding; got {findings}")


# ----------------------------------------------------------------------- #
# AC-5 / R-5: RetroactiveDemoPathAllowlist
# ----------------------------------------------------------------------- #

class RetroactiveDemoPathAllowlist(unittest.TestCase):
    """Only `specs/2026-05-16-state-dashboard/` may use
    `item-type: retroactive-demo`."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.tmp = Path(self._tmp.name)

    def tearDown(self):
        gc.collect()
        self._tmp.cleanup()

    def _make_spec_dir(self, segment: str) -> Path:
        d = self.tmp / "specs" / segment
        d.mkdir(parents=True)
        _write(d / "spec.md", _spec_with_marker("true"))
        return d

    @staticmethod
    def _retro_delta() -> str:
        return (
            "## Delta Entries\n\n"
            "### Delta DE-01 -- retro\n\n"
            "- timestamp: 2026-06-08T12:00:00Z\n"
            "- author: x\n"
            "- rationale: testing the allow-list\n"
            "- item-type: retroactive-demo\n\nBody.\n"
        )

    def test_retroactive_demo_in_non_allowlisted_dir_fails(self):
        d = self._make_spec_dir("some-other-feature")
        _write(d / "validation.md",
               _validation_with_delta(self._retro_delta()))
        findings = schema_lint.scan(self.tmp, paths=[self.tmp / "specs"])
        self.assertTrue(_has_delta(findings, "retroactive-demo permitted only"),
                        f"expected retroactive-demo allow-list finding; got {findings}")

    def test_retroactive_demo_in_allowlisted_dir_passes(self):
        d = self._make_spec_dir("2026-05-16-state-dashboard")
        _write(d / "validation.md",
               _validation_with_delta(self._retro_delta()))
        findings = schema_lint.scan(self.tmp, paths=[self.tmp / "specs"])
        retro_findings = [
            f for f in findings if "retroactive-demo permitted only" in f.issue
        ]
        self.assertEqual(retro_findings, [],
                         f"allow-listed dir must pass: {retro_findings}")


# ----------------------------------------------------------------------- #
# AC-6 / R-6: StateDashboardDemoMigration  (real-repo spot check)
# ----------------------------------------------------------------------- #

class StateDashboardDemoMigration(unittest.TestCase):
    """The live state-dashboard spec dir, post-migration, must carry the
    marker on spec.md, carry exactly one DE-01 retroactive-demo entry on
    validation.md, and lint clean."""

    SPEC_DIR = (REPO_ROOT / "spec-driven-development" / "specs"
                / "2026-05-16-state-dashboard")

    def test_spec_md_has_ui_variant_marker(self):
        spec_text = (self.SPEC_DIR / "spec.md").read_text(encoding="utf-8")
        self.assertIn("ui-variant: true", spec_text,
                      "state-dashboard spec.md must carry ui-variant: true "
                      "after T-018-04 migration")

    def test_validation_md_has_de01_retroactive_demo(self):
        text = (self.SPEC_DIR / "validation.md").read_text(encoding="utf-8")
        self.assertIn("## Delta Entries", text)
        entries = schema_lint._parse_delta_entries(text)
        self.assertEqual(len(entries), 1, entries)
        self.assertEqual(entries[0]["de_id"], "DE-01")
        self.assertEqual(entries[0]["raw_fields"].get("item-type"),
                         "retroactive-demo")

    def test_state_dashboard_lints_clean(self):
        findings = schema_lint.scan(REPO_ROOT, paths=[self.SPEC_DIR])
        self.assertEqual(findings, [],
                         f"state-dashboard demo must lint clean post-T-018-04: "
                         f"{[(f.kind, f.issue) for f in findings]}")

    def test_v02_additions_subsection_preserved(self):
        """Lock-surface protection 7: existing `## v0.2 additions`
        subsection must remain byte-identical."""
        text = (self.SPEC_DIR / "validation.md").read_text(encoding="utf-8")
        self.assertIn("## v0.2 additions (2026-05-16, post user UX feedback)", text)
        # Spot-check that at least one of the original [x] checkboxes remains
        self.assertIn(
            "- [x] Live server mode: `python state_builder.py serve` starts "
            "a local ThreadingHTTPServer on port 8765",
            text,
        )


# ----------------------------------------------------------------------- #
# AC-7 / R-7: ADR014ExistsAndShapeChecks
# ----------------------------------------------------------------------- #

class ADR014ExistsAndShapeChecks(unittest.TestCase):
    """ADR-014 exists, status `proposed`, includes proposed Article XII text."""

    ADR_PATH = (REPO_ROOT / "spec-driven-development" / "docs" / "ADR"
                / "014-ui-lifecycle-variant.md")

    def test_adr014_file_exists(self):
        self.assertTrue(self.ADR_PATH.is_file(),
                        f"ADR-014 missing at {self.ADR_PATH}")

    def test_adr014_status_is_proposed(self):
        text = self.ADR_PATH.read_text(encoding="utf-8")
        # Top-of-body status line (not the frontmatter status, which is the
        # carrier `draft` per the ADR-013 precedent recorded in the spec).
        self.assertIn("status: proposed", text.lower(),
                      "ADR-014 must carry top status: proposed (lowercase) "
                      "until owner ratification")

    def test_adr014_carries_proposed_article_xii_text(self):
        text = self.ADR_PATH.read_text(encoding="utf-8")
        self.assertTrue(
            "Proposed Article XII" in text or "## Proposed Article XII text" in text,
            "ADR-014 must include a 'Proposed Article XII text' section",
        )


# ----------------------------------------------------------------------- #
# AC-9 / R-9 / R-10: DocsPageExistsAndCrossLinks
# ----------------------------------------------------------------------- #

class DocsPageExistsAndCrossLinks(unittest.TestCase):
    """The single-page authoring guide exists and is referenced from the
    templates + ADR-014."""

    DOCS_PATH = (REPO_ROOT / "spec-driven-development" / "docs"
                 / "UI-LIFECYCLE-VARIANT.md")
    TEMPLATE_SPEC = (REPO_ROOT / "spec-driven-development" / "templates"
                     / "feature-spec.md")
    TEMPLATE_VAL = (REPO_ROOT / "spec-driven-development" / "templates"
                    / "validation.md")
    ADR_PATH = (REPO_ROOT / "spec-driven-development" / "docs" / "ADR"
                / "014-ui-lifecycle-variant.md")

    def test_docs_page_exists(self):
        self.assertTrue(self.DOCS_PATH.is_file(),
                        f"UI-LIFECYCLE-VARIANT.md missing at {self.DOCS_PATH}")

    def test_docs_page_has_required_sections(self):
        text = self.DOCS_PATH.read_text(encoding="utf-8")
        for required in (
            "marker", "Delta", "item-type", "retroactive-demo",
            "state-dashboard", "status: blocked",
        ):
            self.assertIn(required, text,
                          f"docs page missing required mention: '{required}'")

    def test_feature_spec_template_references_docs_page(self):
        text = self.TEMPLATE_SPEC.read_text(encoding="utf-8")
        self.assertIn("UI-LIFECYCLE-VARIANT.md", text,
                      "feature-spec.md template must link to docs page")
        self.assertIn("ui-variant: true", text,
                      "feature-spec.md template must show the marker (commented)")

    def test_validation_template_references_docs_page(self):
        text = self.TEMPLATE_VAL.read_text(encoding="utf-8")
        self.assertIn("UI-LIFECYCLE-VARIANT.md", text,
                      "validation.md template must link to docs page")
        self.assertIn("Delta Entries", text,
                      "validation.md template must show the section stub")

    def test_adr014_references_docs_page(self):
        text = self.ADR_PATH.read_text(encoding="utf-8")
        self.assertIn("UI-LIFECYCLE-VARIANT.md", text,
                      "ADR-014 must link to the docs page")


if __name__ == "__main__":
    unittest.main()
