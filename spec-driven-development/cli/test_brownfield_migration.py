"""RED-4A migration classification, preservation, and idempotence contract.

These tests specify R-029 through R-033 and V-39 through V-44. They are
stdlib-only apart from pytest, write only below ``tmp_path``, and deliberately
exercise a read-only API: classification and planning must never mutate a host.
"""

from __future__ import annotations

import hashlib
import importlib
import sys
from dataclasses import fields as dataclass_fields
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

CLI_DIR = Path(__file__).resolve().parent
if str(CLI_DIR) not in sys.path:
    sys.path.insert(0, str(CLI_DIR))

from brownfield_inventory import InventorySnapshot, PathObservation, RepositoryEvidence  # noqa: E402
from brownfield_manifest import BundleEntry, BundleManifest, ValidatedBundle  # noqa: E402
from brownfield_test_fixtures import (  # noqa: E402
    build_node_express_fixture,
    create_disposable_root,
    make_link,
    snapshot_paths,
)

INSTALLATION_CLASSES = (
    "fresh",
    "proposal-only",
    "managed-current",
    "managed-drift",
    "legacy-broad-copy",
    "partial-or-interrupted",
    "foreign-collision",
    "mixed-contaminated",
)
PATH_CLASSES = (
    "absent",
    "managed-unchanged",
    "managed-modified",
    "generated-stale",
    "host-owned",
    "forbidden-contamination",
    "conflict",
)
PATH_REASONS = {
    "absent": "destination is absent",
    "managed-unchanged": "receipt and candidate hashes match observed bytes",
    "managed-modified": "receipt identifies managed bytes but the destination was modified",
    "generated-stale": "managed destination is unchanged but generated candidate bytes changed",
    "host-owned": "existing destination has no managed receipt evidence",
    "forbidden-contamination": "unmanaged destination matches a forbidden contamination rule",
    "conflict": "destination evidence is conflicting or unsafe",
}
INSTALLATION_REASONS = {
    "fresh": "no proposal or SDD installation state was found",
    "proposal-only": "a reviewed proposal exists without installed SDD state",
    "managed-current": "all receipt-managed destinations match current candidate bytes",
    "managed-drift": "at least one receipt-managed destination was modified",
    "legacy-broad-copy": "legacy SDD content exists without a managed adoption receipt",
    "partial-or-interrupted": "transaction or recovery evidence indicates an incomplete adoption",
    "foreign-collision": "an SDD destination is linked or contains an unsafe collision",
    "mixed-contaminated": "managed or legacy SDD state coexists with unmanaged contamination",
}


def _migration():
    """Import the intentionally absent implementation inside each test."""

    return importlib.import_module("brownfield_migration")


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _evidence() -> RepositoryEvidence:
    return RepositoryEvidence(
        schema_version="sdd-058-repository-evidence@1",
        target_head="a" * 40,
        project_name="fixture-host",
        remotes=("https://example.invalid/fixture-host.git",),
        default_branch="main",
        stack=("python",),
        quality_candidates=("python -m pytest",),
        conventions=("type: short description",),
        source_documents=("README.md",),
        evidence_digest="b" * 64,
    )


def _observation(
    path: str = ".github/copilot-instructions.md",
    *,
    content: bytes | None = b"host bytes\n",
    kind: str | None = None,
    ownership_hint: str = "unknown",
    link_kind: str | None = None,
    receipt_hash: str | None = None,
) -> PathObservation:
    actual_kind = kind or ("absent" if content is None else "file")
    return PathObservation(
        path=path,
        kind=actual_kind,
        ownership_hint=ownership_hint,
        sha256=None if content is None else _sha(content),
        byte_length=None if content is None else len(content),
        portable_mode=None if content is None else 0o644,
        link_kind=link_kind,
        receipt_hash=receipt_hash,
    )


def _entry(
    path: str = ".github/copilot-instructions.md",
    *,
    candidate: bytes = b"candidate bytes\n",
    operation: str = "copy",
    ownership: str = "managed",
) -> BundleEntry:
    return BundleEntry(
        destination=path,
        operation=operation,
        source=path if operation == "copy" else None,
        source_sha256=_sha(candidate) if operation == "copy" else None,
        renderer_id="fixture" if operation == "render" else None,
        renderer_version="1" if operation == "render" else None,
        ownership=ownership,
    )


def _receipt(**managed_hashes: str) -> SimpleNamespace:
    return SimpleNamespace(schema_version="1", managed_hashes=dict(managed_hashes))


