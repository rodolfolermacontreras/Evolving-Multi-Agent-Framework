"""Canonical, side-effect-bounded brownfield orchestration service.

The public bootstrap adapter constructs :class:`BrownfieldRequest` values and
formats :class:`BrownfieldResult` values.  Policy, compatibility mapping, and
domain-error normalization live here so there is only one reachable brownfield
application route.
"""

from __future__ import annotations

import dataclasses
import hashlib
import json
import re
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from pathlib import PurePosixPath
from types import SimpleNamespace
from typing import Any

import brownfield_identity
import brownfield_inventory
import brownfield_manifest
import brownfield_migration
import brownfield_proposal
import brownfield_transaction
import host_readiness


SUPPORTED_ACTIONS = (
    "draft",
    "preview",
    "apply",
    "refresh",
    "adopt-baseline",
    "migrate",
    "recover",
    "cleanup",
    "host-doctor",
)
_SHA256 = re.compile(r"[0-9a-f]{64}\Z")

FixtureAuthorizationError = brownfield_transaction.FixtureAuthorizationError


@dataclass(frozen=True)
class BrownfieldRequest:
    action: str
    target: Path
    proposal_root: Path | None
    identity_path: Path | None
    migration: Path | None
    run_quality: bool
    preview_approval: str | None
    owner_approval_path: Path | None
    transaction_workspace: Path | None


@dataclass(frozen=True)
class BrownfieldResult:
    exit_code: int
    status: str
    message: str
    preview: object | None
    receipt_path: Path | None
    readiness: object | None
    recovery_command: str | None


@dataclass(frozen=True)
class DisposableFixtureAuthorization:
    """Unserializable test capability; never accepted by argparse or env vars."""

    target: Path
    temporary_root: Path
    fixture_root: Path


def _result(
    exit_code: int,
    status: str,
    message: str,
    *,
    preview: object | None = None,
    receipt_path: Path | None = None,
    readiness: object | None = None,
    recovery_command: str | None = None,
) -> BrownfieldResult:
    return BrownfieldResult(
        exit_code, status, message, preview, receipt_path, readiness,
        recovery_command,
    )


def _path(value: object | None) -> Path | None:
    return None if value in (None, "") else Path(str(value))


def _proposal_for(target: Path, value: object | None) -> Path:
    return _path(value) or target / ".sdd-proposal"


def request_from_args(args: object) -> BrownfieldRequest:
    """Convert the brownfield argparse namespace without consulting the environment."""

    action = getattr(args, "action", None)
    if action is None:
        return adapt_legacy_brownfield(args)
    target = Path(str(getattr(args, "target_path")))
    return BrownfieldRequest(
        action=action,
        target=target,
        proposal_root=_path(getattr(args, "proposal_root", None)),
        identity_path=_path(getattr(args, "identity", None)),
        migration=_path(getattr(args, "migration", None)),
        run_quality=bool(getattr(args, "run_quality", False)),
        preview_approval=getattr(args, "preview_hash", None),
        owner_approval_path=_path(getattr(args, "owner_approval", None)),
        transaction_workspace=_path(getattr(args, "transaction_workspace", None)),
    )


def _installation_exists(target: Path) -> bool:
    adoption = target / "spec-driven-development" / ".adoption" / "receipt.json"
    return adoption.is_file()


def adapt_legacy_brownfield(args: object) -> BrownfieldRequest:
    """Map old forms only to safe draft, preview, or explicit migration behavior."""

    target = Path(str(getattr(args, "target_path")))
    legacy = "apply" if getattr(args, "apply", False) else (
        "draft-only" if getattr(args, "draft_only", False) else "bare"
    )
    behavior = brownfield_migration.classify_legacy_input(
        legacy, installation_exists=_installation_exists(target)
    )
    proposal = _proposal_for(target, None) if behavior.consume_existing_proposal else None
    return BrownfieldRequest(
        behavior.action,
        target,
        proposal,
        None,
        None,
        False,
        None,
        None,
        None,
    )


