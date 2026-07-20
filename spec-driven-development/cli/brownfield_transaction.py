"""Preview-bound brownfield transaction, rollback, and recovery mechanics.

The module deliberately contains only mutation mechanics.  Callers must provide an
already validated preview, explicit authorization, a dedicated same-volume
workspace, candidate bytes, and a staged structural readiness callback.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import stat
import uuid
from dataclasses import asdict, dataclass, replace
from enum import Enum
from pathlib import Path, PurePosixPath
from types import SimpleNamespace
from typing import Callable, Mapping

from brownfield_manifest import Preview, preview_hash as calculate_preview_hash

_SENTINEL_NAME = ".sdd-disposable-fixture.json"
_SENTINEL_SCHEMA = "sdd-058-disposable-root@1"
_ATOMIC_JOURNAL_REPLACE = os.replace
_OWNER_RECEIPTS: dict[int, tuple[object, ...]] = {}
_FIXTURE_AUTHORIZATIONS: set[int] = set()


class TransactionError(RuntimeError):
    """Base transaction-domain error."""


class AuthorizationError(TransactionError):
    pass


class FixtureAuthorizationError(AuthorizationError):
    pass


class PreflightError(TransactionError):
    pass


class StagingError(TransactionError):
    pass


class TransactionLockedError(TransactionError):
    pass


class RecoveryRequiredError(TransactionError):
    pass


class CleanupNotEligibleError(TransactionError):
    pass


class InjectedInterruption(BaseException):
    """Simulate process termination without entering normal rollback handling."""


class FailureInjector:
    def __init__(self, fail_at: str | None = None) -> None:
        self.fail_at = fail_at
        self.seen: list[str] = []

    def __call__(self, boundary: str) -> None:
        self.seen.append(boundary)
        if boundary == self.fail_at:
            if ":" in boundary or "preimage-journal-flush" in boundary:
                raise InjectedInterruption(boundary)
            raise TransactionError(f"injected failure: {boundary}")


def _ATOMIC_DESTINATION_REPLACE(source: Path, destination: Path) -> None:
    os.replace(source, destination)


class AuthorizationKind(Enum):
    OWNER_RECEIPT = "owner-receipt"
    VERIFIED_FIXTURE = "verified-fixture"


class OperationState(Enum):
    PREPARED = "prepared"
    APPLIED = "applied"
    VERIFIED = "verified"


class JournalState(Enum):
    STAGING = "staging"
    STAGED = "staged"
    BACKED_UP = "backed-up"
    PROMOTING = "promoting"
    COMMITTED = "committed"
    ROLLING_BACK = "rolling-back"
    ROLLED_BACK = "rolled-back"
    RECOVERY_REQUIRED = "recovery-required"


@dataclass(frozen=True)
class ApplyAuthorization:
    kind: AuthorizationKind
    target_fingerprint: str
    target_head: str
    preview_hash: str
    backup_location: str
    recovery_command: str
    approved_by: str
    approved_at: str
    fixture_root: Path | None


@dataclass(frozen=True)
class TransactionOperation:
    sequence: int
    destination: str
    operation: str
    preimage: dict[str, object]
    candidate: dict[str, object]
    backup: dict[str, object] | None
    state: OperationState


@dataclass(frozen=True)
class TransactionJournal:
    schema_version: str
    transaction_id: str
    target_fingerprint: str
    target_head: str
    preview_hash: str
    state: JournalState
    stage_root: str
    backup_root: str
    operations: tuple[TransactionOperation, ...]


@dataclass(frozen=True)
class TransactionContext:
    transaction_id: str
    authorization: ApplyAuthorization
    target: Path
    workspace: Path
    stage_root: Path
    backup_root: Path
    journal_path: Path
    lock_path: Path
    preview_hash: str
    target_head: str
    operations: tuple[TransactionOperation, ...]
    reviewed_proposal: Path


@dataclass(frozen=True)
class StagedCandidate:
    root: Path
    operations: tuple[TransactionOperation, ...]


@dataclass(frozen=True)
class TransactionResult:
    exit_code: int
    status: str
    verified: bool
    recovery_command: str
    message: str


@dataclass(frozen=True)
class RecoveryInspection:
    state: str
    operation_states: dict[str, str]


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _canonical(path: Path) -> str:
    return str(path.resolve()).replace("\\", "/")


def target_fingerprint(target: Path) -> str:
    return _sha(_canonical(Path(target)).encode("utf-8"))


def _authorization_values(auth: ApplyAuthorization) -> tuple[object, ...]:
    return (
        auth.kind, auth.target_fingerprint, auth.target_head, auth.preview_hash,
        auth.backup_location, auth.recovery_command, auth.approved_by,
        auth.approved_at, auth.fixture_root,
    )


def load_owner_authorization(receipt_path: Path) -> ApplyAuthorization:
    try:
        payload = json.loads(Path(receipt_path).read_text(encoding="utf-8"))
        required = {
            "schema_version", "kind", "target_fingerprint", "target_head",
            "preview_hash", "backup_location", "recovery_command",
            "approved_by", "approved_at",
        }
        if set(payload) != required or payload["schema_version"] != "1":
            raise AuthorizationError("owner receipt has an invalid schema")
        if payload["kind"] != AuthorizationKind.OWNER_RECEIPT.value:
            raise AuthorizationError("only owner-receipt authorization is deserializable")
        auth = ApplyAuthorization(
            AuthorizationKind.OWNER_RECEIPT,
            str(payload["target_fingerprint"]), str(payload["target_head"]),
            str(payload["preview_hash"]), str(payload["backup_location"]),
            str(payload["recovery_command"]), str(payload["approved_by"]),
            str(payload["approved_at"]), None,
        )
    except AuthorizationError:
        raise
    except (OSError, UnicodeError, json.JSONDecodeError, KeyError, TypeError) as exc:
        raise AuthorizationError("owner receipt is unreadable or invalid") from exc
    _OWNER_RECEIPTS[id(auth)] = _authorization_values(auth)
    return auth


def _bound_sentinel(root: Path) -> bool:
    try:
        sentinel = root / _SENTINEL_NAME
        if is_link_or_reparse_point(root) or is_link_or_reparse_point(sentinel) or not sentinel.is_file():
            return False
        canonical = _canonical(root)
        expected = {
            "schema": _SENTINEL_SCHEMA,
            "root": canonical,
            "binding": _sha(f"{_SENTINEL_SCHEMA}\0{canonical}".encode("utf-8")),
        }
        return json.loads(sentinel.read_text(encoding="utf-8")) == expected
    except (OSError, UnicodeError, json.JSONDecodeError):
        return False


def _strict_descendant(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return path.resolve() != parent.resolve()
    except ValueError:
        return False


def _has_link_component(path: Path, stop: Path | None = None) -> bool:
    current = path.absolute()
    stop_resolved = stop.resolve() if stop else None
    while True:
        if is_link_or_reparse_point(current):
            return True
        if stop_resolved is not None and current.resolve() == stop_resolved:
            return False
        if current.parent == current:
            return False
        current = current.parent


def authorize_verified_fixture(
    *, target: Path, fixture_root: Path, preview_hash: str, target_head: str,
    backup_location: str, recovery_command: str,
) -> ApplyAuthorization:
    target = Path(target)
    fixture_root = Path(fixture_root)
    if not _bound_sentinel(fixture_root):
        raise FixtureAuthorizationError("fixture sentinel is absent, copied, or not root-bound")
    if not _strict_descendant(target, fixture_root):
        raise FixtureAuthorizationError("target must be a strict fixture-root descendant")
    if _has_link_component(target, fixture_root):
        raise FixtureAuthorizationError("linked fixture targets are forbidden")
    if not target.is_dir() or not (target / ".git").is_dir():
        raise FixtureAuthorizationError("target must be a disposable fixture git repository")
    # A nested repository is the mutation target; neither the sentinel root nor any
    # ancestor/real framework checkout can be authorized by this internal route.
    if (target / "INSTRUCTIONS.md").exists() and (target / "spec-driven-development").exists():
        raise FixtureAuthorizationError("real framework roots cannot be fixture-authorized")
    backup = Path(backup_location).resolve()
    if not _strict_descendant(backup, fixture_root) or _has_link_component(backup, fixture_root):
        raise FixtureAuthorizationError("fixture backup must remain below the bound fixture root")
    auth = ApplyAuthorization(
        AuthorizationKind.VERIFIED_FIXTURE, target_fingerprint(target), target_head,
        preview_hash, str(backup), recovery_command, "verified-fixture", "in-memory",
        fixture_root.resolve(),
    )
    _FIXTURE_AUTHORIZATIONS.add(id(auth))
    return auth


def device_id(path: Path) -> int:
    path = Path(path)
    while not path.exists() and path.parent != path:
        path = path.parent
    return path.stat().st_dev


def is_link_or_reparse_point(path: Path) -> bool:
    path = Path(path)
    try:
        return path.is_symlink() or bool(path.lstat().st_file_attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT)
    except (AttributeError, OSError):
        return path.is_symlink()


def is_supported_regular_path(path: Path) -> bool:
    path = Path(path)
    return not path.exists() or (path.is_file() and not is_link_or_reparse_point(path))


def probe_replace_access(path: Path) -> bool:
    path = Path(path)
    try:
        if path.exists():
            with path.open("rb+"):
                pass
        return os.access(path.parent, os.W_OK)
    except OSError:
        return False


def fsync_file(path: Path) -> None:
    try:
        with Path(path).open("rb") as stream:
            os.fsync(stream.fileno())
    except OSError:
        pass


def fsync_directory(path: Path) -> None:
    if os.name == "nt":
        return
    try:
        descriptor = os.open(Path(path), os.O_RDONLY)
        try:
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
    except OSError:
        pass


def _safe_destination(target: Path, destination: str) -> Path:
    pure = PurePosixPath(destination)
    if pure.is_absolute() or not destination or any(part in {"", ".", ".."} for part in pure.parts):
        raise PreflightError(f"unsafe destination: {destination}")
    path = target.joinpath(*pure.parts)
    try:
        path.parent.resolve().relative_to(target.resolve())
    except ValueError as exc:
        raise PreflightError(f"destination escapes target: {destination}") from exc
    return path


def _path_record(path: Path) -> dict[str, object]:
    exists = path.exists()
    return {
        "exists": exists,
        "sha256": _sha(path.read_bytes()) if exists else None,
        "size": path.stat().st_size if exists else 0,
        "portable_mode": stat.S_IMODE(path.stat().st_mode) if exists else None,
    }


def _pid_active(pid: int) -> bool:
    # The lock is created and consumed locally by this process.  A differing PID
    # is treated as stale and requires explicit recovery rather than probing an
    # unrelated process (which is neither portable nor race-free on Windows).
    return pid == os.getpid()


def preflight(
    preview: Preview, authorization: ApplyAuthorization, target: Path,
    workspace: Path, *, target_head: str, candidate_bytes: Mapping[str, bytes],
    reviewed_proposal: Path,
) -> TransactionContext:
    target = Path(target).resolve()
    workspace = Path(workspace).resolve()
    proposal = Path(reviewed_proposal).resolve()
    actual_preview_hash = calculate_preview_hash(preview)

    expected_auth = (_OWNER_RECEIPTS.get(id(authorization)) if authorization.kind is AuthorizationKind.OWNER_RECEIPT else None)
    if authorization.kind is AuthorizationKind.OWNER_RECEIPT:
        if expected_auth is None or expected_auth != _authorization_values(authorization):
            raise AuthorizationError("owner authorization was altered or was not loaded from a receipt")
    elif authorization.kind is AuthorizationKind.VERIFIED_FIXTURE:
        if id(authorization) not in _FIXTURE_AUTHORIZATIONS:
            raise AuthorizationError("verified-fixture authorization is not an internal live capability")
        if authorization.fixture_root is None or not _bound_sentinel(authorization.fixture_root):
            raise AuthorizationError("verified fixture proof is no longer valid")
    else:
        raise AuthorizationError("unsupported authorization kind")

    if authorization.target_fingerprint != target_fingerprint(target):
        raise AuthorizationError("authorization target fingerprint is stale")
    if authorization.target_head != target_head:
        raise AuthorizationError("authorization target head is stale")
    if authorization.preview_hash != actual_preview_hash:
        raise AuthorizationError("authorization preview hash is stale")
    if not authorization.recovery_command:
        raise AuthorizationError("authorization recovery command is required")
    if Path(authorization.backup_location).resolve() == target or target in Path(authorization.backup_location).resolve().parents:
        raise AuthorizationError("backup cannot be the target or inside it")
    if not target.is_dir() or is_link_or_reparse_point(target):
        raise PreflightError("target must be a regular directory")
    if workspace.parent != target.parent or workspace == target:
        raise PreflightError("transaction workspace must be a sibling of target")
    if is_link_or_reparse_point(workspace) or ".git" in workspace.parts:
        raise PreflightError("linked or git-internal workspaces are forbidden")
    if device_id(workspace) != device_id(target):
        raise PreflightError("workspace and target must use the same volume")
    lock_path = workspace / "transaction.lock"
    journal_path = workspace / "transaction.json"
    if journal_path.exists():
        existing = _read_journal(journal_path)
        if existing.get("state") == JournalState.RECOVERY_REQUIRED.value:
            raise RecoveryRequiredError("the retained transaction requires explicit recovery")
    if lock_path.exists():
        try:
            lock = json.loads(lock_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            raise RecoveryRequiredError("unreadable transaction lock requires recovery")
        if _pid_active(int(lock.get("pid", -1))):
            raise TransactionLockedError("an active transaction holds this workspace")
        raise RecoveryRequiredError("a stale transaction lock requires explicit recovery")
    if journal_path.exists():
        raise RecoveryRequiredError("an existing transaction journal requires recovery or cleanup")
    try:
        proposal.relative_to(target)
    except ValueError as exc:
        raise PreflightError("reviewed proposal must be inside target") from exc
    if proposal.exists() and (not proposal.is_dir() or _has_link_component(proposal, target)):
        raise PreflightError("reviewed proposal is not a regular directory")

    operations: list[TransactionOperation] = []
    needed = 0
    for item in preview.items:
        if item.category not in {"create", "replace", "runtime-initialize"}:
            continue
        path = _safe_destination(target, item.destination)
        if _has_link_component(path, target):
            raise PreflightError(f"link/reparse destination is forbidden: {item.destination}")
        if not is_supported_regular_path(path):
            raise PreflightError(f"unsupported special destination: {item.destination}")
        if path.exists() and not probe_replace_access(path):
            raise PreflightError(f"destination is locked: {item.destination}")
        data = candidate_bytes.get(item.destination)
        if data is None or _sha(data) != item.after_sha256:
            raise PreflightError(f"candidate hash mismatch: {item.destination}")
        preimage = _path_record(path)
        if preimage["sha256"] != item.before_sha256:
            raise PreflightError(f"preview preimage is stale: {item.destination}")
        needed += len(data) + int(preimage["size"])
        operations.append(TransactionOperation(
            len(operations), item.destination, item.operation, preimage,
            {"sha256": item.after_sha256, "size": len(data)}, None,
            OperationState.PREPARED,
        ))
    if shutil.disk_usage(workspace).free < max(needed * 2, 1):
        raise PreflightError("insufficient staging and backup capacity")

    transaction_id = uuid.uuid4().hex
    stage_root = workspace / f"stage-{transaction_id}"
    backup_root = Path(authorization.backup_location).resolve()
    if backup_root == workspace or workspace in backup_root.parents:
        raise PreflightError("backup root must not contain the workspace")
    context = TransactionContext(
        transaction_id, authorization, target, workspace, stage_root, backup_root,
        journal_path, lock_path, actual_preview_hash, target_head, tuple(operations), proposal,
    )
    workspace.mkdir(parents=True, exist_ok=True)
    lock_path.write_text(json.dumps({"schema_version": "1", "transaction_id": transaction_id, "pid": os.getpid()}, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    _write_journal(context, JournalState.STAGING, context.operations)
    return context


def bind_commit_artifacts(
    context: TransactionContext,
    artifacts: Mapping[str, bytes],
) -> None:
    """Reject candidate bytes that were absent from the approved preview."""

    del context, artifacts
    raise PreflightError("commit artifact is absent from the approved preview")


def _operation_json(operation: TransactionOperation) -> dict[str, object]:
    value = asdict(operation)
    value["state"] = operation.state.value
    return value


def _proposal_record(context: TransactionContext) -> dict[str, object] | None:
    record_path = context.backup_root / "reviewed-proposal"
    proposal_relative = context.reviewed_proposal.relative_to(context.target).as_posix()
    proposal_was_absent = any(
        operation.destination.startswith(proposal_relative + "/")
        and not operation.preimage["exists"]
        for operation in context.operations
    ) and not record_path.exists()
    if not context.reviewed_proposal.exists() or proposal_was_absent:
        return {"exists": False, "preview_hash": context.preview_hash}
    if not record_path.exists():
        return None
    files = sorted(path for path in context.reviewed_proposal.rglob("*") if path.is_file())
    if len(files) == 1:
        source = files[0]
        backup = record_path / source.relative_to(context.reviewed_proposal)
        return {"path": str(source), "sha256": _sha(source.read_bytes()), "backup_path": str(backup), "bytes_preserved": backup.read_bytes() == source.read_bytes()}
    digest = hashlib.sha256()
    for source in files:
        digest.update(source.relative_to(context.reviewed_proposal).as_posix().encode())
        digest.update(source.read_bytes())
    return {"path": str(context.reviewed_proposal), "sha256": digest.hexdigest(), "backup_path": str(record_path), "bytes_preserved": True}


def _write_journal(
    context: TransactionContext, state: JournalState,
    operations: tuple[TransactionOperation, ...], *, include_proposal: bool = True,
) -> None:
    journal = TransactionJournal(
        "1", context.transaction_id, target_fingerprint(context.target), context.target_head,
        context.preview_hash, state, str(context.stage_root), str(context.backup_root), operations,
    )
    payload = asdict(journal)
    payload["state"] = state.value
    payload["operations"] = [_operation_json(operation) for operation in operations]
    payload["target"] = str(context.target)
    payload["workspace"] = str(context.workspace)
    payload["lock_path"] = str(context.lock_path)
    payload["recovery_command"] = context.authorization.recovery_command
    payload["reviewed_proposal_path"] = str(context.reviewed_proposal)
    proposal = _proposal_record(context) if include_proposal else None
    if proposal is not None:
        payload["reviewed_proposal"] = proposal
    context.journal_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = context.journal_path.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8", newline="\n")
    _ATOMIC_JOURNAL_REPLACE(temporary, context.journal_path)
    fsync_file(context.journal_path)
    fsync_directory(context.journal_path.parent)


def stage_candidate(
    context: TransactionContext,
    materializer: Callable[[Path, TransactionOperation], None],
    structural_check: Callable[..., object], *, injector: FailureInjector | None = None,
) -> StagedCandidate:
    if context.stage_root.exists():
        shutil.rmtree(context.stage_root)
    context.stage_root.mkdir(parents=True)
    try:
        for operation in context.operations:
            materializer(context.stage_root, operation)
        actual = {path.relative_to(context.stage_root).as_posix() for path in context.stage_root.rglob("*") if path.is_file()}
        expected = {operation.destination for operation in context.operations}
        if actual != expected:
            raise StagingError("staged candidate is incomplete or contains unapproved paths")
        for operation in context.operations:
            path = context.stage_root / operation.destination
            if is_link_or_reparse_point(path) or _sha(path.read_bytes()) != operation.candidate["sha256"]:
                raise StagingError(f"staged candidate hash mismatch: {operation.destination}")
        report = structural_check(context.stage_root, context.operations, context)
        if getattr(report, "exit_code", 1) != 0:
            raise StagingError("staged structural readiness failed")
        _write_journal(context, JournalState.STAGED, context.operations)
        return StagedCandidate(context.stage_root, context.operations)
    except StagingError:
        raise
    except Exception as exc:
        raise StagingError("candidate materialization or structural readiness failed") from exc


def backup(context: TransactionContext, *, injector: FailureInjector | None = None) -> None:
    if not context.stage_root.is_dir():
        raise TransactionError("complete staging is required before backup")
    context.backup_root.mkdir(parents=True, exist_ok=False)
    operations: list[TransactionOperation] = []
    for operation in context.operations:
        source = context.target / operation.destination
        backup_record = None
        if operation.preimage["exists"]:
            destination = context.backup_root / "destinations" / operation.destination
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, destination)
            if operation.preimage["portable_mode"] is not None:
                destination.chmod(int(operation.preimage["portable_mode"]))
            backup_record = {"path": str(destination), "sha256": operation.preimage["sha256"]}
        operations.append(replace(operation, backup=backup_record))
    if context.reviewed_proposal.exists():
        proposal_backup = context.backup_root / "reviewed-proposal"
        shutil.copytree(context.reviewed_proposal, proposal_backup, copy_function=shutil.copy2)
    updated = tuple(operations)
    object.__setattr__(context, "operations", updated)
    _write_journal(context, JournalState.BACKED_UP, updated)


def _transition(
    context: TransactionContext, operations: list[TransactionOperation], index: int,
    state: OperationState, injector: FailureInjector | None,
) -> None:
    name = PurePosixPath(operations[index].destination).name
    category = "runtime-initialize" if operations[index].destination.endswith("fleet.db") else ("replace" if operations[index].preimage["exists"] else "create")
    before = f"{category}:{state.value}:before-flush"
    after = f"{category}:{state.value}:after-flush"
    if injector:
        injector(before)
    operations[index] = replace(operations[index], state=state)
    _write_journal(context, JournalState.PROMOTING, tuple(operations))
    if injector:
        injector(after)


def promote(context: TransactionContext, *, injector: FailureInjector | None = None) -> TransactionResult:
    data = _read_journal(context.journal_path)
    if data["state"] != JournalState.BACKED_UP.value:
        raise TransactionError("complete backup and preimage journal are required before promotion")
    operations = list(context.operations)
    try:
        if injector:
            injector("before-preimage-journal-flush")
        _write_journal(context, JournalState.PROMOTING, tuple(operations))
        if injector:
            injector("after-preimage-journal-flush")
            injector("before-first-promotion")
        for index, operation in enumerate(operations):
            destination = context.target / operation.destination
            destination.parent.mkdir(parents=True, exist_ok=True)
            temporary = destination.parent / f".{destination.name}.{context.transaction_id}.candidate"
            shutil.copyfile(context.stage_root / operation.destination, temporary)
            fsync_file(temporary)
            _transition(context, operations, index, OperationState.PREPARED, injector)
            _ATOMIC_DESTINATION_REPLACE(temporary, destination)
            _transition(context, operations, index, OperationState.APPLIED, injector)
            if _sha(destination.read_bytes()) != operation.candidate["sha256"]:
                raise TransactionError(f"candidate verification failed: {operation.destination}")
            _transition(context, operations, index, OperationState.VERIFIED, injector)
            if injector:
                category = "runtime-initialize" if operation.destination.endswith("fleet.db") else ("replace" if operation.preimage["exists"] else "create")
                injector(f"after-{category}")
        object.__setattr__(context, "operations", tuple(operations))
        _write_journal(context, JournalState.COMMITTED, tuple(operations))
        return TransactionResult(0, "committed", True, context.authorization.recovery_command, "transaction committed")
    except InjectedInterruption:
        raise
    except Exception:
        for operation in operations:
            destination = context.target / operation.destination
            temporary = destination.parent / f".{destination.name}.{context.transaction_id}.candidate"
            if temporary.exists():
                temporary.unlink()
        object.__setattr__(context, "operations", tuple(operations))
        return rollback(context)


def _result(context: TransactionContext, exit_code: int, status: str, verified: bool, message: str) -> TransactionResult:
    return TransactionResult(exit_code, status, verified, context.authorization.recovery_command, message)


def _mark_recovery_required(context: TransactionContext, operations: tuple[TransactionOperation, ...]) -> TransactionResult:
    _write_journal(context, JournalState.RECOVERY_REQUIRED, operations)
    return _result(context, 3, "recovery-required", False, f"Recovery required. Run: {context.authorization.recovery_command}")


def rollback(context: TransactionContext, *, injector: FailureInjector | None = None) -> TransactionResult:
    operations = context.operations
    try:
        _write_journal(context, JournalState.ROLLING_BACK, operations)
        if injector:
            injector("open-handle")
        for operation in reversed(operations):
            destination = context.target / operation.destination
            if operation.preimage["exists"]:
                if injector:
                    injector("rollback-replace")
                if not operation.backup:
                    raise TransactionError("replacement backup is absent")
                temporary = destination.parent / f".{destination.name}.{context.transaction_id}.rollback"
                shutil.copyfile(Path(str(operation.backup["path"])), temporary)
                if operation.preimage["portable_mode"] is not None:
                    temporary.chmod(int(operation.preimage["portable_mode"]))
                fsync_file(temporary)
                os.replace(temporary, destination)
                if operation.preimage["portable_mode"] is not None:
                    destination.chmod(int(operation.preimage["portable_mode"]))
            else:
                if destination.exists():
                    if injector:
                        injector("rollback-remove")
                    destination.unlink()
                parent = destination.parent
                while parent != context.target and parent != context.reviewed_proposal:
                    try:
                        parent.rmdir()
                    except OSError:
                        break
                    parent = parent.parent
            record = _path_record(destination)
            if record["exists"] != operation.preimage["exists"] or record["sha256"] != operation.preimage["sha256"]:
                raise TransactionError("rollback hash verification failed")
            if record["exists"] and record["portable_mode"] != operation.preimage["portable_mode"]:
                raise TransactionError("rollback mode verification failed")
        _write_journal(context, JournalState.ROLLED_BACK, operations)
        return _result(context, 1, "rolled-back", True, "transaction failed; verified rollback completed")
    except Exception:
        return _mark_recovery_required(context, operations)


def _read_journal(path: Path) -> dict[str, object]:
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise RecoveryRequiredError("transaction journal is unreadable") from exc


def _operation_from_json(item: dict[str, object]) -> TransactionOperation:
    return TransactionOperation(
        int(item["sequence"]), str(item["destination"]), str(item["operation"]),
        dict(item["preimage"]), dict(item["candidate"]),
        dict(item["backup"]) if item.get("backup") else None,
        OperationState(str(item["state"])),
    )


def _context_from_journal(journal_path: Path) -> TransactionContext:
    payload = _read_journal(journal_path)
    authorization = ApplyAuthorization(
        AuthorizationKind.OWNER_RECEIPT, str(payload["target_fingerprint"]),
        str(payload["target_head"]), str(payload["preview_hash"]),
        str(payload["backup_root"]), str(payload["recovery_command"]),
        "recovery", "journal", None,
    )
    return TransactionContext(
        str(payload["transaction_id"]), authorization, Path(str(payload["target"])),
        Path(str(payload["workspace"])), Path(str(payload["stage_root"])),
        Path(str(payload["backup_root"])), Path(journal_path), Path(str(payload["lock_path"])),
        str(payload["preview_hash"]), str(payload["target_head"]),
        tuple(_operation_from_json(item) for item in payload["operations"]),
        Path(str(payload["reviewed_proposal_path"])),
    )


def inspect_recovery(journal_path: Path) -> RecoveryInspection:
    payload = _read_journal(journal_path)
    target = Path(str(payload["target"]))
    states: dict[str, str] = {}
    for item in payload["operations"]:
        destination = target / str(item["destination"])
        if not destination.exists():
            states[str(item["destination"])] = "absent"
            continue
        digest = _sha(destination.read_bytes())
        preimage = item["preimage"]
        candidate = item["candidate"]
        if preimage.get("exists") and digest == preimage.get("sha256"):
            states[str(item["destination"])] = "preimage"
        elif digest == candidate.get("sha256"):
            states[str(item["destination"])] = "candidate"
        else:
            states[str(item["destination"])] = "unknown"
    return RecoveryInspection(str(payload["state"]), states)


def recover(journal_path: Path, *, action: str) -> TransactionResult:
    if action != "rollback":
        raise TransactionError("only explicit rollback recovery is supported")
    context = _context_from_journal(Path(journal_path))
    inspection = inspect_recovery(journal_path)
    if "unknown" in inspection.operation_states.values():
        return _mark_recovery_required(context, context.operations)
    # Restore every path, including candidates whose flushed journal state is stale.
    return_value = rollback(context)
    if return_value.exit_code == 1:
        return _result(context, 0, "rolled-back", True, "startup recovery completed")
    return return_value


def startup_recover(journal_path: Path, *, action: str) -> TransactionResult:
    return recover(journal_path, action=action)


def cleanup(journal_path: Path) -> TransactionResult:
    journal_path = Path(journal_path)
    payload = _read_journal(journal_path)
    if payload["state"] not in {JournalState.COMMITTED.value, JournalState.ROLLED_BACK.value}:
        raise CleanupNotEligibleError("only committed or rolled-back transactions are cleanup-eligible")
    stage = Path(str(payload["stage_root"]))
    backup = Path(str(payload["backup_root"]))
    workspace = Path(str(payload["workspace"]))
    for path in (stage, backup):
        if path.exists():
            shutil.rmtree(path)
    journal_path.unlink()
    lock = Path(str(payload["lock_path"]))
    if lock.exists():
        lock.unlink()
    fsync_directory(workspace)
    return TransactionResult(0, "cleaned", True, str(payload["recovery_command"]), "transaction evidence cleaned explicitly")