def _proposal_state(
    *,
    exists: bool = False,
    baseline_exists: bool = False,
    legacy_intent: str | None = None,
) -> SimpleNamespace:
    return SimpleNamespace(
        exists=exists,
        baseline_exists=baseline_exists,
        legacy_intent=legacy_intent,
    )


def _inventory(
    observations: tuple[PathObservation, ...] = (),
    *,
    recovery_markers: tuple[str, ...] = (),
    fingerprint_hits: tuple[str, ...] = (),
) -> InventorySnapshot:
    return InventorySnapshot(
        schema_version="sdd-058-inventory@1",
        target_head="a" * 40,
        evidence=_evidence(),
        observations=observations,
        recovery_markers=recovery_markers,
        fingerprint_hits=fingerprint_hits,
    )


def _validated_bundle(*entries: BundleEntry) -> ValidatedBundle:
    ordered = tuple(entry.destination for entry in entries)
    return ValidatedBundle(
        schema_version="1",
        bundle_id="brownfield-core@1",
        framework_revision="c" * 40,
        entries=tuple(entries),
        forbidden_fingerprint_version="1",
        topological_order=ordered,
    )


def _path_case(path_class: str) -> tuple[PathObservation, BundleEntry, Any]:
    path = ".github/copilot-instructions.md"
    old = b"managed old\n"
    candidate = b"candidate bytes\n"
    if path_class == "absent":
        return _observation(path, content=None), _entry(path, candidate=candidate), None
    if path_class == "managed-unchanged":
        digest = _sha(candidate)
        return (
            _observation(path, content=candidate, ownership_hint="managed", receipt_hash=digest),
            _entry(path, candidate=candidate),
            _receipt(**{path: digest}),
        )
    if path_class == "managed-modified":
        digest = _sha(old)
        return (
            _observation(path, content=b"human modification\n", ownership_hint="managed", receipt_hash=digest),
            _entry(path, candidate=old),
            _receipt(**{path: digest}),
        )
    if path_class == "generated-stale":
        digest = _sha(old)
        return (
            _observation(path, content=old, ownership_hint="managed", receipt_hash=digest),
            _entry(path, candidate=candidate),
            _receipt(**{path: digest}),
        )
    if path_class == "host-owned":
        return _observation(path, ownership_hint="host-owned"), _entry(path), None
    if path_class == "forbidden-contamination":
        return (
            _observation(path, ownership_hint="forbidden-contamination"),
            _entry(path, operation="forbid", ownership="unmanaged"),
            None,
        )
    if path_class == "conflict":
        return (
            _observation(path, kind="link", link_kind="symlink"),
            _entry(path),
            None,
        )
    raise AssertionError(path_class)


def _classes(*values: str):
    migration = _migration()
    results = []
    for index, value in enumerate(values):
        observation, entry, receipt = _path_case(value)
        if index:
            path = f"spec-driven-development/case-{index}.md"
            observation = PathObservation(
                path=path,
                kind=observation.kind,
                ownership_hint=observation.ownership_hint,
                sha256=observation.sha256,
                byte_length=observation.byte_length,
                portable_mode=observation.portable_mode,
                link_kind=observation.link_kind,
                receipt_hash=observation.receipt_hash,
            )
            entry = BundleEntry(
                destination=path,
                operation=entry.operation,
                source=path if entry.operation == "copy" else entry.source,
                source_sha256=entry.source_sha256,
                renderer_id=entry.renderer_id,
                renderer_version=entry.renderer_version,
                dependencies=entry.dependencies,
                text_policy=entry.text_policy,
                ownership=entry.ownership,
                enabled_condition=entry.enabled_condition,
                enabled=entry.enabled,
            )
            if receipt is not None:
                receipt = _receipt(**{path: next(iter(receipt.managed_hashes.values()))})
        results.append(migration.classify_path(observation, entry, receipt))
    return tuple(results)


def _install_case(installation_class: str):
    migration = _migration()
    proposal = _proposal_state()
    inventory = _inventory()
    path_classes = ()
    if installation_class == "proposal-only":
        proposal = _proposal_state(exists=True, baseline_exists=True)
    elif installation_class == "managed-current":
        path_classes = _classes("managed-unchanged")
    elif installation_class == "managed-drift":
        path_classes = _classes("managed-modified")
    elif installation_class == "legacy-broad-copy":
        path_classes = _classes("host-owned")
        inventory = _inventory(fingerprint_hits=("legacy-framework-tree",))
    elif installation_class == "partial-or-interrupted":
        inventory = _inventory(recovery_markers=(".sdd-transaction/active.json",))
    elif installation_class == "foreign-collision":
        path_classes = _classes("conflict")
    elif installation_class == "mixed-contaminated":
        path_classes = _classes("managed-unchanged", "forbidden-contamination")
        inventory = _inventory(fingerprint_hits=("framework-status-history",))
    return migration.classify_installation(inventory, path_classes, proposal)


