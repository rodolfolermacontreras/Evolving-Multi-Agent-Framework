"""RED-3A immutable bundle, clean seed, and preview contract for SDD-058.

The expected membership below is a direct, deliberately explicit expansion of
accepted ADR-026 Appendix A. It is not discovered from the framework tree.
"""

from __future__ import annotations

import dataclasses
import hashlib
import importlib
import json
import sqlite3
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

CLI_DIR = Path(__file__).resolve().parent
FRAMEWORK_ROOT = CLI_DIR.parents[1]
SCHEMA_PATH = FRAMEWORK_ROOT / "spec-driven-development" / "ledger" / "schema.sql"
if str(CLI_DIR) not in sys.path:
    sys.path.insert(0, str(CLI_DIR))

BUNDLE_ID = "brownfield-core@1"
PREVIEW_CATEGORIES = (
    "create",
    "replace",
    "preserve",
    "conflict",
    "forbidden",
    "runtime-initialize",
)
FLEET_WORKER = ".github/instructions/fleet-workers.instructions.md"


def _paths(prefix: str, names: tuple[str, ...], suffix: str) -> set[str]:
    return {f"{prefix}/{name}{suffix}" for name in names}


RENDERED_IDENTITY = {
    ".github/copilot-instructions.md",
    "project.config.json",
    "spec-driven-development/README.md",
    "spec-driven-development/CONTEXT.md",
    *_paths(
        "spec-driven-development/constitution",
        (
            "mission",
            "tech-stack",
            "principles",
            "roadmap",
            "decision-policy",
            "quality-policy",
        ),
        ".md",
    ),
    *_paths(
        "spec-driven-development/roster",
        ("agents", "skills", "skill_packs"),
        ".json",
    ),
    *_paths(
        "spec-driven-development/.adoption",
        ("bundle-manifest", "host-identity", "receipt"),
        ".json",
    ),
}
AGENTS = _paths(
    ".github/agents",
    (
        "principal-executive-manager",
        "principal-product-manager",
        "principal-architect",
        "principal-software-developer",
        "sprint-executive-manager",
        "developer-general",
        "qa-engineer-general",
    ),
    ".agent.md",
)
PROMPTS = _paths(
    ".github/prompts",
    (
        "ask",
        "triage",
        "clarify",
        "grill",
        "spec",
        "plan",
        "tasks",
        "analyze",
        "fleet",
        "implement",
        "qa",
        "retro",
        "state",
        "replan",
        "evolve",
        "constitution",
    ),
    ".prompt.md",
)
SKILLS = {
    *_paths(
        ".github/skills/core",
        (
            "sdd-constitution",
            "project-context",
            "constitution-sync",
            "pre-work-check",
            "git-workflow",
            "testing-conventions",
        ),
        "/SKILL.md",
    ),
    *_paths(
        ".github/skills/workflow",
        ("grill-me", "grill-with-docs", "triage", "to-spec", "to-plan", "to-tasks", "implement"),
        "/SKILL.md",
    ),
    *_paths(
        ".github/skills/engineering",
        ("tdd", "tdd-gate", "diagnose", "code-review", "improve-architecture"),
        "/SKILL.md",
    ),
    *_paths(
        ".github/skills/operational",
        (
            "em-communication-discipline",
            "fleet-coordinator",
            "handoff",
            "lesson-capture",
            "pi-planning",
            "respect-existing",
            "session-self-review",
            "stakeholder-pressure-defense",
        ),
        "/SKILL.md",
    ),
}
INSTRUCTIONS = {
    ".github/instructions/sdd-workflow.instructions.md",
    FLEET_WORKER,
}
TEMPLATES_AND_DOCS = {
    *_paths(
        "spec-driven-development/templates",
        (
            "feature-spec",
            "lightweight-feature",
            "clarification-log",
            "validation",
            "plan",
            "task-list",
            "agent-brief",
            "review-report",
            "handoff",
            "level-2-decision",
            "stakeholder-pressure-response",
        ),
        ".md",
    ),
    "spec-driven-development/docs/ADR/TEMPLATE.md",
    "spec-driven-development/docs/CLI-PATTERN.md",
}
CLI_AND_LEDGER = {
    *_paths(
        "spec-driven-development/cli",
        (
            "__init__",
            "bootstrap",
            "dedup",
            "fleet",
            "qa",
            "retro",
            "schema_lint",
            "done_check",
            "tdd_gate_check",
        ),
        ".py",
    ),
    *_paths(
        "spec-driven-development/ledger",
        ("__init__", "init_ledger", "ledger_cli"),
        ".py",
    ),
    "spec-driven-development/ledger/schema.sql",
    *_paths(
        "spec-driven-development/cli",
        (
            "brownfield_inventory",
            "brownfield_proposal",
            "brownfield_manifest",
            "brownfield_identity",
            "brownfield_migration",
            "brownfield_transaction",
            "host_readiness",
            "brownfield_compat",
        ),
        ".py",
    ),
}
SEEDS = {
    "spec-driven-development/backlog/IDEAS.md",
    "spec-driven-development/backlog/BACKLOG.md",
    *_paths(
        "spec-driven-development",
        ("dispatches", "specs", "sprints", "sessions", "fleet", "exec"),
        "/.gitkeep",
    ),
    "spec-driven-development/ledger/fleet.db",
}
EXPECTED_MEMBERS = frozenset(
    RENDERED_IDENTITY | AGENTS | PROMPTS | SKILLS | INSTRUCTIONS | TEMPLATES_AND_DOCS | CLI_AND_LEDGER | SEEDS
)


