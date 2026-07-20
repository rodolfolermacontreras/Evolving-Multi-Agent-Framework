"""Immutable brownfield bundle manifest, validation, and preview primitives.

This module is the executable form of ADR-026 Appendix A.  Bundle membership is
explicit and default-deny: no directory walk or glob participates in selection.
"""

from __future__ import annotations

import hashlib
import heapq
import json
import sqlite3
import subprocess
from dataclasses import asdict, dataclass, replace
from pathlib import Path, PurePosixPath
from typing import Callable, Iterable, Mapping

SCHEMA_VERSION = "1"
BUNDLE_ID = "brownfield-core@1"
FORBIDDEN_FINGERPRINT_VERSION = "1"
PREVIEW_CATEGORIES = (
    "create",
    "replace",
    "preserve",
    "conflict",
    "forbidden",
    "runtime-initialize",
)
OPERATIONS = frozenset({"copy", "render", "seed", "preserve", "forbid"})
TEXT_POLICIES = frozenset({"binary", "preserve", "utf-8-lf"})
OWNERSHIP_VALUES = frozenset({"managed", "unmanaged"})
FLEET_WORKER = ".github/instructions/fleet-workers.instructions.md"


class ManifestValidationError(ValueError):
    """Raised when a bundle violates the frozen manifest contract."""


class PreviewValidationError(ValueError):
    """Raised when preview data is not canonical or safe."""


@dataclass(frozen=True)
class BundleEntry:
    destination: str
    operation: str
    source: str | None = None
    source_sha256: str | None = None
    renderer_id: str | None = None
    renderer_version: str | None = None
    dependencies: tuple[str, ...] = ()
    text_policy: str = "utf-8-lf"
    ownership: str = "managed"
    enabled_condition: str | None = None
    enabled: bool = True


@dataclass(frozen=True)
class BundleManifest:
    schema_version: str
    bundle_id: str
    framework_revision: str
    entries: tuple[BundleEntry, ...]
    forbidden_fingerprint_version: str


@dataclass(frozen=True)
class ValidatedBundle:
    schema_version: str
    bundle_id: str
    framework_revision: str
    entries: tuple[BundleEntry, ...]
    forbidden_fingerprint_version: str
    topological_order: tuple[str, ...]


@dataclass(frozen=True)
class LedgerEvidence:
    schema_sha256: str
    operational_rows: dict[str, int]


@dataclass(frozen=True)
class FingerprintHit:
    path: str
    fingerprint: str


@dataclass(frozen=True)
class PreviewItem:
    category: str
    destination: str
    reason: str
    ownership: str
    operation: str
    before_sha256: str | None
    after_sha256: str | None
    dependencies: tuple[str, ...]


@dataclass(frozen=True)
class Preview:
    schema_version: str
    categories: tuple[str, ...]
    items: tuple[PreviewItem, ...]


def _named(prefix: str, names: tuple[str, ...], suffix: str) -> set[str]:
    return {f"{prefix}/{name}{suffix}" for name in names}