@pytest.mark.parametrize("expected", INSTALLATION_CLASSES)
def test_classify_installation_returns_each_exact_class_with_stable_reason(expected: str) -> None:
    migration = _migration()

    first = _install_case(expected)
    second = _install_case(expected)

    assert tuple(item.value for item in migration.InstallationClass) == INSTALLATION_CLASSES
    assert first.installation_class.value == expected
    assert first.reasons == (INSTALLATION_REASONS[expected],)
    assert second == first
    assert tuple(item.name for item in dataclass_fields(first)) == (
        "installation_class",
        "reasons",
        "path_classifications",
        "requires_explicit_migration",
        "guidance",
    )
    assert first.requires_explicit_migration is (expected not in {"fresh", "proposal-only"})


@pytest.mark.parametrize("expected", PATH_CLASSES)
def test_classify_path_returns_each_exact_class_with_stable_reason(expected: str) -> None:
    migration = _migration()
    observation, entry, receipt = _path_case(expected)

    first = migration.classify_path(observation, entry, receipt)
    second = migration.classify_path(observation, entry, receipt)

    assert tuple(item.value for item in migration.PathClass) == PATH_CLASSES
    assert first.path == observation.path
    assert first.path_class.value == expected
    assert first.reason == PATH_REASONS[expected]
    assert second == first
    assert tuple(item.name for item in dataclass_fields(first)) == (
        "path",
        "path_class",
        "reason",
        "before_sha256",
        "receipt_sha256",
        "candidate_sha256",
        "managed_destination",
    )


def test_classify_path_uses_receipt_hash_before_appearance_and_contamination_hints() -> None:
    migration = _migration()
    old = b"receipt managed\n"
    receipt_hash = _sha(old)
    observation = _observation(
        content=b"human changed bytes\n",
        ownership_hint="forbidden-contamination",
        receipt_hash=receipt_hash,
    )
    entry = _entry(candidate=old, operation="copy")

    result = migration.classify_path(
        observation,
        entry,
        _receipt(**{observation.path: receipt_hash}),
    )

    assert result.path_class.value == "managed-modified"
    assert result.reason == PATH_REASONS["managed-modified"]


def test_classify_path_precedence_is_conflict_then_receipt_then_forbidden_then_host_owned() -> None:
    migration = _migration()
    path = ".github/copilot-instructions.md"
    old = b"managed\n"
    digest = _sha(old)

    linked = _observation(
        path,
        content=b"changed\n",
        kind="link",
        ownership_hint="forbidden-contamination",
        link_kind="junction",
        receipt_hash=digest,
    )
    linked_result = migration.classify_path(linked, _entry(path, candidate=old), _receipt(**{path: digest}))
    managed_result = migration.classify_path(
        _observation(path, content=b"changed\n", ownership_hint="forbidden-contamination", receipt_hash=digest),
        _entry(path, candidate=old),
        _receipt(**{path: digest}),
    )
    forbidden_result = migration.classify_path(
        _observation(path, ownership_hint="forbidden-contamination"),
        _entry(path, operation="forbid", ownership="unmanaged"),
        None,
    )

    assert linked_result.path_class.value == "conflict"
    assert managed_result.path_class.value == "managed-modified"
    assert forbidden_result.path_class.value == "forbidden-contamination"


def test_classify_installation_precedence_is_recovery_link_mixed_drift_legacy_current_proposal_fresh() -> None:
    migration = _migration()
    proposal = _proposal_state(exists=True, baseline_exists=True)
    mixed_classes = _classes("conflict", "managed-modified", "forbidden-contamination")

    interrupted = migration.classify_installation(
        _inventory(recovery_markers=("active-journal",), fingerprint_hits=("legacy-tree",)),
        mixed_classes,
        proposal,
    )
    linked = migration.classify_installation(
        _inventory(fingerprint_hits=("legacy-tree",)), mixed_classes, proposal
    )
    mixed = migration.classify_installation(
        _inventory(fingerprint_hits=("legacy-tree",)),
        _classes("managed-modified", "forbidden-contamination"),
        proposal,
    )
    drift = migration.classify_installation(
        _inventory(), _classes("managed-modified"), proposal
    )

    assert interrupted.installation_class.value == "partial-or-interrupted"
    assert linked.installation_class.value == "foreign-collision"
    assert mixed.installation_class.value == "mixed-contaminated"
    assert drift.installation_class.value == "managed-drift"