def _manifest_module():
    """Import the intentionally absent production API inside RED test bodies."""

    return importlib.import_module("brownfield_manifest")


def _identity(worktree_profile: bool = False) -> SimpleNamespace:
    return SimpleNamespace(
        fields={"worktree_profile": SimpleNamespace(value=worktree_profile, confirmed_by="owner")}
    )


def _entries_by_destination(bundle) -> dict[str, object]:
    return {entry.destination: entry for entry in bundle.entries}


def _build(worktree_profile: bool = False):
    module = _manifest_module()
    return module, module.build_core_manifest(FRAMEWORK_ROOT, _identity(worktree_profile))


def _replace(entry, **changes):
    return dataclasses.replace(entry, **changes)


def _replace_manifest(manifest, entries):
    return dataclasses.replace(manifest, entries=tuple(entries))


def _renderer_registry(entries) -> dict[str, str]:
    return {
        entry.renderer_id: entry.renderer_version
        for entry in entries
        if entry.renderer_id is not None
    }


def test_build_core_manifest_has_exact_frozen_appendix_a_membership() -> None:
    _, bundle = _build(False)
    entries = _entries_by_destination(bundle)

    assert bundle.schema_version == "1"
    assert bundle.bundle_id == BUNDLE_ID
    assert set(entries) == EXPECTED_MEMBERS
    assert len(entries) == len(EXPECTED_MEMBERS) == 110
    assert tuple(entry.destination for entry in bundle.entries) == tuple(sorted(EXPECTED_MEMBERS))
    assert all("*" not in path and "{" not in path and "}" not in path for path in entries)


def test_build_core_manifest_keeps_conditional_fleet_worker_as_frozen_member() -> None:
    _, disabled = _build(False)
    _, enabled = _build(True)
    disabled_entries = _entries_by_destination(disabled)
    enabled_entries = _entries_by_destination(enabled)

    assert set(disabled_entries) == set(enabled_entries) == EXPECTED_MEMBERS
    assert disabled_entries[FLEET_WORKER].enabled_condition == "worktree_profile"
    assert enabled_entries[FLEET_WORKER].enabled_condition == "worktree_profile"
    assert not disabled_entries[FLEET_WORKER].enabled
    assert enabled_entries[FLEET_WORKER].enabled
    assert disabled_entries[FLEET_WORKER].destination == enabled_entries[FLEET_WORKER].destination


