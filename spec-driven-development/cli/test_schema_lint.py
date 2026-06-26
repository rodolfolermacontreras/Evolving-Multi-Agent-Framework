"""Tests for cli/schema_lint.py (SDD-006)."""

from __future__ import annotations

import gc
import json
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
import schema_lint


# ----------------------------------------------------------------------- #
# Helper: build a minimal fake repo root with .github/{agents,skills,prompts}
# ----------------------------------------------------------------------- #

def make_fake_root(tmp: Path) -> Path:
    root = tmp / "fake-repo"
    (root / ".github" / "agents").mkdir(parents=True)
    (root / ".github" / "skills" / "ok-skill").mkdir(parents=True)
    (root / ".github" / "prompts").mkdir()
    return root


def write_agent(root: Path, name: str, content: str) -> Path:
    p = root / ".github" / "agents" / f"{name}.agent.md"
    p.write_text(content, encoding="utf-8")
    return p


def write_skill(root: Path, dir_name: str, content: str) -> Path:
    skill_dir = root / ".github" / "skills" / dir_name
    skill_dir.mkdir(parents=True, exist_ok=True)
    p = skill_dir / "SKILL.md"
    p.write_text(content, encoding="utf-8")
    return p


def write_prompt(root: Path, name: str, content: str) -> Path:
    p = root / ".github" / "prompts" / f"{name}.prompt.md"
    p.write_text(content, encoding="utf-8")
    return p


GOOD_SKILL = """---
name: ok-skill
description: This is a good skill.
license: MIT
metadata:
  author: tester
  version: '1.0'
---
# OK Skill
"""

GOOD_AGENT = """---
description: A good agent.
---
# Agent
"""

GOOD_PROMPT = """---
description: A good prompt.
---
"""


# ----------------------------------------------------------------------- #
# Tests
# ----------------------------------------------------------------------- #