def test_existing_installations_require_explicit_migration_and_legacy_inputs_map_safely() -> None:
    migration = _migration()

    bare = migration.classify_legacy_input("bare", installation_exists=False)
    draft = migration.classify_legacy_input("draft-only", installation_exists=False)
    apply = migration.classify_legacy_input("apply", installation_exists=False)
    adopted = migration.classify_legacy_input("apply", installation_exists=True)

    assert (bare.action, bare.overwrite_reviewed_proposal, bare.refresh) == ("draft", False, False)
    assert (draft.action, draft.overwrite_reviewed_proposal, draft.refresh) == ("draft", False, False)
    assert (apply.action, apply.preview_first, apply.consume_existing_proposal, apply.refresh) == (
        "preview",
        True,
        True,
        False,
    )
    assert adopted.action == "migrate"
    assert adopted.requires_explicit_migration is True
    assert "explicit migration" in adopted.guidance.lower()


@pytest.mark.parametrize("legacy_input", ("force", "skip-conflicts", "broad-copy", "regenerate"))
def test_unsafe_legacy_inputs_fail_with_migration_guidance(legacy_input: str) -> None:
    migration = _migration()

    with pytest.raises(migration.UnsafeLegacyBehaviorError, match="explicit migration"):
        migration.classify_legacy_input(legacy_input, installation_exists=True)


def test_plan_migration_preserves_unknown_modified_and_history_bytes_without_delete(tmp_path: Path) -> None:
    migration = _migration()
    disposable = create_disposable_root(tmp_path)
    host = build_node_express_fixture(disposable)
    managed_path = host.root / ".github" / "copilot-instructions.md"
    unknown_path = host.root / "spec-driven-development" / "unknown-notes.md"
    history_path = host.root / "spec-driven-development" / "ledger" / "fleet.db"
    managed_path.parent.mkdir(parents=True, exist_ok=True)
    unknown_path.parent.mkdir(parents=True, exist_ok=True)
    history_path.parent.mkdir(parents=True, exist_ok=True)
    managed_path.write_bytes(b"human modified managed bytes\r\n")
    unknown_path.write_bytes(b"unknown host work\n")
    history_path.write_bytes(b"SQLite history bytes\x00\r\n")
    watched = (managed_path, unknown_path, history_path, host.root)
    before = snapshot_paths(watched)

    managed_entry = _entry(managed_path.relative_to(host.root).as_posix(), candidate=b"old managed\n")
    contamination_entry = _entry(
        "spec-driven-development/unknown-notes.md",
        operation="forbid",
        ownership="unmanaged",
    )
    managed_class = migration.classify_path(
        _observation(
            managed_entry.destination,
            content=managed_path.read_bytes(),
            ownership_hint="managed",
            receipt_hash=_sha(b"old managed\n"),
        ),
        managed_entry,
        _receipt(**{managed_entry.destination: _sha(b"old managed\n")}),
    )
    contamination_class = migration.classify_path(
        _observation(
            contamination_entry.destination,
            content=unknown_path.read_bytes(),
            ownership_hint="forbidden-contamination",
        ),
        contamination_entry,
        None,
    )
    classification = migration.classify_installation(
        _inventory(fingerprint_hits=("legacy-history",)),
        (managed_class, contamination_class),
        _proposal_state(exists=True, baseline_exists=True),
    )

    plan = migration.plan_migration(
        classification,
        _validated_bundle(managed_entry, contamination_entry),
        SimpleNamespace(project_name="fixture-host"),
        _receipt(**{managed_entry.destination: _sha(b"old managed\n")}),
    )

    assert snapshot_paths(watched) == before
    assert plan.mode == "migration"
    assert plan.requires_approval is True
    assert set(plan.preserved_paths) >= {
        managed_entry.destination,
        contamination_entry.destination,
        "spec-driven-development/ledger/fleet.db",
    }
    assert all(operation.action != "delete" for operation in plan.operations)
    assert all(operation.destination != contamination_entry.destination for operation in plan.operations)
    assert all(operation.destination in {entry.destination for entry in (managed_entry, contamination_entry)} for operation in plan.operations)