def test_build_core_manifest_declares_sources_renderers_hashes_and_clean_seeds() -> None:
    _, bundle = _build(False)
    entries = _entries_by_destination(bundle)

    assert {entry.operation for entry in bundle.entries} <= {"copy", "render", "seed", "preserve", "forbid"}
    assert all(entries[path].operation == "seed" for path in SEEDS)
    assert entries["spec-driven-development/ledger/fleet.db"].dependencies == (
        "spec-driven-development/ledger/schema.sql",
    )
    for entry in bundle.entries:
        assert entry.text_policy in {"binary", "preserve", "utf-8-lf"}
        assert entry.ownership in {"managed", "unmanaged"}
        if entry.operation == "copy":
            assert entry.source == entry.destination
            assert len(entry.source_sha256) == 64
            int(entry.source_sha256, 16)
            assert entry.renderer_id is None and entry.renderer_version is None
        if entry.operation == "render":
            assert entry.renderer_id and entry.renderer_version
            assert entry.source_sha256 is None


def test_validate_manifest_accepts_only_closed_stably_ordered_graph(tmp_path: Path) -> None:
    module, bundle = _build(False)
    validated = module.validate_manifest(
        bundle, FRAMEWORK_ROOT, tmp_path, _renderer_registry(bundle.entries)
    )

    destinations = tuple(entry.destination for entry in validated.entries)
    assert set(destinations) == EXPECTED_MEMBERS
    assert destinations == validated.topological_order
    assert destinations.index("spec-driven-development/ledger/schema.sql") < destinations.index(
        "spec-driven-development/ledger/fleet.db"
    )
    assert all(set(entry.dependencies) <= EXPECTED_MEMBERS for entry in validated.entries)


@pytest.mark.parametrize(
    ("mutation", "reason"),
    (
        ("missing", "membership"),
        ("extra", "membership"),
        ("missing-dependency", "dependency"),
        ("cycle", "cycle"),
        ("duplicate", "duplicate"),
        ("ancestor", "ancestor"),
        ("unknown-operation", "operation"),
        ("unknown-version", "version"),
        ("renderer-mismatch", "renderer"),
        ("hash-mismatch", "hash"),
        ("source-escape", "source"),
        ("target-escape", "destination"),
    ),
)
def test_validate_manifest_rejects_graph_membership_path_hash_and_renderer_bypasses(
    tmp_path: Path, mutation: str, reason: str
) -> None:
    module, bundle = _build(False)
    entries = list(bundle.entries)
    first_copy_index = next(i for i, entry in enumerate(entries) if entry.operation == "copy")
    first_render_index = next(i for i, entry in enumerate(entries) if entry.operation == "render")
    first_copy = entries[first_copy_index]
    first_render = entries[first_render_index]

    if mutation == "missing":
        entries.pop()
    elif mutation == "extra":
        entries.append(_replace(first_copy, destination="unlisted-canary.txt", source="unlisted-canary.txt"))
    elif mutation == "missing-dependency":
        entries[first_copy_index] = _replace(first_copy, dependencies=("missing/member.txt",))
    elif mutation == "cycle":
        second_index = next(i for i, entry in enumerate(entries) if i != first_copy_index)
        second = entries[second_index]
        entries[first_copy_index] = _replace(first_copy, dependencies=(second.destination,))
        entries[second_index] = _replace(second, dependencies=(first_copy.destination,))
    elif mutation == "duplicate":
        entries.append(first_copy)
    elif mutation == "ancestor":
        entries.append(_replace(first_copy, destination=first_copy.destination + "/child"))
    elif mutation == "unknown-operation":
        entries[first_copy_index] = _replace(first_copy, operation="copy-tree")
    elif mutation == "unknown-version":
        bundle = dataclasses.replace(bundle, schema_version="2")
    elif mutation == "renderer-mismatch":
        entries[first_render_index] = _replace(first_render, renderer_version="unregistered")
    elif mutation == "hash-mismatch":
        entries[first_copy_index] = _replace(first_copy, source_sha256="0" * 64)
    elif mutation == "source-escape":
        entries[first_copy_index] = _replace(first_copy, source="../outside")
    elif mutation == "target-escape":
        entries[first_copy_index] = _replace(first_copy, destination="../outside")

    mutated = _replace_manifest(bundle, entries)
    with pytest.raises(module.ManifestValidationError, match=reason):
        module.validate_manifest(
            mutated, FRAMEWORK_ROOT, tmp_path, _renderer_registry(bundle.entries)
        )