def authorize_disposable_fixture(
    *, target: Path, temporary_root: Path
) -> DisposableFixtureAuthorization:
    """Issue a process-local fixture capability after root-bound sentinel checks."""

    target = Path(target).resolve()
    temporary_root = Path(temporary_root).resolve()
    candidates = [temporary_root]
    try:
        candidates.extend(path for path in temporary_root.iterdir() if path.is_dir())
    except OSError:
        pass
    fixture_root = next(
        (path.resolve() for path in candidates if brownfield_transaction._bound_sentinel(path)),
        None,
    )
    if fixture_root is None:
        raise FixtureAuthorizationError("a root-bound disposable fixture sentinel is required")
    try:
        target.relative_to(fixture_root)
    except ValueError:
        raise FixtureAuthorizationError("target is outside the verified fixture root") from None
    if target == fixture_root or not target.is_dir() or not (target / ".git").is_dir():
        raise FixtureAuthorizationError("target must be a disposable nested git repository")
    if brownfield_transaction._has_link_component(target, fixture_root):
        raise FixtureAuthorizationError("linked fixture targets are forbidden")
    if (target / "INSTRUCTIONS.md").exists() and (target / "spec-driven-development").exists():
        raise FixtureAuthorizationError("real framework roots cannot be fixture-authorized")
    return DisposableFixtureAuthorization(target, temporary_root, fixture_root)


def _load_json_namespace(path: Path, label: str) -> object:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        raise ValueError(f"{label} is missing or invalid") from None

    def convert(item: Any) -> Any:
        if isinstance(item, dict):
            return SimpleNamespace(**{key: convert(child) for key, child in item.items()})
        if isinstance(item, list):
            return tuple(convert(child) for child in item)
        return item

    return convert(value)


def _journal(request: BrownfieldRequest) -> Path:
    if request.transaction_workspace is None:
        raise ValueError("transaction workspace is required")
    path = request.transaction_workspace
    return path if path.suffix == ".json" else path / "transaction.json"


def _json_bytes(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, separators=(",", ":")) + "\n").encode("utf-8")


def _identity_bytes(identity: object) -> bytes:
    return _json_bytes(dataclasses.asdict(identity))


def _draft_identity(evidence: object) -> object:
    identity_evidence = {
        "target_head": evidence.target_head,
        "project_name": {"value": evidence.project_name, "evidence_paths": evidence.source_documents[:1]},
        "repo_url": {"value": evidence.remotes[0] if evidence.remotes else None, "evidence_paths": ()},
        "default_branch": {"value": evidence.default_branch, "evidence_paths": ()},
        "stack": {"value": list(evidence.stack), "evidence_paths": evidence.source_documents[:1]},
        "source_documents": {"value": list(evidence.source_documents), "evidence_paths": evidence.source_documents},
    }
    drafted = brownfield_identity.draft_identity(identity_evidence, "2026-07-13")
    return dataclasses.replace(drafted, generated_at="2026-07-13T00:00:00Z")


def _evidence_bytes(evidence: object) -> bytes:
    return _json_bytes(dataclasses.asdict(evidence))


def _proposal_documents(evidence: object) -> dict[str, bytes]:
    project = evidence.project_name
    stack = ", ".join(evidence.stack) or "unknown"
    branch = evidence.default_branch
    documents = {
        "mission.md": f"# Mission\n\nDescribe the existing mission of {project}.\n",
        "tech-stack.md": f"# Tech Stack\n\nObserved stack: {stack}.\n",
        "principles.md": "# Principles\n\nPreserve existing host behavior and require reviewed changes.\n",
        "roadmap.md": "# Roadmap\n\nValidate one small SDD adoption before broader rollout.\n",
        "decision-policy.md": f"# Decision Policy\n\nRespect the existing {branch} branch workflow.\n",
        "quality-policy.md": "# Quality Policy\n\nConfirm exact host quality commands before execution.\n",
    }
    return {f"constitution/{name}": text.encode("utf-8") for name, text in documents.items()}


def _baseline_payload(evidence: object, documents: dict[str, bytes]) -> bytes:
    files = []
    for path, content in sorted(documents.items()):
        files.append({
            "path": path,
            "sha256": hashlib.sha256(content).hexdigest(),
            "byte_length": len(content),
            "baseline_path": f".baseline/{path}",
            "renderer_id": "constitution",
            "renderer_version": "1",
            "evidence_dependencies": ["archaeology.json"],
            "text_policy": "utf-8-lf",
        })
    return _json_bytes({
        "schema_version": "1",
        "source_revision": evidence.target_head,
        "evidence_digest": evidence.evidence_digest,
        "bundle_version": "brownfield-core@1",
        "generated_at": "2026-07-13",
        "files": files,
    })


