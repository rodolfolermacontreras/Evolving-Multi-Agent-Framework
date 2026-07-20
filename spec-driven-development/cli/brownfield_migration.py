"""Read-only brownfield installation classification and migration planning.

The module converts inventory, manifest, receipt, and proposal evidence into
immutable descriptions.  It performs no filesystem access or mutation: execution,
backup, journaling, and receipt persistence belong to the transaction layer.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Iterable

MIGRATION_ACTIONS = ("create", "replace", "preserve", "report")


class InstallationClass(str, Enum):
    FRESH = "fresh"
    PROPOSAL_ONLY = "proposal-only"
    MANAGED_CURRENT = "managed-current"
    MANAGED_DRIFT = "managed-drift"
    LEGACY_BROAD_COPY = "legacy-broad-copy"
    PARTIAL_OR_INTERRUPTED = "partial-or-interrupted"
    FOREIGN_COLLISION = "foreign-collision"
    MIXED_CONTAMINATED = "mixed-contaminated"


class PathClass(str, Enum):
    ABSENT = "absent"
    MANAGED_UNCHANGED = "managed-unchanged"
    MANAGED_MODIFIED = "managed-modified"
    GENERATED_STALE = "generated-stale"
    HOST_OWNED = "host-owned"
    FORBIDDEN_CONTAMINATION = "forbidden-contamination"
    CONFLICT = "conflict"


_PATH_REASONS = {
    PathClass.ABSENT: "destination is absent",
    PathClass.MANAGED_UNCHANGED: "receipt and candidate hashes match observed bytes",
    PathClass.MANAGED_MODIFIED: "receipt identifies managed bytes but the destination was modified",
    PathClass.GENERATED_STALE: "managed destination is unchanged but generated candidate bytes changed",
    PathClass.HOST_OWNED: "existing destination has no managed receipt evidence",
    PathClass.FORBIDDEN_CONTAMINATION: "unmanaged destination matches a forbidden contamination rule",
    PathClass.CONFLICT: "destination evidence is conflicting or unsafe",
}
_INSTALLATION_REASONS = {
    InstallationClass.FRESH: "no proposal or SDD installation state was found",
    InstallationClass.PROPOSAL_ONLY: "a reviewed proposal exists without installed SDD state",
    InstallationClass.MANAGED_CURRENT: "all receipt-managed destinations match current candidate bytes",
    InstallationClass.MANAGED_DRIFT: "at least one receipt-managed destination was modified",
    InstallationClass.LEGACY_BROAD_COPY: "legacy SDD content exists without a managed adoption receipt",
    InstallationClass.PARTIAL_OR_INTERRUPTED: "transaction or recovery evidence indicates an incomplete adoption",
    InstallationClass.FOREIGN_COLLISION: "an SDD destination is linked or contains an unsafe collision",
    InstallationClass.MIXED_CONTAMINATED: "managed or legacy SDD state coexists with unmanaged contamination",
}


@dataclass(frozen=True, slots=True)
class PathClassification:
    path: str
    path_class: PathClass
    reason: str
    before_sha256: str | None
    receipt_sha256: str | None
    candidate_sha256: str | None
    managed_destination: bool


@dataclass(frozen=True, slots=True)
class InstallationClassification:
    installation_class: InstallationClass
    reasons: tuple[str, ...]
    path_classifications: tuple[PathClassification, ...]
    requires_explicit_migration: bool
    guidance: str


@dataclass(frozen=True, slots=True)
class LegacyBehavior:
    action: str
    overwrite_reviewed_proposal: bool = False
    refresh: bool = False
    preview_first: bool = False
    consume_existing_proposal: bool = False
    requires_explicit_migration: bool = False
    guidance: str = ""


@dataclass(frozen=True, slots=True)
class MigrationOperation:
    action: str
    destination: str
    reason: str
    before_sha256: str | None = None
    after_sha256: str | None = None


@dataclass(frozen=True, slots=True)
class MigrationPlan:
    mode: str
    status: str
    reason: str
    operations: tuple[MigrationOperation, ...]
    preserved_paths: tuple[str, ...]
    side_effects: tuple[str, ...]
    requires_approval: bool
    requires_backup: bool
    requires_journal: bool
    write_receipt: bool
    write_operational_ledger: bool
    guidance: str


class UnsafeLegacyBehaviorError(ValueError):
    """A legacy option cannot be mapped without reviving unsafe behavior."""


def _receipt_hash(prior_receipt: object | None, path: str) -> str | None:
    hashes = getattr(prior_receipt, "managed_hashes", None)
    if not isinstance(hashes, dict):
        return None
    value = hashes.get(path)
    return value if isinstance(value, str) and value else None


def _candidate_hash(bundle_entry: object) -> str | None:
    value = getattr(bundle_entry, "source_sha256", None)
    return value if isinstance(value, str) and value else None


def classify_path(
    observation: object,
    bundle_entry: object,
    prior_receipt: object | None,
) -> PathClassification:
    """Classify one destination using deterministic safety-first precedence.

    Precedence is unsafe-kind conflict, receipt/hash evidence, absence, forbidden
    contamination, then host ownership.  Consequently appearance hints cannot
    relabel receipt-managed content, and links are never treated as files.
    """

    path = str(getattr(observation, "path"))
    kind = getattr(observation, "kind", None)
    before = getattr(observation, "sha256", None)
    receipt = _receipt_hash(prior_receipt, path)
    candidate = _candidate_hash(bundle_entry)

    if kind not in {"absent", "file"}:
        path_class = PathClass.CONFLICT
    elif receipt is not None:
        if before != receipt:
            path_class = PathClass.MANAGED_MODIFIED
        elif candidate is not None and candidate != receipt:
            path_class = PathClass.GENERATED_STALE
        else:
            path_class = PathClass.MANAGED_UNCHANGED
    elif kind == "absent":
        path_class = PathClass.ABSENT
    elif (
        getattr(observation, "ownership_hint", None) == "forbidden-contamination"
        or getattr(bundle_entry, "operation", None) == "forbid"
    ):
        path_class = PathClass.FORBIDDEN_CONTAMINATION
    else:
        path_class = PathClass.HOST_OWNED

    return PathClassification(
        path=path,
        path_class=path_class,
        reason=_PATH_REASONS[path_class],
        before_sha256=before,
        receipt_sha256=receipt,
        candidate_sha256=candidate,
        managed_destination=receipt is not None,
    )


def classify_installation(
    inventory: object,
    path_classes: Iterable[PathClassification],
    proposal_state: object,
) -> InstallationClassification:
    """Return one installation class using the frozen precedence contract."""

    paths = tuple(path_classes)
    classes = {item.path_class for item in paths}
    recovery = bool(tuple(getattr(inventory, "recovery_markers", ()) or ()))
    fingerprints = bool(tuple(getattr(inventory, "fingerprint_hits", ()) or ()))
    has_conflict = PathClass.CONFLICT in classes
    has_forbidden = PathClass.FORBIDDEN_CONTAMINATION in classes
    has_managed = bool(classes & {
        PathClass.MANAGED_UNCHANGED,
        PathClass.MANAGED_MODIFIED,
        PathClass.GENERATED_STALE,
    })

    if recovery:
        selected = InstallationClass.PARTIAL_OR_INTERRUPTED
    elif has_conflict:
        selected = InstallationClass.FOREIGN_COLLISION
    elif has_forbidden and (has_managed or fingerprints):
        selected = InstallationClass.MIXED_CONTAMINATED
    elif classes & {PathClass.MANAGED_MODIFIED, PathClass.GENERATED_STALE}:
        selected = InstallationClass.MANAGED_DRIFT
    elif fingerprints:
        selected = InstallationClass.LEGACY_BROAD_COPY
    elif has_managed:
        selected = InstallationClass.MANAGED_CURRENT
    elif bool(getattr(proposal_state, "exists", False)):
        selected = InstallationClass.PROPOSAL_ONLY
    else:
        selected = InstallationClass.FRESH

    guidance = {
        InstallationClass.FRESH: "Create or review a proposal before applying the curated bundle.",
        InstallationClass.PROPOSAL_ONLY: "Preview the reviewed proposal before any apply.",
        InstallationClass.MANAGED_CURRENT: "No migration is needed while approved inputs remain unchanged.",
        InstallationClass.MANAGED_DRIFT: "Preserve modified managed files and approve an explicit migration before replacement.",
        InstallationClass.LEGACY_BROAD_COPY: "Inventory the legacy installation before approving an explicit migration.",
        InstallationClass.PARTIAL_OR_INTERRUPTED: "Recover or inventory the interrupted transaction before migration.",
        InstallationClass.FOREIGN_COLLISION: "Detach the link or junction, then inventory the destination before migration.",
        InstallationClass.MIXED_CONTAMINATED: "Preserve contamination and modified work; approve an explicit inventory-based migration.",
    }[selected]
    return InstallationClassification(
        installation_class=selected,
        reasons=(_INSTALLATION_REASONS[selected],),
        path_classifications=paths,
        requires_explicit_migration=selected not in {
            InstallationClass.FRESH,
            InstallationClass.PROPOSAL_ONLY,
        },
        guidance=guidance,
    )


def classify_legacy_input(legacy_input: str, *, installation_exists: bool) -> LegacyBehavior:
    """Map supported legacy forms to safe canonical actions."""

    value = str(legacy_input).strip().casefold()
    if installation_exists:
        if value in {"bare", "draft-only", "apply"}:
            return LegacyBehavior(
                action="migrate",
                requires_explicit_migration=True,
                guidance="Existing SDD state requires explicit migration and inventory before changes.",
            )
        raise UnsafeLegacyBehaviorError(
            "Unsafe legacy behavior is disabled; use explicit migration with inventory and approval."
        )
    if value in {"bare", "draft-only"}:
        return LegacyBehavior(action="draft")
    if value == "apply":
        return LegacyBehavior(
            action="preview",
            preview_first=True,
            consume_existing_proposal=True,
        )
    raise UnsafeLegacyBehaviorError(
        "Unsafe legacy behavior is disabled; use explicit migration with inventory and approval."
    )


def _preserved_paths(classification: InstallationClassification) -> tuple[str, ...]:
    preserved = {
        item.path
        for item in classification.path_classifications
        if item.path_class not in {PathClass.ABSENT, PathClass.MANAGED_UNCHANGED}
    }
    if classification.installation_class in {
        InstallationClass.LEGACY_BROAD_COPY,
        InstallationClass.MIXED_CONTAMINATED,
    }:
        # The operational ledger is historical host data, never migration debris.
        preserved.add("spec-driven-development/ledger/fleet.db")
    return tuple(sorted(preserved))


def plan_migration(
    classification: InstallationClassification,
    validated_bundle: object,
    identity: object,
    prior_receipt: object | None,
) -> MigrationPlan:
    """Build a deterministic migration description without reading or writing a host."""

    del identity, prior_receipt  # Inputs are intentionally opaque to this read-only layer.
    selected = classification.installation_class
    preserved = _preserved_paths(classification)

    if selected is InstallationClass.MANAGED_CURRENT:
        return MigrationPlan(
            mode="migration",
            status="no-op",
            reason="managed installation already matches approved inputs",
            operations=(),
            preserved_paths=preserved,
            side_effects=(),
            requires_approval=False,
            requires_backup=False,
            requires_journal=False,
            write_receipt=False,
            write_operational_ledger=False,
            guidance="No changes are required.",
        )

    blocking_guidance = {
        InstallationClass.MANAGED_DRIFT: "Modified managed content is preserved; inventory and approve explicit replacement.",
        InstallationClass.LEGACY_BROAD_COPY: "Preserve the legacy tree and complete an inventory before explicit migration approval.",
        InstallationClass.PARTIAL_OR_INTERRUPTED: "Recover the interrupted transaction and inventory all destinations before migration.",
        InstallationClass.FOREIGN_COLLISION: "Detach the host link or junction and inventory its destination before migration.",
        InstallationClass.MIXED_CONTAMINATED: "Contamination, unknown work, modified files, and history are preserved pending explicit approval.",
    }
    if selected in blocking_guidance:
        return MigrationPlan(
            mode="migration",
            status="blocked",
            reason=_INSTALLATION_REASONS[selected],
            operations=(),
            preserved_paths=preserved,
            side_effects=(),
            requires_approval=True,
            requires_backup=False,
            requires_journal=False,
            write_receipt=False,
            write_operational_ledger=False,
            guidance=blocking_guidance[selected],
        )

    entries = {entry.destination: entry for entry in getattr(validated_bundle, "entries", ())}
    operations: list[MigrationOperation] = []
    for item in classification.path_classifications:
        entry = entries.get(item.path)
        if entry is None or getattr(entry, "operation", None) in {"forbid", "preserve"}:
            continue
        if item.path_class is PathClass.ABSENT:
            operations.append(MigrationOperation("create", item.path, item.reason, None, item.candidate_sha256))
    operations.sort(key=lambda operation: operation.destination)
    return MigrationPlan(
        mode="migration",
        status="planned",
        reason=_INSTALLATION_REASONS[selected],
        operations=tuple(operations),
        preserved_paths=preserved,
        side_effects=(),
        requires_approval=bool(operations),
        requires_backup=False,
        requires_journal=False,
        write_receipt=bool(operations),
        write_operational_ledger=bool(operations),
        guidance=classification.guidance,
    )