_RENDERED_IDENTITY = {
    ".github/copilot-instructions.md",
    "project.config.json",
    "spec-driven-development/README.md",
    "spec-driven-development/CONTEXT.md",
    *_named("spec-driven-development/constitution", ("mission", "tech-stack", "principles", "roadmap", "decision-policy", "quality-policy"), ".md"),
    *_named("spec-driven-development/roster", ("agents", "skills", "skill_packs"), ".json"),
    *_named("spec-driven-development/.adoption", ("bundle-manifest", "host-identity", "receipt"), ".json"),
}
_AGENTS = _named(".github/agents", ("principal-executive-manager", "principal-product-manager", "principal-architect", "principal-software-developer", "sprint-executive-manager", "developer-general", "qa-engineer-general"), ".agent.md")
_PROMPTS = _named(".github/prompts", ("ask", "triage", "clarify", "grill", "spec", "plan", "tasks", "analyze", "fleet", "implement", "qa", "retro", "state", "replan", "evolve", "constitution"), ".prompt.md")
_SKILLS = {
    *_named(".github/skills/core", ("sdd-constitution", "project-context", "constitution-sync", "pre-work-check", "git-workflow", "testing-conventions"), "/SKILL.md"),
    *_named(".github/skills/workflow", ("grill-me", "grill-with-docs", "triage", "to-spec", "to-plan", "to-tasks", "implement"), "/SKILL.md"),
    *_named(".github/skills/engineering", ("tdd", "tdd-gate", "diagnose", "code-review", "improve-architecture"), "/SKILL.md"),
    *_named(".github/skills/operational", ("em-communication-discipline", "fleet-coordinator", "handoff", "lesson-capture", "pi-planning", "respect-existing", "session-self-review", "stakeholder-pressure-defense"), "/SKILL.md"),
}
_INSTRUCTIONS = {".github/instructions/sdd-workflow.instructions.md", FLEET_WORKER}
_TEMPLATES_AND_DOCS = {
    *_named("spec-driven-development/templates", ("feature-spec", "lightweight-feature", "clarification-log", "validation", "plan", "task-list", "agent-brief", "review-report", "handoff", "level-2-decision", "stakeholder-pressure-response"), ".md"),
    "spec-driven-development/docs/ADR/TEMPLATE.md",
    "spec-driven-development/docs/CLI-PATTERN.md",
}
_EXISTING_CLI_AND_LEDGER = {
    *_named("spec-driven-development/cli", ("__init__", "bootstrap", "dedup", "fleet", "qa", "retro", "schema_lint", "done_check", "tdd_gate_check"), ".py"),
    *_named("spec-driven-development/ledger", ("__init__", "init_ledger", "ledger_cli"), ".py"),
    "spec-driven-development/ledger/schema.sql",
}
_SDD058_MODULES = _named("spec-driven-development/cli", ("brownfield_inventory", "brownfield_proposal", "brownfield_manifest", "brownfield_identity", "brownfield_migration", "brownfield_transaction", "host_readiness", "brownfield_compat"), ".py")
_SEEDS = {
    "spec-driven-development/backlog/IDEAS.md",
    "spec-driven-development/backlog/BACKLOG.md",
    *_named("spec-driven-development", ("dispatches", "specs", "sprints", "sessions", "fleet", "exec"), "/.gitkeep"),
    "spec-driven-development/ledger/fleet.db",
}
EXPECTED_DESTINATIONS = frozenset(_RENDERED_IDENTITY | _AGENTS | _PROMPTS | _SKILLS | _INSTRUCTIONS | _TEMPLATES_AND_DOCS | _EXISTING_CLI_AND_LEDGER | _SDD058_MODULES | _SEEDS)


def _read_source_bytes(root: Path, source: str) -> bytes:
    """Read exactly one allowlisted source file."""

    if source not in EXPECTED_DESTINATIONS:
        raise ManifestValidationError(f"source is not allowlisted: {source}")
    return (root / PurePosixPath(source)).read_bytes()


def _framework_revision(root: Path) -> str:
    try:
        result = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        )
        return result.stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def _worktree_enabled(identity: object) -> bool:
    try:
        field = identity.fields["worktree_profile"]
        return field.value is True and bool(field.confirmed_by)
    except (AttributeError, KeyError, TypeError):
        return False


def _renderer_for(path: str) -> str:
    if path in _AGENTS:
        return "agent"
    if path in _PROMPTS:
        return "prompt"
    if path == FLEET_WORKER:
        return "fleet-worker-instruction"
    if path.endswith("roster/agents.json") or path.endswith("roster/skills.json") or path.endswith("roster/skill_packs.json"):
        return "rosters"
    if path.startswith("spec-driven-development/constitution/"):
        return "constitution"
    if path == "project.config.json":
        return "project-config"
    if path == ".github/copilot-instructions.md":
        return "copilot-instructions"
    if path.startswith("spec-driven-development/.adoption/"):
        return "adoption"
    return "host-document"