def _draft_files(evidence: object, identity: object) -> dict[str, bytes]:
    documents = _proposal_documents(evidence)
    files = {
        "archaeology.json": _evidence_bytes(evidence),
        "host-identity.json": _identity_bytes(identity),
        "baseline-manifest.json": _baseline_payload(evidence, documents),
    }
    files.update(documents)
    files.update({f".baseline/{path}": content for path, content in documents.items()})
    return files


def _file_preview(files: dict[str, bytes], root: Path) -> object:
    items = []
    for path, content in sorted(files.items()):
        destination = root / PurePosixPath(path)
        before = destination.read_bytes() if destination.is_file() else None
        items.append(brownfield_manifest.PreviewItem(
            "create" if before is None else "replace",
            f".sdd-proposal/{path}",
            "proposal-draft",
            "managed",
            "render",
            None if before is None else hashlib.sha256(before).hexdigest(),
            hashlib.sha256(content).hexdigest(),
            (),
        ))
    return brownfield_manifest.Preview("1", brownfield_manifest.PREVIEW_CATEGORIES, tuple(items))


def _execute_transaction(
    request: BrownfieldRequest,
    fixture_authorization: object | None,
    *,
    preview: object,
    target_head: str,
    candidates: dict[str, bytes],
    reviewed_proposal: Path,
    structural_check: object | None = None,
    commit_artifacts: object | None = None,
) -> tuple[object, object]:
    authorization = _authorization(
        request, fixture_authorization, preview, target_head
    )
    if request.transaction_workspace is None:
        raise ValueError("transaction workspace is required")
    request.transaction_workspace.mkdir(parents=True, exist_ok=True)
    context = brownfield_transaction.preflight(
        preview,
        authorization,
        request.target,
        request.transaction_workspace,
        target_head=target_head,
        candidate_bytes=candidates,
        reviewed_proposal=reviewed_proposal,
    )
    artifacts = commit_artifacts(context) if callable(commit_artifacts) else {}
    if artifacts:
        brownfield_transaction.bind_commit_artifacts(context, artifacts)
        candidates.update(artifacts)

    def materialize(stage_root: Path, operation: object) -> None:
        destination = stage_root / PurePosixPath(operation.destination)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(candidates[operation.destination])

    def staged_readiness(stage_root: Path, *_args: object) -> object:
        if structural_check is None:
            return SimpleNamespace(exit_code=0)
        return structural_check(stage_root, context)

    brownfield_transaction.stage_candidate(context, materialize, staged_readiness)
    brownfield_transaction.backup(context)
    return context, brownfield_transaction.promote(context)


def _authorization(
    request: BrownfieldRequest,
    fixture_authorization: object | None,
    preview: object,
    target_head: str,
) -> object:
    digest = brownfield_manifest.preview_hash(preview)
    if request.preview_approval != digest:
        raise ValueError("approved preview hash does not match the current preview")
    if fixture_authorization is not None:
        if not isinstance(fixture_authorization, DisposableFixtureAuthorization):
            raise ValueError("fixture authorization is not a live capability")
        if fixture_authorization.target != request.target.resolve():
            raise ValueError("fixture authorization target does not match")
        backup = fixture_authorization.fixture_root / f"backup-{request.action}"
        return brownfield_transaction.authorize_verified_fixture(
            target=request.target,
            fixture_root=fixture_authorization.fixture_root,
            preview_hash=digest,
            target_head=target_head,
            backup_location=str(backup),
            recovery_command=f"bootstrap.py brownfield {request.target} --action recover",
        )
    if request.owner_approval_path is None:
        raise ValueError("owner approval receipt is required")
    authorization = brownfield_transaction.load_owner_authorization(request.owner_approval_path)
    if authorization.preview_hash != digest:
        raise ValueError("owner receipt does not bind the current preview")
    return authorization