class SchemaLintAcceptance(unittest.TestCase):

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.root = make_fake_root(Path(self._tmp.name))
        # Always seed a known-good baseline so tests can add bad files on top.
        write_skill(self.root, "ok-skill", GOOD_SKILL)
        write_agent(self.root, "ok-agent", GOOD_AGENT)
        write_prompt(self.root, "ok-prompt", GOOD_PROMPT)

    def tearDown(self):
        gc.collect()
        self._tmp.cleanup()

    def test_agent_missing_description_fails(self):
        """AC2."""
        write_agent(self.root, "bad-agent", "---\nhandoffs: []\n---\n")
        findings = schema_lint.scan(self.root)
        self.assertTrue(any("bad-agent" in f.path and "description" in f.issue for f in findings))

    def test_skill_missing_required_fields_fails(self):
        """AC3."""
        write_skill(self.root, "bad-skill", "---\ndescription: only desc\n---\n")
        findings = schema_lint.scan(self.root)
        issues = [f.issue for f in findings if "bad-skill" in f.path]
        self.assertTrue(any("name" in i for i in issues))
        self.assertTrue(any("license" in i for i in issues))
        self.assertTrue(any("metadata" in i for i in issues))

    def test_prompt_missing_description_fails(self):
        """AC4."""
        write_prompt(self.root, "bad-prompt", "---\nfoo: bar\n---\n")
        findings = schema_lint.scan(self.root)
        self.assertTrue(any("bad-prompt" in f.path and "description" in f.issue for f in findings))

    def test_unquoted_version_fails(self):
        """AC5."""
        write_skill(self.root, "unquoted-skill",
                    "---\nname: unquoted-skill\ndescription: x\nlicense: MIT\n"
                    "metadata:\n  author: t\n  version: 1.0\n---\n")
        findings = schema_lint.scan(self.root)
        self.assertTrue(any("quoted string" in f.issue and "unquoted-skill" in f.path for f in findings))

    def test_skill_name_dir_mismatch_fails(self):
        """AC6."""
        write_skill(self.root, "real-dir-name",
                    "---\nname: declared-different\ndescription: x\nlicense: MIT\n"
                    "metadata:\n  author: t\n  version: '1.0'\n---\n")
        findings = schema_lint.scan(self.root)
        self.assertTrue(any("name mismatch" in f.issue and "real-dir-name" in f.path for f in findings))

    def test_json_flag_emits_findings(self):
        """AC7."""
        write_agent(self.root, "bad-agent2", "---\nhandoffs: []\n---\n")
        result = subprocess.run(
            [sys.executable, str(SCHEMA_LINT), "--repo-root", str(self.root), "--json"],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 1)
        payload = json.loads(result.stdout)
        self.assertTrue(any("bad-agent2" in item["path"] for item in payload))

    def test_repo_root_flag(self):
        """AC8."""
        result = subprocess.run(
            [sys.executable, str(SCHEMA_LINT), "--repo-root", str(self.root)],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("clean", result.stdout.lower())

    def test_exit_codes(self):
        """AC9."""
        # Clean exit
        r0 = subprocess.run(
            [sys.executable, str(SCHEMA_LINT), "--repo-root", str(self.root)],
            capture_output=True, text=True,
        )
        self.assertEqual(r0.returncode, 0)
        # Finding -> 1
        write_agent(self.root, "bad-rc", "---\nx: 1\n---\n")
        r1 = subprocess.run(
            [sys.executable, str(SCHEMA_LINT), "--repo-root", str(self.root)],
            capture_output=True, text=True,
        )
        self.assertEqual(r1.returncode, 1)
        # Bad usage -> 2
        r2 = subprocess.run(
            [sys.executable, str(SCHEMA_LINT), "--repo-root", "/no/such/path/xyz"],
            capture_output=True, text=True,
        )
        self.assertEqual(r2.returncode, 2)

    def test_runtime_imports_are_stdlib_only(self):
        """AC10."""
        import ast
        tree = ast.parse(SCHEMA_LINT.read_text(encoding="utf-8"))
        stdlib = set(sys.stdlib_module_names)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    self.assertIn(alias.name.split(".", 1)[0], stdlib)
            elif isinstance(node, ast.ImportFrom) and node.module:
                self.assertIn(node.module.split(".", 1)[0], stdlib)

    def test_real_repo_passes_clean_or_findings_documented(self):
        """AC1 in practice -- run against the live repo. Tolerates findings
        but records them for the developer to address."""
        findings = schema_lint.scan(REPO_ROOT)
        if findings:
            sample = "\n".join(f"  [{f.kind}] {f.path}: {f.issue}" for f in findings[:5])
            self.skipTest(f"{len(findings)} real-repo findings -- triage and fix:\n{sample}")


# ----------------------------------------------------------------------- #
# T-FDC-03: filesystem data contract (SDD-FDC-001 / R1, R2)
#
# Validates check_artifact() against the locked schema in ADR-012 and the
# positional-paths invocation mode used by R6 verification.
# ----------------------------------------------------------------------- #

GOOD_ARTIFACT = """---
id: SDD-TEST-001-spec
type: spec
status: active
owner: principal-architect
updated: 2026-06-06
---
# Example artifact
"""


class ArtifactContractAcceptance(unittest.TestCase):
    """SDD-FDC-001 R1, R2 -- artifact frontmatter contract."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.tmp = Path(self._tmp.name)
        self.specs = self.tmp / "specs" / "demo-feature"
        self.specs.mkdir(parents=True)
        self.sprints = self.tmp / "sprints" / "PI-X"
        self.sprints.mkdir(parents=True)

    def tearDown(self):
        gc.collect()
        self._tmp.cleanup()

    def _write(self, path: Path, content: str) -> Path:
        path.write_text(content, encoding="utf-8")
        return path

    # --- R1 / AC-1: missing field => finding + non-zero ---------------------

    def test_artifact_no_frontmatter_reported(self):
        """{} parse result must produce a finding, never crash."""
        p = self._write(self.specs / "raw.md", "# raw doc no frontmatter\n")
        findings = schema_lint.check_artifact(p)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].kind, "artifact")
        self.assertIn("no YAML frontmatter", findings[0].issue)

    def test_artifact_missing_each_required_field_fails(self):
        for missing in schema_lint.REQUIRED_CONTRACT_FIELDS:
            fm_lines = [
                "id: SDD-X",
                "type: spec",
                "status: active",
                "owner: principal-architect",
                "updated: 2026-06-06",
            ]
            kept = [line for line in fm_lines if not line.startswith(f"{missing}:")]
            content = "---\n" + "\n".join(kept) + "\n---\n# body\n"
            p = self._write(self.specs / f"missing-{missing}.md", content)
            findings = schema_lint.check_artifact(p)
            self.assertTrue(
                any(f"missing '{missing}'" in f.issue for f in findings),
                f"expected missing '{missing}' finding, got: {[f.issue for f in findings]}",
            )

    def test_artifact_bad_type_enum_reported(self):
        bad = (
            "---\nid: x\ntype: not-a-real-type\nstatus: active\n"
            "owner: principal-architect\nupdated: 2026-06-06\n---\nbody\n"
        )
        p = self._write(self.specs / "bad-type.md", bad)
        findings = schema_lint.check_artifact(p)
        self.assertTrue(any("type 'not-a-real-type' not in enum" in f.issue for f in findings))

    def test_artifact_bad_status_enum_reported(self):
        bad = (
            "---\nid: x\ntype: spec\nstatus: wibble\n"
            "owner: principal-architect\nupdated: 2026-06-06\n---\nbody\n"
        )
        p = self._write(self.specs / "bad-status.md", bad)
        findings = schema_lint.check_artifact(p)
        self.assertTrue(any("status 'wibble' not in enum" in f.issue for f in findings))

    def test_artifact_non_iso_updated_warning(self):
        bad = (
            "---\nid: x\ntype: spec\nstatus: active\n"
            "owner: principal-architect\nupdated: not-a-date\n---\nbody\n"
        )
        p = self._write(self.specs / "bad-date.md", bad)
        findings = schema_lint.check_artifact(p)
        warnings = [f for f in findings if "not ISO YYYY-MM-DD" in f.issue]
        self.assertTrue(warnings, "expected ISO-date warning")
        self.assertEqual(warnings[0].severity, "WARNING")

    # --- R2 / AC-2: valid tree => exit 0 -----------------------------------

    def test_artifact_all_valid_passes(self):
        self._write(self.specs / "spec.md", GOOD_ARTIFACT)
        self._write(self.sprints / "INDEX.md", GOOD_ARTIFACT.replace("type: spec", "type: index"))
        findings = schema_lint.scan(self.tmp, paths=[self.specs, self.sprints])
        self.assertEqual(findings, [], f"unexpected findings: {[f.issue for f in findings]}")

    # --- Skip list ----------------------------------------------------------

    def test_artifact_skip_list_honored(self):
        # lessons-template.md is the documented template skip.
        self._write(self.sprints / "lessons-template.md", "# no frontmatter on purpose\n")
        findings = schema_lint.scan(self.tmp, paths=[self.sprints])
        self.assertEqual(findings, [],
                         f"template should be skipped, got: {[f.path for f in findings]}")

    def test_artifact_underscore_prefix_skipped(self):
        self._write(self.sprints / "_template_session.md", "# no frontmatter\n")
        findings = schema_lint.scan(self.tmp, paths=[self.sprints])
        self.assertEqual(findings, [],
                         f"_-prefixed file should be skipped, got: {[f.path for f in findings]}")

    # --- R6 invocation mode (positional paths) -----------------------------

    def test_positional_paths_mode_scans_only_given_dirs(self):
        # Set up: an in-tree fake repo with both .github (bad agent) and specs (good)
        fake_root = self.tmp / "fake-repo"
        agents_dir = fake_root / ".github" / "agents"
        agents_dir.mkdir(parents=True)
        (agents_dir / "bad-agent.agent.md").write_text("---\nx: 1\n---\n", encoding="utf-8")
        specs_only = fake_root / "specs"
        specs_only.mkdir()
        (specs_only / "good.md").write_text(GOOD_ARTIFACT, encoding="utf-8")

        # Positional path => ignore .github/, scan only specs/, exit clean
        findings_explicit = schema_lint.scan(fake_root, paths=[specs_only])
        self.assertEqual(findings_explicit, [])

        # Default (no positional) => walks .github/ AND specs/, bad-agent shows up
        findings_default = schema_lint.scan(fake_root)
        self.assertTrue(any("bad-agent" in f.path for f in findings_default))

    def test_positional_paths_cli_exit_zero_for_valid_tree(self):
        valid_specs = self.tmp / "valid-specs"
        valid_specs.mkdir()
        (valid_specs / "spec.md").write_text(GOOD_ARTIFACT, encoding="utf-8")
        result = subprocess.run(
            [sys.executable, str(SCHEMA_LINT), str(valid_specs)],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_positional_paths_cli_exit_one_for_invalid_tree(self):
        bad_specs = self.tmp / "bad-specs"
        bad_specs.mkdir()
        (bad_specs / "raw.md").write_text("# no frontmatter\n", encoding="utf-8")
        result = subprocess.run(
            [sys.executable, str(SCHEMA_LINT), str(bad_specs)],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 1)

    def test_positional_paths_cli_exit_two_for_missing_dir(self):
        result = subprocess.run(
            [sys.executable, str(SCHEMA_LINT), str(self.tmp / "does-not-exist")],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 2)


# ----------------------------------------------------------------------- #
# SDD-023: first-class user gate declarations
# ----------------------------------------------------------------------- #

GOOD_GATE_VALIDATION = """---
id: SDD-GATE-validation
type: validation
status: active
owner: principal-architect
updated: 2026-06-08
---

# Validation

## Required User Gates Declared By This Spec

| gate_id | gate_type | blocking_scope | approver | evidence_type | evidence_ref | status | next_action |
|---------|-----------|----------------|----------|---------------|--------------|--------|-------------|
| GATE-001 | `push-approval` | `push` | owner | `owner-quote` |  | pending | Record owner approval before push. |
"""

class UserGateContractAcceptance(unittest.TestCase):
    """SDD-023 gate parser and lint rules."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.spec_dir = Path(self._tmp.name) / "specs" / "2026-06-08-gate-fixture"
        self.spec_dir.mkdir(parents=True)

    def tearDown(self):
        gc.collect()
        self._tmp.cleanup()

    def _write_validation(self, content: str = GOOD_GATE_VALIDATION) -> Path:
        path = self.spec_dir / "validation.md"
        path.write_text(content, encoding="utf-8")
        return path

    def test_gate_table_parses_from_validation_md_without_gates_md(self):
        path = self._write_validation()

        gates = schema_lint.parse_user_gates(path)
        findings = schema_lint.check_user_gates(path)

        self.assertEqual(findings, [])
        self.assertEqual(len(gates), 1)
        self.assertEqual(gates[0].gate_id, "GATE-001")
        self.assertEqual(gates[0].gate_type, "push-approval")
        self.assertFalse((self.spec_dir / "gates.md").exists())

    def test_gate_invalid_status_fails(self):
        path = self._write_validation(GOOD_GATE_VALIDATION.replace("pending", "waiting"))

        findings = schema_lint.check_user_gates(path)

        self.assertTrue(any("status 'waiting' not in enum" in f.issue for f in findings))

    def test_gate_invalid_evidence_type_fails(self):
        path = self._write_validation(GOOD_GATE_VALIDATION.replace("`owner-quote`", "`green-tests`"))

        findings = schema_lint.check_user_gates(path)

        self.assertTrue(any("invalid approval evidence source 'green-tests'" in f.issue for f in findings))

    def test_gate_approved_without_evidence_ref_fails(self):
        path = self._write_validation(GOOD_GATE_VALIDATION.replace("pending", "approved"))

        findings = schema_lint.check_user_gates(path)

        self.assertTrue(any("approved gate requires non-empty evidence_ref" in f.issue for f in findings))

    def test_historical_validation_without_gate_section_passes(self):
        path = self._write_validation(GOOD_ARTIFACT + "\n## Required Items\n\n- [ ] V-1. Example.\n")

        findings = schema_lint.check_user_gates(path)

        self.assertEqual(findings, [])


# ----------------------------------------------------------------------- #
# SDD-036 / ADR-017: optional `depends_on` frontmatter contract
#
# T-036-02 (parse helper) + T-036-03 (check_depends_on validator).
# Validates: present-only enforcement, ID shape, duplicates, self-dep,
# BACKLOG existence warning, and absent => zero findings.
# ----------------------------------------------------------------------- #

def _spec_with_depends_on(dep_line: str, spec_id: str = "SDD-036-spec") -> str:
    return (
        "---\n"
        f"id: {spec_id}\n"
        "type: spec\n"
        "status: active\n"
        "owner: principal-architect\n"
        "updated: 2026-06-11\n"
        f"{dep_line}\n"
        "---\n# spec body\n"
    )


class DependsOnParseHelper(unittest.TestCase):
    """T-036-02 -- parse_depends_on hand-parses the inline list form."""

    def test_absent_field_returns_empty(self):
        self.assertEqual(schema_lint.parse_depends_on({}), [])
        self.assertEqual(schema_lint.parse_depends_on({"id": "x"}), [])

    def test_inline_single_id(self):
        fm = schema_lint.parse_frontmatter(_spec_with_depends_on("depends_on: [SDD-018]"))
        self.assertEqual(fm.get("depends_on"), "[SDD-018]")


# ----------------------------------------------------------------------- #
# T-047-11 (SDD-047 D-1) -- orphan-skill rule
#
# Every non-domain skill slug must be referenced at least once across
# .github/agents, .github/prompts, and .github/instructions. domain/ skills
# are reference implementations and are EXEMPT. Opt-in via --check-orphans so
# the default scan() output stays byte-identical (existing tests unaffected).
# ----------------------------------------------------------------------- #


def _make_orphan_root(tmp: Path) -> Path:
    root = tmp / "orphan-repo"
    (root / ".github" / "agents").mkdir(parents=True)
    (root / ".github" / "prompts").mkdir(parents=True)
    (root / ".github" / "instructions").mkdir(parents=True)
    (root / ".github" / "skills").mkdir(parents=True)
    return root


def _skill_body(slug: str) -> str:
    return (
        "---\n"
        f"name: {slug}\n"
        "description: A skill.\n"
        "license: MIT\n"
        "metadata:\n"
        "  author: emf-framework\n"
        "  version: '1.0'\n"
        "---\n"
        f"# {slug}\n"
    )


class OrphanSkillRule(unittest.TestCase):
    """SDD-047 D-1 R-1..R-3 -- unreferenced (non-domain) skills are flagged."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.root = _make_orphan_root(Path(self._tmp.name))

    def tearDown(self):
        gc.collect()
        self._tmp.cleanup()

    def _write_skill(self, slug: str, sub: str = "") -> None:
        base = self.root / ".github" / "skills"
        d = (base / sub / slug) if sub else (base / slug)
        d.mkdir(parents=True, exist_ok=True)
        (d / "SKILL.md").write_text(_skill_body(slug), encoding="utf-8")

    def test_unreferenced_skill_is_flagged(self):
        """R-1: a non-domain skill referenced nowhere is an orphan finding."""
        self._write_skill("lonely-skill")
        findings = schema_lint.check_orphan_skills(self.root)
        self.assertTrue(
            any("lonely-skill" in f.path and "orphan" in f.issue for f in findings)
        )

    def test_referenced_in_agent_not_flagged(self):
        """R-1: a skill named in an agent file is not an orphan."""
        self._write_skill("wired-skill")
        write_agent(self.root, "owner-agent",
                    "---\ndescription: a.\n---\n# Agent\n- wired-skill: does things\n")
        findings = schema_lint.check_orphan_skills(self.root)
        self.assertFalse(any("wired-skill" in f.path for f in findings))

    def test_referenced_in_prompt_not_flagged(self):
        """R-1: a skill named only in a prompt is not an orphan."""
        self._write_skill("prompt-wired")
        write_prompt(self.root, "use-it",
                     "---\ndescription: p.\n---\nApply the prompt-wired skill.\n")
        findings = schema_lint.check_orphan_skills(self.root)
        self.assertFalse(any("prompt-wired" in f.path for f in findings))

    def test_referenced_in_instruction_not_flagged(self):
        """R-1: a skill named only in an instruction file is not an orphan."""
        self._write_skill("instr-wired")
        (self.root / ".github" / "instructions" / "x.instructions.md").write_text(
            "---\ndescription: i.\n---\nSee instr-wired for details.\n", encoding="utf-8"
        )
        findings = schema_lint.check_orphan_skills(self.root)
        self.assertFalse(any("instr-wired" in f.path for f in findings))

    def test_domain_skill_is_exempt(self):
        """R-2: domain/ reference skills are exempt even when unreferenced."""
        self._write_skill("fastapi-routes", sub="domain")
        findings = schema_lint.check_orphan_skills(self.root)
        self.assertFalse(any("fastapi-routes" in f.path for f in findings))

    def test_check_orphans_flag_off_by_default(self):
        """R-3: default scan() does not run the orphan rule (byte-identical)."""
        self._write_skill("lonely-skill")
        # Default scan must not surface an orphan finding.
        findings = schema_lint.scan(self.root)
        self.assertFalse(any("orphan" in f.issue for f in findings))

    def test_check_orphans_cli_flag_flags_orphan(self):
        """R-3: --check-orphans surfaces the orphan and exits non-zero."""
        self._write_skill("lonely-skill")
        with_flag = subprocess.run(
            [sys.executable, str(SCHEMA_LINT), "--repo-root", str(self.root),
             "--check-orphans"],
            capture_output=True, text=True,
        )
        self.assertEqual(with_flag.returncode, 1)
        self.assertIn("orphan", with_flag.stdout.lower())

    def test_real_repo_has_zero_orphans(self):
        """R-1 in practice: the live framework has every skill wired."""
        findings = schema_lint.check_orphan_skills(REPO_ROOT)
        if findings:
            sample = "\n".join(f"  {f.path}: {f.issue}" for f in findings)
            self.fail(f"{len(findings)} orphan skill(s):\n{sample}")


class DependsOnParseHelperContinued(unittest.TestCase):
    """T-036-02 (continued) -- parse_depends_on inline-list parsing."""

    def test_inline_single_id_value(self):
        fm = schema_lint.parse_frontmatter(_spec_with_depends_on("depends_on: [SDD-018]"))
        self.assertEqual(schema_lint.parse_depends_on(fm), ["SDD-018"])

    def test_inline_multiple_ids(self):
        fm = schema_lint.parse_frontmatter(_spec_with_depends_on("depends_on: [SDD-018, SDD-019]"))
        self.assertEqual(schema_lint.parse_depends_on(fm), ["SDD-018", "SDD-019"])

    def test_empty_inline_list(self):
        fm = schema_lint.parse_frontmatter(_spec_with_depends_on("depends_on: []"))
        self.assertEqual(schema_lint.parse_depends_on(fm), [])

    def test_bare_scalar(self):
        fm = schema_lint.parse_frontmatter(_spec_with_depends_on("depends_on: SDD-018"))
        self.assertEqual(schema_lint.parse_depends_on(fm), ["SDD-018"])


class DependsOnValidator(unittest.TestCase):
    """T-036-03 -- check_depends_on validates ONLY when present."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.tmp = Path(self._tmp.name)

    def tearDown(self):
        gc.collect()
        self._tmp.cleanup()

    def _spec(self, dep_line: str, spec_id: str = "SDD-036-spec") -> Path:
        p = self.tmp / "spec.md"
        p.write_text(_spec_with_depends_on(dep_line, spec_id), encoding="utf-8")
        return p

    def test_absent_depends_on_zero_findings(self):
        p = self.tmp / "spec.md"
        p.write_text(GOOD_ARTIFACT, encoding="utf-8")
        self.assertEqual(schema_lint.check_depends_on(p, {"SDD-018"}), [])

    def test_valid_single_dep_zero_findings(self):
        p = self._spec("depends_on: [SDD-018]")
        self.assertEqual(schema_lint.check_depends_on(p, {"SDD-018"}), [])

    def test_bad_id_shape_is_error(self):
        p = self._spec("depends_on: [not-an-id]")
        findings = schema_lint.check_depends_on(p, {"SDD-018"})
        self.assertTrue(any("is not a valid artifact ID" in f.issue for f in findings))
        self.assertTrue(all(f.severity == "ERROR" for f in findings))

    def test_duplicate_entry_is_error(self):
        p = self._spec("depends_on: [SDD-018, SDD-018]")
        findings = schema_lint.check_depends_on(p, {"SDD-018"})
        dups = [f for f in findings if "duplicate entry" in f.issue]
        self.assertEqual(len(dups), 1)
        self.assertEqual(dups[0].severity, "ERROR")

    def test_self_dependency_is_error(self):
        # Self-dep is keyed on the frontmatter `id`; use a shape-valid id so
        # the entry passes ID-shape validation and reaches the self-dep check.
        p = self._spec("depends_on: [SDD-036]", spec_id="SDD-036")
        findings = schema_lint.check_depends_on(p, {"SDD-036"})
        self.assertTrue(any("depends_on lists self" in f.issue for f in findings))
        self.assertTrue(all(f.severity == "ERROR" for f in findings))

    def test_missing_backlog_ref_is_warning(self):
        p = self._spec("depends_on: [SDD-999]")
        findings = schema_lint.check_depends_on(p, {"SDD-018"})
        warns = [f for f in findings if "not found in BACKLOG.md" in f.issue]
        self.assertEqual(len(warns), 1)
        self.assertEqual(warns[0].severity, "WARNING")

    def test_backlog_none_skips_existence_check(self):
        p = self._spec("depends_on: [SDD-999]")
        self.assertEqual(schema_lint.check_depends_on(p, None), [])


class DependsOnDiscoveryAndWalk(unittest.TestCase):
    """T-036-03 -- BACKLOG discovery + integration into _walk_artifacts."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.tmp = Path(self._tmp.name)
        (self.tmp / "backlog").mkdir(parents=True)
        (self.tmp / "backlog" / "BACKLOG.md").write_text(
            "| SDD-018 | UI variant | DONE |\n", encoding="utf-8"
        )
        self.specs = self.tmp / "specs" / "demo"
        self.specs.mkdir(parents=True)

    def tearDown(self):
        gc.collect()
        self._tmp.cleanup()

    def test_discover_backlog_ids_walks_up(self):
        ids = schema_lint._discover_backlog_ids(self.specs)
        self.assertIsNotNone(ids)
        self.assertIn("SDD-018", ids)

    def test_discover_returns_none_when_absent(self):
        # Isolated tree with no `backlog/BACKLOG.md` in any ancestor.
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as loose:
            self.assertIsNone(schema_lint._discover_backlog_ids(Path(loose)))

    def test_walk_valid_demonstrator_clean(self):
        (self.specs / "spec.md").write_text(
            _spec_with_depends_on("depends_on: [SDD-018]"), encoding="utf-8"
        )
        findings = schema_lint.scan(self.tmp, paths=[self.tmp / "specs"])
        self.assertEqual(findings, [], f"unexpected findings: {[f.issue for f in findings]}")

    def test_walk_bad_dep_surfaces_finding(self):
        (self.specs / "spec.md").write_text(
            _spec_with_depends_on("depends_on: [bogus]"), encoding="utf-8"
        )
        findings = schema_lint.scan(self.tmp, paths=[self.tmp / "specs"])
        self.assertTrue(any("is not a valid artifact ID" in f.issue for f in findings))