def build_core_manifest(framework_root: Path, identity: object) -> BundleManifest:
    """Build the exact Appendix A manifest without discovering source trees."""

    root = Path(framework_root).resolve()
    entries: list[BundleEntry] = []
    rendered = _RENDERED_IDENTITY | _AGENTS | _PROMPTS | {FLEET_WORKER}
    copy_paths = (_SKILLS | (_INSTRUCTIONS - {FLEET_WORKER}) | _TEMPLATES_AND_DOCS |
                  _EXISTING_CLI_AND_LEDGER | _SDD058_MODULES)
    for destination in sorted(EXPECTED_DESTINATIONS):
        if destination in _SEEDS:
            dependencies = ("spec-driven-development/ledger/schema.sql",) if destination.endswith("fleet.db") else ()
            entry = BundleEntry(destination, "seed", dependencies=dependencies, text_policy="binary" if destination.endswith(".db") else "utf-8-lf")
        elif destination in rendered:
            renderer = _renderer_for(destination)
            condition = "worktree_profile" if destination == FLEET_WORKER else None
            entry = BundleEntry(
                destination,
                "render",
                renderer_id=renderer,
                renderer_version="1",
                enabled_condition=condition,
                enabled=_worktree_enabled(identity) if condition else True,
            )
        elif destination in copy_paths:
            content = _read_source_bytes(root, destination)
            entry = BundleEntry(
                destination,
                "copy",
                source=destination,
                source_sha256=hashlib.sha256(content).hexdigest(),
                text_policy="preserve" if destination.endswith(".sql") else "utf-8-lf",
            )
        else:  # pragma: no cover - the exhaustive frozen partition is tested
            raise AssertionError(f"unclassified Appendix A member: {destination}")
        entries.append(entry)
    return BundleManifest(
        schema_version=SCHEMA_VERSION,
        bundle_id=BUNDLE_ID,
        framework_revision=_framework_revision(root),
        entries=tuple(entries),
        forbidden_fingerprint_version=FORBIDDEN_FINGERPRINT_VERSION,
    )


def _safe_relative(path: str, label: str) -> PurePosixPath:
    if not isinstance(path, str) or not path or "\\" in path:
        raise ManifestValidationError(f"invalid {label}: {path!r}")
    pure = PurePosixPath(path)
    if pure.is_absolute() or any(part in {"", ".", ".."} for part in pure.parts):
        raise ManifestValidationError(f"unsafe {label}: {path}")
    return pure


def _stable_topological(entries: tuple[BundleEntry, ...]) -> tuple[str, ...]:
    by_path = {entry.destination: entry for entry in entries}
    indegree = {path: 0 for path in by_path}
    dependents: dict[str, list[str]] = {path: [] for path in by_path}
    for entry in entries:
        for dependency in entry.dependencies:
            if dependency not in by_path:
                raise ManifestValidationError(f"dependency is not a member: {dependency}")
            indegree[entry.destination] += 1
            dependents[dependency].append(entry.destination)
    ready = list(path for path, degree in indegree.items() if degree == 0)
    heapq.heapify(ready)
    ordered: list[str] = []
    while ready:
        path = heapq.heappop(ready)
        ordered.append(path)
        for dependent in sorted(dependents[path]):
            indegree[dependent] -= 1
            if indegree[dependent] == 0:
                heapq.heappush(ready, dependent)
    if len(ordered) != len(entries):
        raise ManifestValidationError("dependency cycle detected")
    return tuple(ordered)


def validate_manifest(
    manifest: BundleManifest,
    framework_root: Path,
    target_root: Path,
    renderer_registry: Mapping[str, str],
) -> ValidatedBundle:
    """Validate membership, provenance, containment, renderers, and closure."""

    if manifest.schema_version != SCHEMA_VERSION or manifest.bundle_id != BUNDLE_ID:
        raise ManifestValidationError("unsupported manifest version")
    if manifest.forbidden_fingerprint_version != FORBIDDEN_FINGERPRINT_VERSION:
        raise ManifestValidationError("unsupported fingerprint version")
    entries = tuple(manifest.entries)
    destinations = [entry.destination for entry in entries]
    if len(destinations) != len(set(destinations)):
        raise ManifestValidationError("duplicate destination")
    for path in destinations:
        _safe_relative(path, "destination")
    sorted_paths = sorted(destinations)
    for parent, child in zip(sorted_paths, sorted_paths[1:]):
        if child.startswith(parent + "/"):
            raise ManifestValidationError(f"ancestor destination conflict: {parent}")
    for entry in entries:
        if entry.operation not in OPERATIONS:
            raise ManifestValidationError(f"unknown operation: {entry.operation}")
        if entry.text_policy not in TEXT_POLICIES or entry.ownership not in OWNERSHIP_VALUES:
            raise ManifestValidationError("invalid operation policy")
        if entry.source is not None:
            _safe_relative(entry.source, "source")
        for dependency in entry.dependencies:
            _safe_relative(dependency, "dependency")
    order = _stable_topological(entries)
    if set(destinations) != EXPECTED_DESTINATIONS:
        raise ManifestValidationError("manifest membership differs from Appendix A")
    root = Path(framework_root).resolve()
    target = Path(target_root).resolve()
    for entry in entries:
        destination_path = (target / PurePosixPath(entry.destination)).resolve()
        if destination_path != target and target not in destination_path.parents:
            raise ManifestValidationError(f"destination escapes target: {entry.destination}")
        if entry.operation == "copy":
            if entry.source != entry.destination or entry.source_sha256 is None:
                raise ManifestValidationError(f"source/hash declaration invalid: {entry.destination}")
            source_path = (root / PurePosixPath(entry.source)).resolve()
            if source_path != root and root not in source_path.parents:
                raise ManifestValidationError(f"source escapes framework: {entry.source}")
            actual = hashlib.sha256(_read_source_bytes(root, entry.source)).hexdigest()
            if actual != entry.source_sha256:
                raise ManifestValidationError(f"source hash mismatch: {entry.source}")
            if entry.renderer_id is not None or entry.renderer_version is not None:
                raise ManifestValidationError("copy entry has renderer")
        elif entry.operation == "render":
            if not entry.renderer_id or not entry.renderer_version:
                raise ManifestValidationError("renderer declaration missing")
            if renderer_registry.get(entry.renderer_id) != entry.renderer_version:
                raise ManifestValidationError(f"renderer mismatch: {entry.renderer_id}")
            if entry.source_sha256 is not None:
                raise ManifestValidationError("render entry has source hash")
    ordered_entries = tuple({entry.destination: entry for entry in entries}[path] for path in order)
    return ValidatedBundle(
        manifest.schema_version,
        manifest.bundle_id,
        manifest.framework_revision,
        ordered_entries,
        manifest.forbidden_fingerprint_version,
        order,
    )