def _draft(request: BrownfieldRequest) -> BrownfieldResult:
    target = brownfield_inventory.validate_repository_root(request.target)
    proposal = _proposal_for(target, request.proposal_root)
    if proposal.exists():
        return _result(
            1,
            "blocked",
            "Reviewed proposal already exists; use preview or explicit refresh.",
        )
    evidence = brownfield_inventory.collect_repository_evidence(target)
    identity = _draft_identity(evidence)
    brownfield_proposal.generate_proposal(
        evidence, identity, Path(__file__).resolve().parents[2], "2026-07-13"
    )
    files = _draft_files(evidence, identity)
    preview = _file_preview(files, proposal)
    return _result(
        0,
        "preview",
        "Brownfield proposal draft preview is ready for exact approval.",
        preview=preview,
    )


def _persist_draft(
    request: BrownfieldRequest,
    fixture_authorization: object | None,
) -> BrownfieldResult:
    target = brownfield_inventory.validate_repository_root(request.target)
    proposal = _proposal_for(target, request.proposal_root)
    evidence = brownfield_inventory.collect_repository_evidence(target)
    identity = _draft_identity(evidence)
    files = _draft_files(evidence, identity)
    preview = _file_preview(files, proposal)
    candidates = {f".sdd-proposal/{path}": content for path, content in files.items()}
    context, promoted = _execute_transaction(
        request,
        fixture_authorization,
        preview=preview,
        target_head=evidence.target_head,
        candidates=candidates,
        reviewed_proposal=proposal,
    )
    del context
    if promoted.exit_code != 0:
        return _result(
            promoted.exit_code,
            promoted.status,
            promoted.message,
            preview=preview,
            recovery_command=promoted.recovery_command,
        )
    return _result(0, "drafted", "Reviewed proposal inputs were persisted transactionally.", preview=preview)


def _reviewed_inputs(request: BrownfieldRequest) -> tuple[Path, object, object]:
    proposal = _proposal_for(request.target, request.proposal_root)
    baseline = brownfield_proposal.load_and_validate_baseline(proposal)
    identity_path = request.identity_path or proposal / "host-identity.json"
    identity = brownfield_identity.load_identity(identity_path)
    return proposal, baseline, identity


def _framework_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _reviewed_constitution(proposal: Path, baseline: object) -> dict[str, bytes]:
    result = {}
    for item in baseline.files:
        relative = PurePosixPath(item.path)
        if len(relative.parts) != 2 or relative.parts[0] != "constitution":
            raise ValueError("reviewed proposal contains an unsupported path")
        result[relative.name] = (proposal / relative).read_bytes()
    return result


def _manifest_bytes(bundle: object) -> bytes:
    return _json_bytes(dataclasses.asdict(bundle))


def _host_text_source(path: str, identity: object) -> bytes:
    source = (_framework_root() / PurePosixPath(path)).read_text(encoding="utf-8")
    project = str(identity.fields["project_name"].value)
    source = source.replace("Evolving Multi-Agent Framework", project)
    source = source.replace("Evolving-Multi-Agent-Framework", project.replace(" ", "-"))
    source = source.replace("evolving-multi-agent-framework", project.casefold().replace(" ", "-"))
    return source.replace("\r\n", "\n").replace("\r", "\n").encode("utf-8")


def _render_bundle(
    bundle: object,
    identity: object,
    proposal: Path,
    baseline: object,
) -> tuple[dict[str, bytes], object]:
    reviewed = _reviewed_constitution(proposal, baseline)
    constitution = brownfield_identity.render_constitution(identity, reviewed)
    seeds = brownfield_manifest.build_clean_seed_bytes(bundle)
    agents = tuple(
        PurePosixPath(entry.destination).stem.removesuffix(".agent")
        for entry in bundle.entries if entry.destination.startswith(".github/agents/")
    )
    skills = tuple(
        PurePosixPath(entry.destination).parent.name
        for entry in bundle.entries if "/skills/" in entry.destination
    )
    prompts = tuple(
        PurePosixPath(entry.destination).stem.removesuffix(".prompt")
        for entry in bundle.entries if entry.destination.startswith(".github/prompts/")
    )
    roster = brownfield_identity.render_rosters(
        identity, SimpleNamespace(agents=agents, skills=skills, prompts=prompts)
    )
    rendered: dict[str, bytes] = {
        "project.config.json": brownfield_identity.render_project_config(identity),
        ".github/copilot-instructions.md": brownfield_identity.render_copilot_instructions(identity),
        "spec-driven-development/README.md": (
            f"# SDD for {identity.fields['project_name'].value}\n\nHost lifecycle assets.\n"
        ).encode("utf-8"),
        "spec-driven-development/CONTEXT.md": (
            f"# Context\n\nMission: {identity.fields['mission'].value}\n"
        ).encode("utf-8"),
        "spec-driven-development/.adoption/bundle-manifest.json": _manifest_bytes(bundle),
        "spec-driven-development/.adoption/host-identity.json": _identity_bytes(identity),
    }
    rendered.update(constitution)
    rendered.update(roster)
    rendered.update(brownfield_identity.render_seeds(identity))
    for entry in bundle.entries:
        if entry.operation != "render" or entry.destination in rendered:
            continue
        if entry.destination == "spec-driven-development/.adoption/receipt.json":
            continue
        rendered[entry.destination] = _host_text_source(entry.destination, identity)
    return rendered, seeds