def test_build_core_manifest_reads_only_individually_allowlisted_sources(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = _manifest_module()
    canary = FRAMEWORK_ROOT / "spec-driven-development" / "unlisted-install-canary.txt"
    reads: list[str] = []
    original = module._read_source_bytes

    def recording_reader(root: Path, source: str) -> bytes:
        reads.append(source)
        assert source in EXPECTED_MEMBERS
        assert source not in {".github", "spec-driven-development"}
        return original(root, source)

    monkeypatch.setattr(module, "_read_source_bytes", recording_reader)
    bundle = module.build_core_manifest(FRAMEWORK_ROOT, _identity(False))

    assert canary.as_posix() not in reads
    assert set(reads) == {entry.source for entry in bundle.entries if entry.operation == "copy"}
    assert all("*" not in source and not source.endswith("/") for source in reads)


def test_materialize_candidate_never_reads_or_copies_unlisted_canary(tmp_path: Path) -> None:
    module, bundle = _build(False)
    framework = tmp_path / "framework"
    target = tmp_path / "candidate"
    framework.mkdir()
    canary = framework / "unlisted-canary.txt"
    canary.write_text("UNLISTED_SOURCE_CANARY\n", encoding="utf-8")
    reads: list[str] = []

    def source_reader(source: str) -> bytes:
        reads.append(source)
        if source == "unlisted-canary.txt":
            raise AssertionError("default-denied source was read")
        return b"approved fixture source\n"

    module.materialize_candidate(
        bundle,
        target,
        rendered_bytes={entry.destination: b"rendered\n" for entry in bundle.entries if entry.operation == "render"},
        seed_bytes=module.build_clean_seed_bytes(bundle),
        source_reader=source_reader,
    )

    assert "unlisted-canary.txt" not in reads
    assert not (target / "unlisted-canary.txt").exists()
    assert b"UNLISTED_SOURCE_CANARY" not in b"".join(
        path.read_bytes() for path in target.rglob("*") if path.is_file()
    )


def test_build_clean_seed_bytes_has_positive_empty_host_contract() -> None:
    module, bundle = _build(False)
    seeds = module.build_clean_seed_bytes(bundle)

    assert set(seeds) == SEEDS - {"spec-driven-development/ledger/fleet.db"}
    assert seeds["spec-driven-development/backlog/IDEAS.md"].startswith(b"# Ideas")
    assert seeds["spec-driven-development/backlog/BACKLOG.md"].startswith(b"# Backlog")
    for path, content in seeds.items():
        assert isinstance(content, bytes)
        assert b"\r\n" not in content
        if path.endswith("/.gitkeep"):
            assert content == b""
    joined = b"\n".join(seeds.values()).lower()
    assert b"sdd-" not in joined
    assert b"pi-" not in joined
    assert b"sprint" not in joined
    assert b"evolving-multi-agent-framework" not in joined


def test_initialize_clean_ledger_uses_exact_approved_schema_and_zero_rows(tmp_path: Path) -> None:
    module = _manifest_module()
    approved_schema = SCHEMA_PATH.read_bytes()
    database = tmp_path / "fleet.db"

    evidence = module.initialize_clean_ledger(database, approved_schema)

    assert evidence.schema_sha256 == hashlib.sha256(approved_schema).hexdigest()
    assert evidence.operational_rows == {"dispatches": 0, "decisions": 0}
    with sqlite3.connect(database) as connection:
        tables = {
            row[0] for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
            )
        }
        assert tables == {"dispatches", "decisions"}
        assert [row[1] for row in connection.execute("PRAGMA table_info(dispatches)")] == [
            "id", "dispatched_at", "pi", "sprint", "feature_dir", "task_id",
            "task_title", "agent_id", "agent_role", "outcome", "outcome_at", "notes",
        ]
        assert [row[1] for row in connection.execute("PRAGMA table_info(decisions)")] == [
            "id", "decided_at", "level", "decider", "artifact", "description",
        ]
        assert connection.execute("SELECT COUNT(*) FROM dispatches").fetchone()[0] == 0
        assert connection.execute("SELECT COUNT(*) FROM decisions").fetchone()[0] == 0