def build_clean_seed_bytes(bundle: BundleManifest | ValidatedBundle) -> dict[str, bytes]:
    """Return positive, host-neutral seed bytes; runtime DB is initialized later."""

    seed_paths = {entry.destination for entry in bundle.entries if entry.operation == "seed"}
    result: dict[str, bytes] = {}
    for path in sorted(seed_paths):
        if path.endswith("fleet.db"):
            continue
        if path.endswith("/.gitkeep"):
            result[path] = b""
        elif path.endswith("IDEAS.md"):
            result[path] = b"# Ideas\n\nNo host ideas have been recorded.\n"
        elif path.endswith("BACKLOG.md"):
            result[path] = b"# Backlog\n\nNo host backlog items have been recorded.\n"
    return result


def initialize_clean_ledger(database: Path, approved_schema: bytes) -> LedgerEvidence:
    """Initialize a new ledger from the approved schema with no operational rows."""

    database = Path(database)
    database.parent.mkdir(parents=True, exist_ok=True)
    if database.exists():
        database.unlink()
    schema_text = approved_schema.decode("utf-8")
    with sqlite3.connect(database) as connection:
        connection.executescript(schema_text)
        rows = {
            "dispatches": connection.execute("SELECT COUNT(*) FROM dispatches").fetchone()[0],
            "decisions": connection.execute("SELECT COUNT(*) FROM decisions").fetchone()[0],
        }
    return LedgerEvidence(hashlib.sha256(approved_schema).hexdigest(), rows)


_FINGERPRINTS = (
    ("framework-identity", (b"evolving-multi-agent-framework",)),
    ("pi-history", (b"pi-",)),
    ("sprint-history", (b"sprint",)),
    ("sdd-history", (b"sdd-",)),
    ("framework-backlog-title", (b"brownfield bootstrap preserves proposals",)),
)


def find_forbidden_fingerprints(files: Mapping[str, bytes]) -> tuple[FingerprintHit, ...]:
    """Report versioned framework-history fingerprints in candidate bytes."""

    hits: list[FingerprintHit] = []
    for path in sorted(files):
        normalized = path.replace("\\", "/")
        if Path(normalized).is_absolute() or ".." in PurePosixPath(normalized).parts:
            raise ManifestValidationError(f"unsafe fingerprint path: {path}")
        content = files[path].lower()
        for name, needles in _FINGERPRINTS:
            if any(needle in content for needle in needles):
                hits.append(FingerprintHit(normalized, name))
    return tuple(hits)