def _ledger_bytes() -> bytes:
    import tempfile

    with tempfile.TemporaryDirectory() as directory:
        database = Path(directory) / "fleet.db"
        schema = (_framework_root() / "spec-driven-development/ledger/schema.sql").read_bytes()
        connection = sqlite3.connect(database)
        try:
            connection.executescript(schema.decode("utf-8"))
            connection.commit()
        finally:
            connection.close()
        return database.read_bytes()


def _candidate_bytes(
    bundle: object,
    rendered: dict[str, bytes],
    seeds: dict[str, bytes],
) -> dict[str, bytes]:
    result: dict[str, bytes] = {}
    for entry in bundle.entries:
        if not entry.enabled or entry.operation in {"preserve", "forbid"}:
            continue
        if entry.operation == "copy":
            result[entry.destination] = (_framework_root() / PurePosixPath(entry.source)).read_bytes()
        elif entry.operation == "render" and entry.destination in rendered:
            result[entry.destination] = rendered[entry.destination]
        elif entry.operation == "seed" and entry.destination.endswith("fleet.db"):
            result[entry.destination] = _ledger_bytes()
        elif entry.operation == "seed":
            result[entry.destination] = seeds[entry.destination]
    return result


def _existing_bytes(target: Path, bundle: object) -> dict[str, bytes]:
    result = {}
    for entry in bundle.entries:
        path = target / PurePosixPath(entry.destination)
        if path.is_file() and not path.is_symlink():
            result[entry.destination] = path.read_bytes()
    return result


def _receipt_namespace(payload: dict[str, object]) -> object:
    return SimpleNamespace(**payload)


def _receipt_payload(
    bundle: object,
    identity: object,
    managed_hashes: dict[str, str],
    preview_hash: str,
    transaction_id: str,
) -> dict[str, object]:
    schema = (_framework_root() / "spec-driven-development/ledger/schema.sql").read_bytes()
    return {
        "schema_version": "1",
        "bundle_id": bundle.bundle_id,
        "framework_revision": bundle.framework_revision,
        "identity_schema_version": identity.schema_version,
        "preview_hash": preview_hash,
        "transaction_id": transaction_id,
        "transaction_state": "committed",
        "managed_hashes": managed_hashes,
        "ledger_schema_sha256": hashlib.sha256(schema).hexdigest(),
        "adoption_operational_rows": {"dispatches": 0, "decisions": 0},
        "readiness_exit_code": 0,
    }


def _build_install(request: BrownfieldRequest) -> tuple[Path, object, object, object, dict[str, bytes], object]:
    target = brownfield_inventory.validate_repository_root(request.target)
    proposal, baseline, identity = _reviewed_inputs(request)
    manifest = brownfield_manifest.build_core_manifest(_framework_root(), identity)
    registry = {
        entry.renderer_id: entry.renderer_version
        for entry in manifest.entries if entry.renderer_id is not None
    }
    bundle = brownfield_manifest.validate_manifest(
        manifest, _framework_root(), target, registry
    )
    rendered, seeds = _render_bundle(bundle, identity, proposal, baseline)
    candidates = _candidate_bytes(bundle, rendered, seeds)
    existing = _existing_bytes(target, bundle)
    categories = {
        path: "preserve" if existing.get(path) == content else (
            "replace" if path in existing else "runtime-initialize" if path.endswith("fleet.db") else "create"
        )
        for path, content in candidates.items()
    }
    categories["spec-driven-development/.adoption/receipt.json"] = "preserve"
    preview = brownfield_manifest.build_preview(bundle, existing, rendered, seeds, categories)
    preview = dataclasses.replace(
        preview,
        items=tuple(
            dataclasses.replace(
                item,
                after_sha256=hashlib.sha256(candidates[item.destination]).hexdigest(),
            )
            if item.category == "runtime-initialize" else item
            for item in preview.items
        ),
    )
    return proposal, baseline, identity, bundle, candidates, preview