def test_managed_current_rerun_is_semantic_noop_without_side_effect_requests() -> None:
    migration = _migration()
    content = b"managed current\n"
    path = ".github/copilot-instructions.md"
    entry = _entry(path, candidate=content)
    receipt = _receipt(**{path: _sha(content)})
    path_class = migration.classify_path(
        _observation(path, content=content, ownership_hint="managed", receipt_hash=_sha(content)),
        entry,
        receipt,
    )
    classification = migration.classify_installation(
        _inventory(), (path_class,), _proposal_state(exists=True, baseline_exists=True)
    )

    first = migration.plan_migration(
        classification, _validated_bundle(entry), SimpleNamespace(), receipt
    )
    second = migration.plan_migration(
        classification, _validated_bundle(entry), SimpleNamespace(), receipt
    )

    assert first == second
    assert first.status == "no-op"
    assert first.reason == "managed installation already matches approved inputs"
    assert first.operations == ()
    assert first.side_effects == ()
    assert first.requires_backup is False
    assert first.requires_journal is False
    assert first.write_receipt is False
    assert first.write_operational_ledger is False


def test_managed_drift_is_reported_and_preserved_not_silently_replaced() -> None:
    migration = _migration()
    path = "spec-driven-development/CONTEXT.md"
    old = b"managed old\n"
    changed = b"host edit must survive\n"
    entry = _entry(path, candidate=old)
    receipt = _receipt(**{path: _sha(old)})
    path_class = migration.classify_path(
        _observation(path, content=changed, ownership_hint="managed", receipt_hash=_sha(old)),
        entry,
        receipt,
    )
    classification = migration.classify_installation(
        _inventory(), (path_class,), _proposal_state(exists=True, baseline_exists=True)
    )

    plan = migration.plan_migration(
        classification, _validated_bundle(entry), SimpleNamespace(), receipt
    )

    assert classification.installation_class.value == "managed-drift"
    assert plan.status == "blocked"
    assert path in plan.preserved_paths
    assert plan.operations == ()
    assert "modified" in plan.guidance.lower()
    assert "approve" in plan.guidance.lower()


def test_legacy_broad_copy_is_preserved_and_requires_explicit_inventory_migration() -> None:
    migration = _migration()
    path_class = _classes("host-owned")[0]
    classification = migration.classify_installation(
        _inventory(fingerprint_hits=("framework-history",)),
        (path_class,),
        _proposal_state(exists=True, baseline_exists=False, legacy_intent="apply"),
    )

    plan = migration.plan_migration(
        classification,
        _validated_bundle(_entry()),
        SimpleNamespace(),
        None,
    )

    assert classification.installation_class.value == "legacy-broad-copy"
    assert classification.requires_explicit_migration is True
    assert plan.requires_approval is True
    assert plan.operations == ()
    assert path_class.path in plan.preserved_paths
    assert "inventory" in plan.guidance.lower()
    assert "migration" in plan.guidance.lower()


def test_host_link_is_detected_without_traversal_and_returns_detach_inventory_guidance(tmp_path: Path) -> None:
    migration = _migration()
    disposable = create_disposable_root(tmp_path)
    target = disposable.root / "linked-framework-target"
    target.mkdir()
    canary = target / "must-not-change.txt"
    canary.write_bytes(b"linked tree canary\n")
    link = disposable.root / "host" / "spec-driven-development"
    link.parent.mkdir()
    linked = make_link(link, target)
    before = snapshot_paths((target, canary, link))
    link_kind = "symlink" if linked else "junction"
    observation = _observation(
        "spec-driven-development",
        content=b"link marker",
        kind="link",
        ownership_hint="unknown",
        link_kind=link_kind,
    )

    path_class = migration.classify_path(
        observation,
        _entry("spec-driven-development", candidate=b"candidate"),
        None,
    )
    classification = migration.classify_installation(
        _inventory(observations=(observation,)),
        (path_class,),
        _proposal_state(),
    )
    plan = migration.plan_migration(
        classification,
        _validated_bundle(_entry("spec-driven-development", candidate=b"candidate")),
        SimpleNamespace(),
        None,
    )

    assert snapshot_paths((target, canary, link)) == before
    assert path_class.path_class.value == "conflict"
    assert classification.installation_class.value == "foreign-collision"
    assert plan.operations == ()
    assert "detach" in plan.guidance.lower()
    assert "inventory" in plan.guidance.lower()
    assert "link" in plan.guidance.lower() or "junction" in plan.guidance.lower()


def test_every_migration_plan_operation_vocabulary_excludes_delete() -> None:
    migration = _migration()

    assert "delete" not in migration.MIGRATION_ACTIONS
    assert set(migration.MIGRATION_ACTIONS) <= {"create", "replace", "preserve", "report"}