def materialize_candidate(
    bundle: BundleManifest | ValidatedBundle,
    target: Path,
    *,
    rendered_bytes: Mapping[str, bytes],
    seed_bytes: Mapping[str, bytes],
    source_reader: Callable[[str], bytes],
) -> None:
    """Materialize only individually declared and enabled file entries."""

    root = Path(target)
    for entry in bundle.entries:
        if not entry.enabled or entry.operation in {"preserve", "forbid"}:
            continue
        if entry.operation == "copy":
            assert entry.source is not None
            content = source_reader(entry.source)
        elif entry.operation == "render":
            content = rendered_bytes[entry.destination]
        elif entry.operation == "seed" and not entry.destination.endswith("fleet.db"):
            content = seed_bytes[entry.destination]
        else:
            continue
        destination = root / PurePosixPath(entry.destination)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(content)


def _hash_or_none(content: bytes | None) -> str | None:
    return None if content is None else hashlib.sha256(content).hexdigest()


def build_preview(
    validated_bundle: ValidatedBundle,
    inventory: Mapping[str, bytes] | object,
    rendered_bytes: Mapping[str, bytes],
    seed_bytes: Mapping[str, bytes],
    migration: Mapping[str, str] | object | None = None,
) -> Preview:
    """Build a deterministic six-category preview from bounded inputs.

    Inventory may be a path-to-bytes mapping or expose a ``files`` mapping.
    Migration may map destinations to explicit categories; absent paths follow
    conservative create/replace/preserve classification.
    """

    existing = inventory if isinstance(inventory, Mapping) else getattr(inventory, "files", {})
    overrides = migration if isinstance(migration, Mapping) else getattr(migration, "categories", {})
    items: list[PreviewItem] = []
    for entry in validated_bundle.entries:
        if not entry.enabled:
            continue
        before = existing.get(entry.destination)
        after: bytes | None
        if entry.operation == "copy":
            after = None  # source bytes are represented by the validated source hash
            after_hash = entry.source_sha256
        elif entry.operation == "render":
            after = rendered_bytes.get(entry.destination)
            after_hash = _hash_or_none(after)
        elif entry.operation == "seed" and entry.destination.endswith("fleet.db"):
            after = None
            after_hash = None
        elif entry.operation == "seed":
            after = seed_bytes.get(entry.destination)
            after_hash = _hash_or_none(after)
        else:
            after = None
            after_hash = None
        category = overrides.get(entry.destination) if isinstance(overrides, Mapping) else None
        if category is None:
            if entry.operation == "forbid":
                category = "forbidden"
            elif entry.operation == "preserve":
                category = "preserve"
            elif entry.operation == "seed" and entry.destination.endswith("fleet.db"):
                category = "runtime-initialize"
            elif before is None:
                category = "create"
            elif _hash_or_none(before) == after_hash:
                category = "preserve"
            elif entry.ownership == "managed":
                category = "replace"
            else:
                category = "conflict"
        items.append(PreviewItem(
            category=category,
            destination=entry.destination,
            reason=f"manifest-{entry.operation}",
            ownership=entry.ownership,
            operation=entry.operation,
            before_sha256=_hash_or_none(before),
            after_sha256=after_hash,
            dependencies=entry.dependencies,
        ))
    return validate_preview(Preview(SCHEMA_VERSION, PREVIEW_CATEGORIES, tuple(items)))


def validate_preview(preview: Preview) -> Preview:
    if preview.schema_version != SCHEMA_VERSION or tuple(preview.categories) != PREVIEW_CATEGORIES:
        raise PreviewValidationError("preview schema or categories are invalid")
    destinations: set[str] = set()
    for item in preview.items:
        if item.category not in PREVIEW_CATEGORIES:
            raise PreviewValidationError(f"unknown preview category: {item.category}")
        try:
            _safe_relative(item.destination, "destination")
        except ManifestValidationError as error:
            raise PreviewValidationError(str(error)) from error
        if item.destination in destinations:
            raise PreviewValidationError(f"duplicate preview destination: {item.destination}")
        destinations.add(item.destination)
    return preview


def canonical_preview_bytes(preview: Preview) -> bytes:
    validated = validate_preview(preview)
    payload: dict[str, object] = {"schema_version": validated.schema_version}
    for category in PREVIEW_CATEGORIES:
        category_items = []
        for item in sorted(
            (candidate for candidate in validated.items if candidate.category == category),
            key=lambda candidate: candidate.destination,
        ):
            data = asdict(item)
            data.pop("category")
            data["dependencies"] = list(item.dependencies)
            category_items.append(data)
        payload[category] = category_items
    return (json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n").encode("utf-8")


def preview_hash(preview: Preview) -> str:
    return hashlib.sha256(canonical_preview_bytes(preview)).hexdigest()