def _preview(request: BrownfieldRequest) -> BrownfieldResult:
    proposal, baseline, identity, bundle, candidates, preview = _build_install(request)
    del proposal, baseline, identity, bundle, candidates
    mutable = tuple(item for item in preview.items if item.category in {"create", "replace", "runtime-initialize"})
    if not mutable:
        return _result(0, "no-op", "Installed bundle already matches reviewed inputs.", preview=preview)
    return _result(
        0,
        "preview",
        "Reviewed proposal preview is ready.",
        preview=preview,
    )


def _apply(request: BrownfieldRequest, fixture_authorization: object | None) -> BrownfieldResult:
    # Normal apply deliberately begins by consuming reviewed proposal/baseline.
    # It never calls inventory-driven generation or refresh.
    proposal, baseline, identity, bundle, candidates, preview = _build_install(request)
    del baseline
    mutable = tuple(item for item in preview.items if item.category in {"create", "replace", "runtime-initialize"})
    if not mutable:
        return _result(0, "no-op", "Installed bundle already matches reviewed inputs.", preview=preview)
    if request.preview_approval is None or not _SHA256.fullmatch(request.preview_approval):
        return _result(2, "invalid", "A valid approved preview hash is required.", preview=preview)
    managed_hashes = {
        path: hashlib.sha256(content).hexdigest()
        for path, content in candidates.items()
        if path not in {
            "spec-driven-development/cli/bootstrap.py",
            "spec-driven-development/cli/brownfield_manifest.py",
        }
    }

    def receipt_artifacts(context: object) -> dict[str, bytes]:
        payload = _receipt_payload(
            bundle, identity, managed_hashes, context.preview_hash, context.transaction_id
        )
        return {"spec-driven-development/.adoption/receipt.json": _json_bytes(payload)}

    def staged_readiness(stage_root: Path, context: object) -> object:
        payload = json.loads(
            candidates["spec-driven-development/.adoption/receipt.json"]
        )
        allowed = tuple(entry.destination for entry in bundle.entries if entry.enabled)
        view = host_readiness.staged_root_view(request.target, stage_root, allowed)
        return host_readiness.run_structural_checks(
            view, bundle, identity, _receipt_namespace(payload), staged=True
        )

    context, promoted = _execute_transaction(
        request,
        fixture_authorization,
        preview=preview,
        target_head=identity.target_head,
        candidates=candidates,
        reviewed_proposal=proposal,
        structural_check=staged_readiness,
        commit_artifacts=receipt_artifacts,
    )
    if promoted.exit_code != 0:
        return _result(
            promoted.exit_code,
            promoted.status,
            promoted.message,
            preview=preview,
            recovery_command=promoted.recovery_command,
        )

    receipt_payload = _receipt_payload(
        bundle, identity, managed_hashes, context.preview_hash, context.transaction_id
    )
    receipt_path = request.target / "spec-driven-development/.adoption/receipt.json"
    readiness = host_readiness.run_structural_checks(
        request.target, bundle, identity, _receipt_namespace(receipt_payload), staged=False
    )
    if readiness.exit_code != 0:
        rolled_back = brownfield_transaction.rollback(context)
        return _result(
            rolled_back.exit_code,
            rolled_back.status,
            "Final host readiness failed; transaction was rolled back.",
            preview=preview,
            readiness=readiness,
            recovery_command=rolled_back.recovery_command,
        )
    return _result(
        0,
        "installed",
        host_readiness.format_readiness_summary(readiness, installed=True),
        preview=preview,
        receipt_path=receipt_path,
        readiness=readiness,
        recovery_command=promoted.recovery_command,
    )


def _candidate_constitution(evidence: object) -> dict[str, bytes]:
    return _proposal_documents(evidence)