def test_forbidden_fingerprints_detect_injected_framework_history_only() -> None:
    module = _manifest_module()
    clean = {
        "backlog/IDEAS.md": b"# Ideas\n\nNo host ideas yet.\n",
        "exec/.gitkeep": b"",
    }
    assert module.find_forbidden_fingerprints(clean) == ()

    contaminated = dict(clean)
    contaminated["exec/state.md"] = (
        b"Evolving-Multi-Agent-Framework PI-9 Sprint 24 SDD-058 "
        b"Brownfield bootstrap preserves proposals and creates a clean host"
    )
    hits = module.find_forbidden_fingerprints(contaminated)
    assert module.FORBIDDEN_FINGERPRINT_VERSION == "1"
    assert {hit.fingerprint for hit in hits} >= {
        "framework-identity", "pi-history", "sprint-history", "sdd-history", "framework-backlog-title"
    }
    assert all(not Path(hit.path).is_absolute() and "\\" not in hit.path for hit in hits)


def _preview_item(module, category: str, path: str, before: str | None, after: str | None):
    return module.PreviewItem(
        category=category,
        destination=path,
        reason=f"fixture-{category}",
        ownership="managed",
        operation="seed" if category == "runtime-initialize" else "copy",
        before_sha256=before,
        after_sha256=after,
        dependencies=(),
    )


def test_canonical_preview_has_exact_six_ordered_categories_and_each_path_once(tmp_path: Path) -> None:
    module = _manifest_module()
    before = "1" * 64
    after = "2" * 64
    items = tuple(
        _preview_item(module, category, f"managed/{index}.txt", before, after)
        for index, category in enumerate(reversed(PREVIEW_CATEGORIES))
    )
    preview = module.Preview(schema_version="1", categories=PREVIEW_CATEGORIES, items=items)

    payload = json.loads(module.canonical_preview_bytes(preview))
    assert tuple(payload) == ("schema_version", *PREVIEW_CATEGORIES)
    assert tuple(payload)[1:] == PREVIEW_CATEGORIES
    flattened = [item for category in PREVIEW_CATEGORIES for item in payload[category]]
    assert len(flattened) == len({item["destination"] for item in flattened}) == 6
    assert all("\\" not in item["destination"] for item in flattened)
    assert str(tmp_path).replace("\\", "/") not in json.dumps(payload)


def test_canonical_preview_and_hash_are_deterministic_for_equivalent_orderings() -> None:
    module = _manifest_module()
    items = tuple(
        _preview_item(module, category, f"managed/{category}.txt", None, str(index) * 64)
        for index, category in enumerate(PREVIEW_CATEGORIES, start=1)
    )
    forward = module.Preview(schema_version="1", categories=PREVIEW_CATEGORIES, items=items)
    reverse = module.Preview(schema_version="1", categories=PREVIEW_CATEGORIES, items=tuple(reversed(items)))

    canonical = module.canonical_preview_bytes(forward)
    assert canonical == module.canonical_preview_bytes(reverse)
    assert canonical.endswith(b"\n") and b"\r\n" not in canonical
    assert module.preview_hash(forward) == module.preview_hash(reverse)
    assert module.preview_hash(forward) == hashlib.sha256(canonical).hexdigest()


def test_build_preview_rejects_unknown_duplicate_or_bypass_categories_before_output() -> None:
    module = _manifest_module()
    valid = _preview_item(module, "create", "managed/file.txt", None, "a" * 64)
    cases = (
        (valid, _replace(valid, category="warn")),
        (valid, _replace(valid, category="force")),
        (valid, _replace(valid, destination=valid.destination, category="preserve")),
    )

    for items in cases:
        with pytest.raises(module.PreviewValidationError):
            module.validate_preview(
                module.Preview(schema_version="1", categories=PREVIEW_CATEGORIES, items=items)
            )