def _proposal_plan_files(
    evidence: object,
    plan: object,
) -> dict[str, bytes]:
    candidate_documents = {
        item.path: item.candidate_bytes for item in plan.items
    }
    files: dict[str, bytes] = {
        "archaeology.json": _evidence_bytes(evidence),
        "baseline-manifest.json": _baseline_payload(evidence, candidate_documents),
    }
    for item in plan.items:
        if item.result_bytes is None:
            raise brownfield_proposal.ProposalConflictError(
                "proposal plan contains an unresolved conflict"
            )
        files[item.reviewed_destination] = item.result_bytes
        files[item.baseline_destination] = item.candidate_bytes
    return files


def _proposal_action(
    request: BrownfieldRequest,
    fixture_authorization: object | None,
    *,
    adoption: bool,
) -> BrownfieldResult:
    proposal = _proposal_for(request.target, request.proposal_root)
    brownfield_inventory.validate_repository_root(request.target)
    evidence = brownfield_inventory.collect_repository_evidence(request.target)
    candidates = _candidate_constitution(evidence)
    plan = (
        brownfield_proposal.plan_baseline_adoption(proposal, candidates)
        if adoption
        else brownfield_proposal.plan_refresh(proposal, candidates)
    )
    status = "baseline-adoption-plan" if adoption else "refresh-plan"
    return _result(
        1,
        status,
        "Proposal action requires explicit conflict resolution.",
        preview=plan,
    ) if plan.requires_resolution else _execute_proposal_plan(
        request,
        fixture_authorization,
        evidence,
        plan,
        status,
        "baseline-adopted" if adoption else "refreshed",
    )


def _execute_proposal_plan(
    request: BrownfieldRequest,
    fixture_authorization: object | None,
    evidence: object,
    plan: object,
    plan_status: str,
    committed_status: str,
) -> BrownfieldResult:
    proposal = _proposal_for(request.target, request.proposal_root)
    files = _proposal_plan_files(evidence, plan)
    preview = _file_preview(files, proposal)
    if request.preview_approval is None:
        return _result(0, plan_status, "Proposal-only preview is ready.", preview=preview)
    candidates = {f".sdd-proposal/{path}": content for path, content in files.items()}
    _, promoted = _execute_transaction(
        request,
        fixture_authorization,
        preview=preview,
        target_head=evidence.target_head,
        candidates=candidates,
        reviewed_proposal=proposal,
    )
    if promoted.exit_code != 0:
        return _result(
            promoted.exit_code,
            promoted.status,
            promoted.message,
            preview=preview,
            recovery_command=promoted.recovery_command,
        )
    return _result(
        0,
        committed_status,
        "Approved proposal-only transaction committed.",
        preview=preview,
        recovery_command=promoted.recovery_command,
    )


def _refresh(
    request: BrownfieldRequest,
    fixture_authorization: object | None,
) -> BrownfieldResult:
    return _proposal_action(
        request, fixture_authorization, adoption=False
    )


def _adopt_baseline(
    request: BrownfieldRequest,
    fixture_authorization: object | None,
) -> BrownfieldResult:
    return _proposal_action(
        request, fixture_authorization, adoption=True
    )


def _prior_receipt(target: Path) -> object | None:
    path = target / "spec-driven-development/.adoption/receipt.json"
    return _load_json_namespace(path, "adoption receipt") if path.is_file() else None


def _migration(
    request: BrownfieldRequest,
    fixture_authorization: object | None,
) -> BrownfieldResult:
    target = brownfield_inventory.validate_repository_root(request.target)
    proposal = _proposal_for(target, request.proposal_root)
    identity_path = request.identity_path or proposal / "host-identity.json"
    identity = brownfield_identity.load_identity(identity_path)
    manifest = brownfield_manifest.build_core_manifest(_framework_root(), identity)
    registry = {
        entry.renderer_id: entry.renderer_version
        for entry in manifest.entries if entry.renderer_id is not None
    }
    bundle = brownfield_manifest.validate_manifest(manifest, _framework_root(), target, registry)
    inventory = brownfield_inventory.inventory_target(
        target, (entry.destination for entry in bundle.entries), ()
    )
    receipt = _prior_receipt(target)
    classes = tuple(
        brownfield_migration.classify_path(observation, entry, receipt)
        for observation, entry in zip(inventory.observations, bundle.entries)
    )
    classification = brownfield_migration.classify_installation(
        inventory, classes, SimpleNamespace(exists=proposal.is_dir())
    )
    plan = brownfield_migration.plan_migration(classification, bundle, identity, receipt)
    if plan.status == "no-op":
        return _result(0, "no-op", plan.guidance, preview=plan)
    if plan.status != "planned":
        return _result(1, "migration-plan", plan.guidance, preview=plan)
    proposal, baseline, identity, bundle, candidates, preview = _build_install(request)
    del proposal, baseline, identity, bundle, candidates
    if request.preview_approval is None:
        return _result(0, "migration-plan", plan.guidance, preview=preview)
    applied = _apply(request, fixture_authorization)
    if applied.exit_code != 0:
        return applied
    return _result(
        0,
        "migrated",
        applied.message,
        preview=applied.preview,
        receipt_path=applied.receipt_path,
        readiness=applied.readiness,
        recovery_command=applied.recovery_command,
    )


def _host_doctor(request: BrownfieldRequest) -> BrownfieldResult:
    identity_path = request.identity_path
    if identity_path is None:
        raise ValueError("confirmed identity path is required for host-doctor")
    identity = brownfield_identity.load_identity(identity_path)
    if request.run_quality:
        report = host_readiness.run_quality_checks(request.target, identity, lambda _text: None)
    else:
        adoption = request.target / "spec-driven-development" / ".adoption"
        bundle = _load_json_namespace(adoption / "bundle-manifest.json", "bundle manifest")
        receipt = _load_json_namespace(adoption / "receipt.json", "adoption receipt")
        report = host_readiness.run_structural_checks(
            request.target, bundle, identity, receipt, staged=False
        )
    return _result(
        report.exit_code,
        "ok" if report.exit_code == 0 else "blocked",
        host_readiness.format_readiness_summary(report, installed=True),
        readiness=report,
    )


def _domain_result(error: Exception) -> BrownfieldResult:
    if isinstance(error, brownfield_transaction.RecoveryRequiredError):
        return _result(
            3,
            "recovery-required",
            "Brownfield recovery is required; retained evidence was not removed.",
        )
    invalid = (
        ValueError,
        TypeError,
        brownfield_inventory.BrownfieldInventoryError,
        host_readiness.ReadinessConfigurationError,
    )
    conflict = (
        brownfield_proposal.ProposalConflictError,
        brownfield_transaction.PreflightError,
        brownfield_transaction.StagingError,
        brownfield_transaction.TransactionLockedError,
    )
    if isinstance(error, conflict):
        return _result(1, "blocked", "Brownfield operation is blocked; review the retained evidence and remediation.")
    if isinstance(error, invalid):
        return _result(2, "invalid", "Brownfield inputs are invalid; review the requested action and paths.")
    return _result(1, "failed", "Brownfield operation failed unexpectedly.")


def execute(
    request: BrownfieldRequest,
    *,
    fixture_authorization: object | None = None,
) -> BrownfieldResult:
    """Execute exactly one canonical action and return presentation-free output."""

    try:
        if request.action not in SUPPORTED_ACTIONS:
            raise ValueError("unsupported brownfield action")
        if request.action == "draft":
            return (
                _persist_draft(request, fixture_authorization)
                if request.preview_approval is not None
                else _draft(request)
            )
        if request.action == "preview":
            return _preview(request)
        if request.action == "apply":
            return _apply(request, fixture_authorization)
        if request.action == "refresh":
            return _refresh(request, fixture_authorization)
        if request.action == "adopt-baseline":
            return _adopt_baseline(request, fixture_authorization)
        if request.action == "migrate":
            return _migration(request, fixture_authorization)
        if request.action == "recover":
            transaction = brownfield_transaction.recover(_journal(request), action="rollback")
            return _result(
                transaction.exit_code,
                transaction.status,
                transaction.message,
                recovery_command=transaction.recovery_command,
            )
        if request.action == "cleanup":
            transaction = brownfield_transaction.cleanup(_journal(request))
            return _result(
                transaction.exit_code,
                transaction.status,
                transaction.message,
                recovery_command=transaction.recovery_command,
            )
        return _host_doctor(request)
    except Exception as error:
        return _domain_result(error)
