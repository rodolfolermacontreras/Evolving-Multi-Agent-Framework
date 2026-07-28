"""RED-6 transactional apply, rollback, recovery, and cleanup contract.

Covers R-021 through R-024, R-036, R-044 and V-22, V-24, V-26,
V-28 through V-33, and V-53.  Every mutation-capable test is confined to a
positively identified disposable root below ``tmp_path``.  Owner receipts are
constructed for local fixture repositories only; no real host is inspected or
mutated.
"""

from __future__ import annotations

import gc
import hashlib
import importlib
import json
import os
import stat
import sys
import weakref
from dataclasses import fields as dataclass_fields, replace
from pathlib import Path
from types import SimpleNamespace

import pytest

CLI_DIR = Path(__file__).resolve().parent
if str(CLI_DIR) not in sys.path:
    sys.path.insert(0, str(CLI_DIR))

from brownfield_manifest import (  # noqa: E402
    PREVIEW_CATEGORIES,
    Preview,
    PreviewItem,
    preview_hash,
)
from brownfield_test_fixtures import (  # noqa: E402
    SENTINEL_NAME,
    build_node_express_fixture,
    build_python_fixture,
    copy_sentinel,
    create_disposable_root,
    make_link,
    snapshot_paths,
)

HEAD = "a" * 40
RECOVERY_COMMAND = "bootstrap brownfield recover --journal transaction.json --action rollback"
TRANSITION_BOUNDARIES = (
    "before-preimage-journal-flush",
    "after-preimage-journal-flush",
    "replace:prepared:before-flush",
    "replace:prepared:after-flush",
    "replace:applied:before-flush",
    "replace:applied:after-flush",
    "replace:verified:before-flush",
    "replace:verified:after-flush",
    "create:prepared:before-flush",
    "create:prepared:after-flush",
    "create:applied:before-flush",
    "create:applied:after-flush",
    "create:verified:before-flush",
    "create:verified:after-flush",
    "runtime-initialize:prepared:before-flush",
    "runtime-initialize:prepared:after-flush",
    "runtime-initialize:applied:before-flush",
    "runtime-initialize:applied:after-flush",
    "runtime-initialize:verified:before-flush",
    "runtime-initialize:verified:after-flush",
)


def _transaction():
    """Import the intentionally absent transaction engine inside each test."""

    return importlib.import_module("brownfield_transaction")


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _preview(
    *,
    replacement_before: bytes = b"host original\r\nsecond line\r\n",
    replacement_after: bytes = b"managed replacement\n",
    create_after: bytes = b"new managed file\n",
    runtime_after: bytes = b"fixture runtime seed\n",
) -> Preview:
    items = (
        PreviewItem(
            category="replace",
            destination="host-owned/replace.txt",
            reason="approved managed replacement",
            ownership="managed",
            operation="copy",
            before_sha256=_sha(replacement_before),
            after_sha256=_sha(replacement_after),
            dependencies=(),
        ),
        PreviewItem(
            category="create",
            destination="spec-driven-development/created.txt",
            reason="approved managed create",
            ownership="managed",
            operation="copy",
            before_sha256=None,
            after_sha256=_sha(create_after),
            dependencies=("host-owned/replace.txt",),
        ),
        PreviewItem(
            category="runtime-initialize",
            destination="spec-driven-development/ledger/fleet.db",
            reason="initialize approved zero-row runtime",
            ownership="managed",
            operation="seed",
            before_sha256=None,
            after_sha256=_sha(runtime_after),
            dependencies=("spec-driven-development/created.txt",),
        ),
    )
    return Preview("1", PREVIEW_CATEGORIES, items)


def _write_transaction_inputs(
    target: Path,
    preview: Preview,
    *,
    replacement_before: bytes = b"host original\r\nsecond line\r\n",
    replacement_after: bytes = b"managed replacement\n",
    create_after: bytes = b"new managed file\n",
    runtime_after: bytes = b"fixture runtime seed\n",
) -> tuple[Path, dict[str, bytes]]:
    replacement = target / "host-owned/replace.txt"
    replacement.parent.mkdir(parents=True, exist_ok=True)
    replacement.write_bytes(replacement_before)
    if os.name != "nt":
        replacement.chmod(0o640)
    proposal = target / ".sdd-proposal/constitution/mission.md"
    proposal.parent.mkdir(parents=True, exist_ok=True)
    proposal.write_bytes(b"# Mission\r\n\r\nOwner reviewed proposal.\r\n")
    candidates = {
        "host-owned/replace.txt": replacement_after,
        "spec-driven-development/created.txt": create_after,
        "spec-driven-development/ledger/fleet.db": runtime_after,
    }
    assert preview_hash(preview)
    return proposal, candidates


def _workspace(disposable_root: Path, target: Path, name: str = "transaction-workspace") -> Path:
    workspace = disposable_root / name
    assert workspace.parent == target.parent
    workspace.mkdir()
    return workspace


def _fixture_authorization(
    transaction, target: Path, disposable_root: Path, workspace: Path, preview: Preview
):
    backup = disposable_root / "fixture-backup"
    backup.mkdir()
    return transaction.authorize_verified_fixture(
        target=target,
        fixture_root=disposable_root,
        workspace=workspace,
        preview_hash=preview_hash(preview),
        target_head=HEAD,
        backup_location=str(backup),
        recovery_command=RECOVERY_COMMAND,
    )


def _owner_receipt_payload(
    transaction, target: Path, workspace: Path, preview: Preview, backup: Path
) -> dict[str, object]:
    return {
        "schema_version": "3",
        "kind": "owner-receipt",
        "target_fingerprint": transaction.target_fingerprint(target),
        "target_identity": transaction._identity_json(transaction._filesystem_identity(target)),
        "workspace_location": str(workspace.resolve()),
        "workspace_identity": transaction._identity_json(
            transaction._filesystem_identity(workspace)
        ),
        "target_head": HEAD,
        "preview_hash": preview_hash(preview),
        "backup_location": str(backup.resolve()),
        "backup_root_identity": transaction._identity_json(
            transaction._filesystem_identity(backup)
        ),
        "recovery_command": RECOVERY_COMMAND,
        "approved_by": "Fixture Owner",
        "approved_at": "2026-07-12T12:00:00Z",
    }


def _owner_authorization(
    transaction, target: Path, workspace: Path, preview: Preview, backup: Path
):
    backup.mkdir()
    receipt = target.parent / "fixture-owner-approval.json"
    receipt.write_text(
        json.dumps(
            _owner_receipt_payload(transaction, target, workspace, preview, backup),
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return transaction.load_owner_authorization(receipt)


def _context(
    transaction,
    target: Path,
    disposable_root: Path,
    preview: Preview,
    *,
    authorization=None,
    candidates: dict[str, bytes] | None = None,
    workspace: Path | None = None,
):
    workspace = workspace or _workspace(disposable_root, target)
    authorization = authorization or _fixture_authorization(
        transaction, target, disposable_root, workspace, preview
    )
    return transaction.preflight(
        preview,
        authorization,
        target,
        workspace,
        target_head=HEAD,
        candidate_bytes=candidates or {},
        reviewed_proposal=target / ".sdd-proposal",
    )


def _stage_and_backup(transaction, context, candidates: dict[str, bytes], *, injector=None):
    def materialize(stage_root: Path, operation) -> None:
        destination = stage_root / operation.destination
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(candidates[operation.destination])

    staged = transaction.stage_candidate(
        context,
        materialize,
        lambda root, *_args: SimpleNamespace(exit_code=0, root=root),
        injector=injector,
    )
    transaction.backup(context, injector=injector)
    return staged


def _journal(context) -> dict[str, object]:
    return json.loads(Path(context.journal_path).read_text(encoding="utf-8"))


def _rewrite_journal(context, **changes: object) -> None:
    payload = _journal(context)
    payload.update(changes)
    Path(context.journal_path).write_text(
        json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def _injector(transaction, fail_at: str):
    return transaction.FailureInjector(fail_at=fail_at)


def test_transaction_public_contract_has_exact_authorization_operation_and_journal_fields() -> None:
    transaction = _transaction()

    assert tuple(transaction.AuthorizationKind) == (
        transaction.AuthorizationKind.OWNER_RECEIPT,
        transaction.AuthorizationKind.VERIFIED_FIXTURE,
    )
    assert tuple(item.value for item in transaction.OperationState) == (
        "prepared",
        "applied",
        "verified",
    )
    assert tuple(item.value for item in transaction.JournalState) == (
        "staging",
        "staged",
        "backed-up",
        "promoting",
        "committed",
        "rolling-back",
        "rolled-back",
        "recovery-required",
    )
    assert tuple(item.name for item in dataclass_fields(transaction.ApplyAuthorization)) == (
        "kind",
        "target_fingerprint",
        "target_identity",
        "workspace_location",
        "workspace_identity",
        "target_head",
        "preview_hash",
        "backup_location",
        "backup_root_identity",
        "recovery_command",
        "approved_by",
        "approved_at",
        "fixture_root",
    )
    assert tuple(item.name for item in dataclass_fields(transaction.TransactionOperation)) == (
        "sequence",
        "destination",
        "operation",
        "preimage",
        "candidate",
        "backup",
        "state",
    )
    assert tuple(item.name for item in dataclass_fields(transaction.TransactionJournal)) == (
        "schema_version",
        "transaction_id",
        "target_fingerprint",
        "target_identity",
        "workspace_identity",
        "backup_parent_identity",
        "backup_root_identity",
        "target_head",
        "preview_hash",
        "state",
        "stage_root",
        "backup_root",
        "operations",
    )


@pytest.mark.parametrize(
    "changed_field,bad_value",
    (
        ("target_fingerprint", "0" * 64),
        ("target_head", "b" * 40),
        ("preview_hash", "c" * 64),
        ("backup_location", "wrong-backup"),
        ("recovery_command", "wrong recovery command"),
    ),
)
def test_preflight_owner_receipt_requires_exact_reviewed_authorization_fields(
    tmp_path: Path, changed_field: str, bad_value: str
) -> None:
    transaction = _transaction()
    disposable = create_disposable_root(tmp_path)
    fixture = build_python_fixture(disposable)
    preview = _preview()
    _, candidates = _write_transaction_inputs(fixture.root, preview)
    workspace = _workspace(disposable.root, fixture.root)
    backup = disposable.root / "owner-backup"
    authorization = _owner_authorization(
        transaction, fixture.root, workspace, preview, backup
    )
    invalid = replace(authorization, **{changed_field: bad_value})
    before = snapshot_paths((fixture.root,))

    with pytest.raises(transaction.AuthorizationError):
        _context(
            transaction,
            fixture.root,
            disposable.root,
            preview,
            authorization=invalid,
            candidates=candidates,
            workspace=workspace,
        )

    assert snapshot_paths((fixture.root,)) == before
    assert list(workspace.iterdir()) == []


def test_owner_receipt_is_exact_positive_authorization_for_disposable_local_host(tmp_path: Path) -> None:
    transaction = _transaction()
    disposable = create_disposable_root(tmp_path)
    fixture = build_node_express_fixture(disposable)
    preview = _preview()
    _, candidates = _write_transaction_inputs(fixture.root, preview)
    workspace = _workspace(disposable.root, fixture.root)
    backup = disposable.root / "owner-backup"
    authorization = _owner_authorization(
        transaction, fixture.root, workspace, preview, backup
    )

    context = _context(
        transaction,
        fixture.root,
        disposable.root,
        preview,
        authorization=authorization,
        candidates=candidates,
        workspace=workspace,
    )

    assert context.authorization.kind.value == "owner-receipt"
    assert context.preview_hash == preview_hash(preview)
    assert context.backup_root.resolve() == backup.resolve()
    assert context.target.resolve() == fixture.root.resolve()


@pytest.mark.parametrize(
    "target_case",
    ("fixture-root", "sibling", "ancestor", "copied-sentinel", "temp-looking", "linked"),
)
def test_verified_fixture_authorization_has_hard_positive_disposable_guard(
    tmp_path: Path, target_case: str
) -> None:
    transaction = _transaction()
    disposable = create_disposable_root(tmp_path)
    fixture = build_node_express_fixture(disposable)
    preview = _preview()
    sibling = tmp_path / "sibling"
    sibling.mkdir()
    temp_looking = tmp_path / "tmp-sdd-058-disposable-looking"
    temp_looking.mkdir()
    copied = tmp_path / "copied"
    copy_sentinel(disposable.root, copied)
    external = tmp_path / "external"
    external.mkdir()
    linked = tmp_path / "linked"
    link_created = make_link(linked, external)
    workspace = disposable.root / "authorization-workspace"
    workspace.mkdir()
    backup = disposable.root / "backup"
    backup.mkdir()
    targets = {
        "fixture-root": disposable.root,
        "sibling": sibling,
        "ancestor": tmp_path,
        "copied-sentinel": copied,
        "temp-looking": temp_looking,
        "linked": linked if link_created else linked / "missing-link-equivalent",
    }
    before = snapshot_paths((targets[target_case], fixture.root))

    with pytest.raises(transaction.FixtureAuthorizationError):
        transaction.authorize_verified_fixture(
            target=targets[target_case],
            fixture_root=disposable.root,
            workspace=workspace,
            preview_hash=preview_hash(preview),
            target_head=HEAD,
            backup_location=str(backup),
            recovery_command=RECOVERY_COMMAND,
        )

    assert snapshot_paths((targets[target_case], fixture.root)) == before


def test_verified_fixture_authorization_is_in_memory_only_and_not_owner_deserializable(tmp_path: Path) -> None:
    transaction = _transaction()
    disposable = create_disposable_root(tmp_path)
    fixture = build_python_fixture(disposable)
    preview = _preview()
    workspace = _workspace(disposable.root, fixture.root)
    authorization = _fixture_authorization(
        transaction, fixture.root, disposable.root, workspace, preview
    )
    forged = tmp_path / "forged-fixture-approval.json"
    forged.write_text(
        json.dumps(
            {
                "schema_version": "1",
                "kind": "verified-fixture",
                "target_fingerprint": authorization.target_fingerprint,
                "target_head": authorization.target_head,
                "preview_hash": authorization.preview_hash,
                "backup_location": authorization.backup_location,
                "recovery_command": authorization.recovery_command,
                "approved_by": authorization.approved_by,
                "approved_at": authorization.approved_at,
                "fixture_root": str(disposable.root),
            }
        ),
        encoding="utf-8",
    )

    assert authorization.kind.value == "verified-fixture"
    assert authorization.fixture_root == disposable.root.resolve()
    with pytest.raises(transaction.AuthorizationError):
        transaction.load_owner_authorization(forged)


def test_preflight_requires_same_volume_sibling_workspace_before_any_write(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    transaction = _transaction()
    disposable = create_disposable_root(tmp_path)
    fixture = build_python_fixture(disposable)
    preview = _preview()
    _, candidates = _write_transaction_inputs(fixture.root, preview)
    workspace = _workspace(disposable.root, fixture.root)
    real_device = fixture.root.stat().st_dev
    monkeypatch.setattr(
        transaction,
        "device_id",
        lambda path: real_device + 1 if Path(path) == workspace else real_device,
    )
    before = snapshot_paths((fixture.root, workspace))

    with pytest.raises(transaction.PreflightError, match="same.volume"):
        _context(
            transaction,
            fixture.root,
            disposable.root,
            preview,
            candidates=candidates,
            workspace=workspace,
        )

    assert snapshot_paths((fixture.root, workspace)) == before
    assert list(workspace.iterdir()) == []


@pytest.mark.parametrize("condition", ("special", "locked", "stale-head", "stale-preview", "link"))
def test_preflight_rejects_special_locked_stale_and_link_inputs_without_artifacts(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, condition: str
) -> None:
    transaction = _transaction()
    disposable = create_disposable_root(tmp_path)
    fixture = build_node_express_fixture(disposable)
    preview = _preview()
    _, candidates = _write_transaction_inputs(fixture.root, preview)
    workspace = _workspace(disposable.root, fixture.root)
    authorization = _fixture_authorization(
        transaction, fixture.root, disposable.root, workspace, preview
    )
    kwargs = {"target_head": HEAD, "candidate_bytes": candidates}
    if condition == "special":
        monkeypatch.setattr(transaction, "is_supported_regular_path", lambda _path: False)
    elif condition == "locked":
        monkeypatch.setattr(transaction, "probe_replace_access", lambda _path: False)
    elif condition == "stale-head":
        kwargs["target_head"] = "b" * 40
    elif condition == "stale-preview":
        authorization = replace(authorization, preview_hash="c" * 64)
    else:
        linked_target = disposable.root / "linked-content"
        linked_target.mkdir()
        linked = fixture.root / "host-owned/replace.txt"
        linked.unlink()
        if not make_link(linked, linked_target):
            monkeypatch.setattr(transaction, "is_link_or_reparse_point", lambda path: Path(path) == linked)
    before = snapshot_paths((fixture.root, workspace))

    with pytest.raises((transaction.PreflightError, transaction.AuthorizationError)):
        transaction.preflight(
            preview,
            authorization,
            fixture.root,
            workspace,
            reviewed_proposal=fixture.root / ".sdd-proposal",
            **kwargs,
        )

    assert snapshot_paths((fixture.root, workspace)) == before
    assert list(workspace.iterdir()) == []


def test_stage_is_complete_same_volume_and_structurally_verified_before_backup(tmp_path: Path) -> None:
    transaction = _transaction()
    disposable = create_disposable_root(tmp_path)
    fixture = build_python_fixture(disposable)
    preview = _preview()
    proposal, candidates = _write_transaction_inputs(fixture.root, preview)
    context = _context(transaction, fixture.root, disposable.root, preview, candidates=candidates)
    host_before = snapshot_paths((fixture.root, proposal))
    events: list[str] = []

    def materialize(stage_root: Path, operation) -> None:
        events.append(f"materialize:{operation.destination}")
        destination = stage_root / operation.destination
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(candidates[operation.destination])

    def structural(stage_root: Path, *_args):
        events.append("structural")
        assert stage_root.stat().st_dev == fixture.root.stat().st_dev
        assert {
            path.relative_to(stage_root).as_posix()
            for path in stage_root.rglob("*")
            if path.is_file()
        } == set(candidates)
        return SimpleNamespace(exit_code=0)

    transaction.stage_candidate(context, materialize, structural)

    assert events == [
        "materialize:host-owned/replace.txt",
        "materialize:spec-driven-development/created.txt",
        "materialize:spec-driven-development/ledger/fleet.db",
        "structural",
    ]
    assert snapshot_paths((fixture.root, proposal)) == host_before
    assert _journal(context)["state"] == "staged"
    assert list(Path(context.backup_root).iterdir()) == []


def test_failed_or_incomplete_stage_never_creates_backup_or_mutates_host(tmp_path: Path) -> None:
    transaction = _transaction()
    disposable = create_disposable_root(tmp_path)
    fixture = build_node_express_fixture(disposable)
    preview = _preview()
    proposal, candidates = _write_transaction_inputs(fixture.root, preview)
    context = _context(transaction, fixture.root, disposable.root, preview, candidates=candidates)
    before = snapshot_paths((fixture.root, proposal))

    def incomplete(stage_root: Path, operation) -> None:
        if operation.destination.endswith("replace.txt"):
            destination = stage_root / operation.destination
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(candidates[operation.destination])

    with pytest.raises(transaction.StagingError):
        transaction.stage_candidate(
            context,
            incomplete,
            lambda *_args: SimpleNamespace(exit_code=0),
        )

    assert snapshot_paths((fixture.root, proposal)) == before
    assert list(Path(context.backup_root).iterdir()) == []
    assert _journal(context)["state"] == "staging"


def test_backup_is_complete_including_reviewed_proposal_and_portable_metadata(tmp_path: Path) -> None:
    transaction = _transaction()
    disposable = create_disposable_root(tmp_path)
    fixture = build_python_fixture(disposable)
    preview = _preview()
    proposal, candidates = _write_transaction_inputs(fixture.root, preview)
    replacement = fixture.root / "host-owned/replace.txt"
    context = _context(transaction, fixture.root, disposable.root, preview, candidates=candidates)
    _stage_and_backup(transaction, context, candidates)

    journal = _journal(context)
    assert journal["state"] == "backed-up"
    assert journal["preview_hash"] == preview_hash(preview)
    assert journal["target_head"] == HEAD
    assert [item["destination"] for item in journal["operations"]] == list(candidates)
    replaced, created, runtime = journal["operations"]
    assert replaced["preimage"]["sha256"] == _sha(replacement.read_bytes())
    assert replaced["preimage"]["exists"] is True
    assert Path(replaced["backup"]["path"]).read_bytes() == replacement.read_bytes()
    assert created["preimage"]["exists"] is False
    assert created["backup"] is None
    assert runtime["preimage"]["exists"] is False
    assert runtime["backup"] is None
    proposal_record = journal["reviewed_proposal"]
    assert proposal_record["sha256"] == _sha(proposal.read_bytes())
    assert Path(proposal_record["backup_path"]).read_bytes() == proposal.read_bytes()
    assert proposal_record["bytes_preserved"] is True
    assert replaced["preimage"]["portable_mode"] == stat.S_IMODE(replacement.stat().st_mode)
    assert Path(context.journal_path).read_bytes().endswith(b"\n")


def test_backup_fsync_failure_never_reaches_backed_up(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    transaction = _transaction()
    disposable = create_disposable_root(tmp_path)
    fixture = build_python_fixture(disposable)
    preview = _preview()
    _, candidates = _write_transaction_inputs(fixture.root, preview)
    context = _context(transaction, fixture.root, disposable.root, preview, candidates=candidates)

    def materialize(stage_root: Path, operation) -> None:
        destination = stage_root / operation.destination
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(candidates[operation.destination])

    transaction.stage_candidate(
        context, materialize, lambda *_args: SimpleNamespace(exit_code=0)
    )
    monkeypatch.setattr(
        transaction, "fsync_file", lambda _path: (_ for _ in ()).throw(OSError("fsync canary"))
    )

    with pytest.raises(transaction.TransactionError, match="backup|durab"):
        transaction.backup(context)

    assert _journal(context)["state"] == "staged"


def test_multifile_proposal_backup_corruption_never_reaches_backed_up(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    transaction = _transaction()
    disposable = create_disposable_root(tmp_path)
    fixture = build_python_fixture(disposable)
    preview = _preview()
    _, candidates = _write_transaction_inputs(fixture.root, preview)
    extra = fixture.root / ".sdd-proposal/constitution/tech-stack.md"
    extra.write_bytes(b"# Tech stack\n\nFixture bytes.\n")
    context = _context(
        transaction, fixture.root, disposable.root, preview, candidates=candidates
    )

    def materialize(stage_root: Path, operation) -> None:
        destination = stage_root / operation.destination
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(candidates[operation.destination])

    transaction.stage_candidate(
        context, materialize, lambda *_args: SimpleNamespace(exit_code=0)
    )
    real_copy2 = transaction.shutil.copy2

    def corrupt_copy2(source: Path, destination: Path, *args, **kwargs) -> Path:
        result = real_copy2(source, destination, *args, **kwargs)
        if Path(source) == extra:
            Path(destination).write_bytes(b"corrupt\n")
        return result

    monkeypatch.setattr(transaction.shutil, "copy2", corrupt_copy2)

    with pytest.raises(transaction.TransactionError, match="backup|durab|verif"):
        transaction.backup(context)

    assert _journal(context)["state"] == "staged"


@pytest.mark.parametrize("failure", ["corrupt-bytes", "mode-mismatch", "directory-fsync"])
def test_backup_verification_failure_never_reaches_backed_up(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, failure: str
) -> None:
    transaction = _transaction()
    disposable = create_disposable_root(tmp_path)
    fixture = build_python_fixture(disposable)
    preview = _preview()
    _, candidates = _write_transaction_inputs(fixture.root, preview)
    context = _context(transaction, fixture.root, disposable.root, preview, candidates=candidates)

    def materialize(stage_root: Path, operation) -> None:
        destination = stage_root / operation.destination
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(candidates[operation.destination])

    transaction.stage_candidate(
        context, materialize, lambda *_args: SimpleNamespace(exit_code=0)
    )
    if failure == "corrupt-bytes":
        real_copyfile = transaction.shutil.copyfile

        def corrupt_copy(source: Path, destination: Path) -> None:
            real_copyfile(source, destination)
            Path(destination).write_bytes(b"short")

        monkeypatch.setattr(transaction.shutil, "copyfile", corrupt_copy)
    elif failure == "mode-mismatch":
        real_path_record = transaction._path_record

        def mismatched_mode(path: Path) -> dict[str, object]:
            record = real_path_record(path)
            if context.backup_root in Path(path).parents:
                record["portable_mode"] = int(record["portable_mode"]) ^ stat.S_IXUSR
            return record

        monkeypatch.setattr(transaction, "_path_record", mismatched_mode)
    else:
        monkeypatch.setattr(
            transaction, "fsync_directory",
            lambda _path: (_ for _ in ()).throw(OSError("directory fsync canary")),
        )

    with pytest.raises(transaction.TransactionError, match="backup|durab"):
        transaction.backup(context)

    assert _journal(context)["state"] == "staged"


def test_backup_revalidates_root_after_injector_before_creation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    transaction = _transaction()
    disposable = create_disposable_root(tmp_path)
    fixture = build_python_fixture(disposable)
    preview = _preview()
    _, candidates = _write_transaction_inputs(fixture.root, preview)
    context = _context(transaction, fixture.root, disposable.root, preview, candidates=candidates)
    transaction.stage_candidate(
        context,
        lambda stage_root, operation: (
            (stage_root / operation.destination).parent.mkdir(parents=True, exist_ok=True),
            (stage_root / operation.destination).write_bytes(candidates[operation.destination]),
        ),
        lambda *_args: SimpleNamespace(exit_code=0),
    )
    substituted = False
    mkdir_calls = 0
    real_check = transaction.is_link_or_reparse_point
    real_mkdir = Path.mkdir

    def check(path: Path) -> bool:
        return (substituted and Path(path) == context.backup_root) or real_check(path)

    def inject(event: str) -> None:
        nonlocal substituted
        if event == "before-backup-create":
            substituted = True

    def mkdir_canary(path: Path, *args, **kwargs) -> None:
        nonlocal mkdir_calls
        if substituted and path == context.backup_root:
            mkdir_calls += 1
            raise OSError("backup creation must not run after root substitution")
        real_mkdir(path, *args, **kwargs)

    monkeypatch.setattr(transaction, "is_link_or_reparse_point", check)
    monkeypatch.setattr(Path, "mkdir", mkdir_canary)

    with pytest.raises(transaction.TransactionError):
        transaction.backup(context, injector=inject)

    assert substituted is True
    assert mkdir_calls == 0
    assert _journal(context)["state"] == "staged"


def test_mutation_boundary_rejects_link_substitution_before_promotion(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    transaction = _transaction()
    disposable = create_disposable_root(tmp_path)
    fixture = build_python_fixture(disposable)
    preview = _preview()
    _, candidates = _write_transaction_inputs(fixture.root, preview)
    context = _context(transaction, fixture.root, disposable.root, preview, candidates=candidates)
    _stage_and_backup(transaction, context, candidates)
    guarded = fixture.root / "spec-driven-development"
    real_check = transaction.is_link_or_reparse_point
    monkeypatch.setattr(
        transaction,
        "is_link_or_reparse_point",
        lambda path: Path(path) == guarded or real_check(path),
    )

    result = transaction.promote(context)

    assert result.exit_code != 0
    assert not (fixture.root / "spec-driven-development/created.txt").exists()


def test_promotion_rejects_ordinary_directory_replacement_of_trusted_target_root(
    tmp_path: Path,
) -> None:
    transaction = _transaction()
    disposable = create_disposable_root(tmp_path)
    fixture = build_python_fixture(disposable)
    preview = _preview()
    _, candidates = _write_transaction_inputs(fixture.root, preview)
    context = _context(transaction, fixture.root, disposable.root, preview, candidates=candidates)
    _stage_and_backup(transaction, context, candidates)
    original_root = fixture.root.with_name(f"{fixture.root.name}-original")
    fixture.root.rename(original_root)
    fixture.root.mkdir()
    protected = fixture.root / "protected.txt"
    protected.write_bytes(b"replacement root bytes\n")

    with pytest.raises(transaction.TransactionError, match="filesystem identity"):
        transaction.promote(context)

    assert protected.read_bytes() == b"replacement root bytes\n"
    assert not (fixture.root / "host-owned/replace.txt").exists()
    assert not (fixture.root / "spec-driven-development").exists()


def test_restart_recovery_rejects_ordinary_directory_replacement_of_trusted_target_root(
    tmp_path: Path,
) -> None:
    transaction = _transaction()
    disposable = create_disposable_root(tmp_path)
    fixture = build_python_fixture(disposable)
    preview = _preview()
    _, candidates = _write_transaction_inputs(fixture.root, preview)
    context = _context(transaction, fixture.root, disposable.root, preview, candidates=candidates)
    _stage_and_backup(transaction, context, candidates)
    original_root = fixture.root.with_name(f"{fixture.root.name}-original")
    fixture.root.rename(original_root)
    fixture.root.mkdir()
    protected = fixture.root / "protected.txt"
    protected.write_bytes(b"replacement root bytes\n")

    with pytest.raises(transaction.RecoveryRequiredError, match="journal"):
        transaction.startup_recover(
            context.journal_path,
            action="rollback",
            workspace=context.workspace,
            target=context.target,
            authorization=context.authorization,
        )

    assert protected.read_bytes() == b"replacement root bytes\n"
    assert not (fixture.root / "host-owned").exists()
    assert not (fixture.root / "spec-driven-development").exists()


def test_stage_reset_revalidates_root_after_injector_before_rmtree(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    transaction = _transaction()
    disposable = create_disposable_root(tmp_path)
    fixture = build_python_fixture(disposable)
    preview = _preview()
    _, candidates = _write_transaction_inputs(fixture.root, preview)
    context = _context(transaction, fixture.root, disposable.root, preview, candidates=candidates)
    context.stage_root.mkdir(parents=True)
    (context.stage_root / "retained.txt").write_bytes(b"retained evidence\n")
    substituted = False
    rmtree_calls = 0
    real_check = transaction.is_link_or_reparse_point
    real_rmtree = transaction.shutil.rmtree

    def check(path: Path) -> bool:
        return (substituted and Path(path) == context.stage_root) or real_check(path)

    def inject(event: str) -> None:
        nonlocal substituted
        if event == "before-stage-reset":
            substituted = True

    def rmtree_canary(path: Path, *args, **kwargs) -> None:
        nonlocal rmtree_calls
        if substituted and Path(path) == context.stage_root:
            rmtree_calls += 1
            raise OSError("stage reset must not run after root substitution")
        real_rmtree(path, *args, **kwargs)

    monkeypatch.setattr(transaction, "is_link_or_reparse_point", check)
    monkeypatch.setattr(transaction.shutil, "rmtree", rmtree_canary)

    with pytest.raises(transaction.StagingError):
        transaction.stage_candidate(
            context,
            lambda *_args: None,
            lambda *_args: SimpleNamespace(exit_code=0),
            injector=inject,
        )

    assert substituted is True
    assert rmtree_calls == 0


def test_promotion_revalidates_parent_after_transition_before_atomic_replace(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    transaction = _transaction()
    disposable = create_disposable_root(tmp_path)
    fixture = build_python_fixture(disposable)
    preview = _preview()
    _, candidates = _write_transaction_inputs(fixture.root, preview)
    context = _context(transaction, fixture.root, disposable.root, preview, candidates=candidates)
    _stage_and_backup(transaction, context, candidates)
    guarded = fixture.root / "host-owned"
    substituted = False
    replace_calls = 0
    real_check = transaction.is_link_or_reparse_point

    def check(path: Path) -> bool:
        return (substituted and Path(path) == guarded) or real_check(path)

    def inject(event: str) -> None:
        nonlocal substituted
        if event == "replace:prepared:after-flush":
            substituted = True

    def replace_canary(_source: Path, _destination: Path) -> None:
        nonlocal replace_calls
        replace_calls += 1
        raise OSError("atomic replace must not run after parent substitution")

    monkeypatch.setattr(transaction, "is_link_or_reparse_point", check)
    monkeypatch.setattr(transaction, "_ATOMIC_DESTINATION_REPLACE", replace_canary)

    result = transaction.promote(context, injector=inject)

    assert result.exit_code == 3
    assert replace_calls == 0


def test_rollback_revalidates_link_substitution_before_destination_mutation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    transaction = _transaction()
    disposable = create_disposable_root(tmp_path)
    fixture = build_python_fixture(disposable)
    preview = _preview()
    _, candidates = _write_transaction_inputs(fixture.root, preview)
    context = _context(transaction, fixture.root, disposable.root, preview, candidates=candidates)
    _stage_and_backup(transaction, context, candidates)
    guarded = fixture.root / "host-owned"
    foreign = tmp_path / "foreign"
    foreign.mkdir()
    protected = foreign / "replace.txt"
    protected.write_bytes(b"foreign bytes\n")
    before = snapshot_paths((foreign,))
    real_check = transaction.is_link_or_reparse_point
    monkeypatch.setattr(
        transaction,
        "is_link_or_reparse_point",
        lambda path: Path(path) == guarded or real_check(path),
    )

    result = transaction.rollback(context)

    assert result.exit_code == 3
    assert snapshot_paths((foreign,)) == before


def test_rollback_revalidates_parent_after_injector_before_replace(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    transaction = _transaction()
    disposable = create_disposable_root(tmp_path)
    fixture = build_python_fixture(disposable)
    preview = _preview()
    _, candidates = _write_transaction_inputs(fixture.root, preview)
    context = _context(transaction, fixture.root, disposable.root, preview, candidates=candidates)
    _stage_and_backup(transaction, context, candidates)
    guarded = fixture.root / "host-owned"
    substituted = False
    replace_calls = 0
    real_check = transaction.is_link_or_reparse_point
    real_replace = transaction.os.replace

    def check(path: Path) -> bool:
        return (substituted and Path(path) == guarded) or real_check(path)

    def inject(event: str) -> None:
        nonlocal substituted
        if event == "rollback-replace":
            substituted = True

    def replace_canary(source: Path, destination: Path) -> None:
        nonlocal replace_calls
        if Path(destination) == fixture.root / "host-owned/replace.txt":
            replace_calls += 1
            raise OSError("rollback replace must not run after parent substitution")
        real_replace(source, destination)

    monkeypatch.setattr(transaction, "is_link_or_reparse_point", check)
    monkeypatch.setattr(transaction.os, "replace", replace_canary)

    result = transaction.rollback(context, injector=inject)

    assert result.exit_code == 3
    assert replace_calls == 0


def test_rollback_revalidates_parent_after_injector_before_unlink(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    transaction = _transaction()
    disposable = create_disposable_root(tmp_path)
    fixture = build_python_fixture(disposable)
    preview = _preview()
    _, candidates = _write_transaction_inputs(fixture.root, preview)
    context = _context(transaction, fixture.root, disposable.root, preview, candidates=candidates)
    _stage_and_backup(transaction, context, candidates)
    assert transaction.promote(context).status == "committed"
    guarded = fixture.root / "spec-driven-development"
    substituted = False
    unlink_calls = 0
    real_check = transaction.is_link_or_reparse_point
    real_unlink = Path.unlink

    def check(path: Path) -> bool:
        return (substituted and Path(path) == guarded) or real_check(path)

    def inject(event: str) -> None:
        nonlocal substituted
        if event == "rollback-remove":
            substituted = True

    def unlink_canary(path: Path, *args, **kwargs) -> None:
        nonlocal unlink_calls
        if path == fixture.root / "spec-driven-development/ledger/fleet.db":
            unlink_calls += 1
            raise OSError("rollback unlink must not run after parent substitution")
        real_unlink(path, *args, **kwargs)

    monkeypatch.setattr(transaction, "is_link_or_reparse_point", check)
    monkeypatch.setattr(Path, "unlink", unlink_canary)

    result = transaction.rollback(context, injector=inject)

    assert result.exit_code == 3
    assert unlink_calls == 0


def test_rollback_revalidates_parent_before_pruning(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    transaction = _transaction()
    disposable = create_disposable_root(tmp_path)
    fixture = build_python_fixture(disposable)
    preview = _preview()
    _, candidates = _write_transaction_inputs(fixture.root, preview)
    context = _context(transaction, fixture.root, disposable.root, preview, candidates=candidates)
    _stage_and_backup(transaction, context, candidates)
    parent = fixture.root / "spec-driven-development"
    real_mutation_destination = transaction._mutation_destination
    rejected = False

    def substitute_before_prune(target: Path, destination: str) -> Path:
        nonlocal rejected
        if Path(target) == fixture.root and destination == "spec-driven-development":
            rejected = True
            raise transaction.TransactionError("mutation destination is linked or reparsed")
        return real_mutation_destination(target, destination)

    monkeypatch.setattr(transaction, "_mutation_destination", substitute_before_prune)

    result = transaction.rollback(context)

    assert result.exit_code == 3
    assert rejected is True
    assert not parent.exists() or parent.is_dir()


def test_recovery_inspection_revalidates_link_substitution_before_destination_read(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    transaction = _transaction()
    disposable = create_disposable_root(tmp_path)
    fixture = build_python_fixture(disposable)
    preview = _preview()
    _, candidates = _write_transaction_inputs(fixture.root, preview)
    context = _context(transaction, fixture.root, disposable.root, preview, candidates=candidates)
    _stage_and_backup(transaction, context, candidates)
    guarded = fixture.root / "host-owned"
    real_check = transaction.is_link_or_reparse_point
    monkeypatch.setattr(
        transaction,
        "is_link_or_reparse_point",
        lambda path: Path(path) == guarded or real_check(path),
    )

    with pytest.raises(transaction.RecoveryRequiredError, match="journal"):
        transaction.inspect_recovery(
            context.journal_path,
            workspace=context.workspace,
            target=context.target,
            authorization=context.authorization,
        )


def test_recovery_inspection_resolves_mutation_boundary_immediately_before_read(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    transaction = _transaction()
    disposable = create_disposable_root(tmp_path)
    fixture = build_python_fixture(disposable)
    preview = _preview()
    _, candidates = _write_transaction_inputs(fixture.root, preview)
    context = _context(transaction, fixture.root, disposable.root, preview, candidates=candidates)
    _stage_and_backup(transaction, context, candidates)
    inspected = "host-owned/replace.txt"
    real_mutation_destination = transaction._mutation_destination
    calls: list[str] = []

    def reject_inspection_read(target: Path, destination: str) -> Path:
        calls.append(destination)
        if destination == inspected:
            raise transaction.TransactionError("mutation destination is linked or reparsed")
        return real_mutation_destination(target, destination)

    monkeypatch.setattr(transaction, "_mutation_destination", reject_inspection_read)

    with pytest.raises(transaction.TransactionError, match="linked|reparse"):
        transaction.inspect_recovery(
            context.journal_path,
            workspace=context.workspace,
            target=context.target,
            authorization=context.authorization,
        )

    assert inspected in calls


def test_proposal_only_transaction_allows_absent_reviewed_root_and_journals_exact_preview(
    tmp_path: Path,
) -> None:
    transaction = _transaction()
    disposable = create_disposable_root(tmp_path)
    fixture = build_python_fixture(disposable)
    content = b"# Reviewed draft\n"
    preview = Preview(
        "1",
        PREVIEW_CATEGORIES,
        (
            PreviewItem(
                "create",
                ".sdd-proposal/constitution/mission.md",
                "approved proposal draft",
                "managed",
                "render",
                None,
                _sha(content),
                (),
            ),
        ),
    )
    workspace = _workspace(disposable.root, fixture.root)
    authorization = _fixture_authorization(
        transaction, fixture.root, disposable.root, workspace, preview
    )
    context = transaction.preflight(
        preview,
        authorization,
        fixture.root,
        workspace,
        target_head=HEAD,
        candidate_bytes={".sdd-proposal/constitution/mission.md": content},
        reviewed_proposal=fixture.root / ".sdd-proposal",
    )

    _stage_and_backup(
        transaction,
        context,
        {".sdd-proposal/constitution/mission.md": content},
    )
    result = transaction.promote(context)

    assert result.exit_code == 0
    assert (fixture.root / ".sdd-proposal/constitution/mission.md").read_bytes() == content
    journal = _journal(context)
    assert journal["preview_hash"] == preview_hash(preview)
    assert journal["reviewed_proposal"] == {
        "exists": False,
        "preview_hash": preview_hash(preview),
    }


def test_bound_commit_artifact_is_staged_backed_up_and_rolled_back_on_atomic_replace_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    transaction = _transaction()
    disposable = create_disposable_root(tmp_path)
    fixture = build_python_fixture(disposable)
    receipt_relative = "spec-driven-development/.adoption/receipt.json"
    receipt = b'{"transaction_state":"committed"}\n'
    base_preview = _preview()
    preview = replace(
        base_preview,
        items=base_preview.items + (
            PreviewItem(
                "create",
                receipt_relative,
                "approved adoption receipt",
                "managed",
                "render",
                None,
                _sha(receipt),
                (),
            ),
        ),
    )
    proposal, candidates = _write_transaction_inputs(fixture.root, preview)
    candidates[receipt_relative] = receipt
    context = _context(
        transaction, fixture.root, disposable.root, preview, candidates=candidates
    )
    _stage_and_backup(transaction, context, candidates)
    before = snapshot_paths((fixture.root, proposal))
    real_replace = transaction._ATOMIC_DESTINATION_REPLACE

    def fail_receipt(source, destination) -> None:
        if Path(destination) == fixture.root / receipt_relative:
            raise OSError("fixture receipt replace failure")
        real_replace(source, destination)

    monkeypatch.setattr(transaction, "_ATOMIC_DESTINATION_REPLACE", fail_receipt)
    result = transaction.promote(context)

    assert result.exit_code == 1
    assert result.status == "rolled-back"
    assert snapshot_paths((fixture.root, proposal)) == before
    assert not (fixture.root / receipt_relative).exists()
    assert _journal(context)["state"] == "rolled-back"


def test_preflight_forbids_binding_candidate_bytes_absent_from_approved_preview(
    tmp_path: Path,
) -> None:
    transaction = _transaction()
    disposable = create_disposable_root(tmp_path)
    fixture = build_python_fixture(disposable)
    preview = _preview()
    _, candidates = _write_transaction_inputs(fixture.root, preview)
    context = _context(
        transaction, fixture.root, disposable.root, preview, candidates=candidates
    )

    with pytest.raises(
        transaction.PreflightError,
        match="approved preview",
    ):
        transaction.bind_commit_artifacts(
            context,
            {
                "spec-driven-development/.adoption/receipt.json":
                    b'{"transaction_state":"committed"}\n'
            },
        )

    assert tuple(operation.destination for operation in context.operations) == tuple(
        item.destination for item in preview.items
    )


def test_journal_and_directory_fsync_precede_every_mutation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    transaction = _transaction()
    disposable = create_disposable_root(tmp_path)
    fixture = build_node_express_fixture(disposable)
    preview = _preview()
    _, candidates = _write_transaction_inputs(fixture.root, preview)
    context = _context(transaction, fixture.root, disposable.root, preview, candidates=candidates)
    _stage_and_backup(transaction, context, candidates)
    events: list[tuple[str, str]] = []
    real_replace = transaction.os.replace

    def fsync_file(path: Path) -> None:
        events.append(("fsync-file", Path(path).name))

    def fsync_directory(path: Path) -> None:
        events.append(("fsync-directory", Path(path).name))

    def tracked_replace(source, destination) -> None:
        events.append(("replace", Path(destination).relative_to(fixture.root).as_posix()))
        real_replace(source, destination)

    monkeypatch.setattr(transaction, "fsync_file", fsync_file)
    monkeypatch.setattr(transaction, "fsync_directory", fsync_directory)
    monkeypatch.setattr(transaction.os, "replace", tracked_replace)

    transaction.promote(context)

    replace_indexes = [index for index, event in enumerate(events) if event[0] == "replace"]
    assert len(replace_indexes) == 3
    for index in replace_indexes:
        prior = events[:index]
        assert prior[-2][0] == "fsync-file"
        assert prior[-1][0] == "fsync-directory"
    assert _journal(context)["state"] == "committed"


@pytest.mark.parametrize("boundary", TRANSITION_BOUNDARIES)
def test_each_prepared_applied_verified_interruption_is_startup_recoverable(
    tmp_path: Path, boundary: str
) -> None:
    transaction = _transaction()
    disposable = create_disposable_root(tmp_path, name=f"fixtures-{hashlib.sha256(boundary.encode()).hexdigest()[:8]}")
    fixture = build_python_fixture(disposable)
    preview = _preview()
    proposal, candidates = _write_transaction_inputs(fixture.root, preview)
    original = snapshot_paths((fixture.root / "host-owned/replace.txt", fixture.root / "spec-driven-development/created.txt", proposal))
    context = _context(transaction, fixture.root, disposable.root, preview, candidates=candidates)
    _stage_and_backup(transaction, context, candidates)

    with pytest.raises(transaction.InjectedInterruption):
        transaction.promote(context, injector=_injector(transaction, boundary))

    assert Path(context.journal_path).exists()
    recovered = transaction.startup_recover(
        context.journal_path,
        action="rollback",
        workspace=context.workspace,
        target=context.target,
        authorization=context.authorization,
    )
    assert recovered.exit_code == 0
    assert snapshot_paths((fixture.root / "host-owned/replace.txt", fixture.root / "spec-driven-development/created.txt", proposal)) == original
    assert _journal(context)["state"] == "rolled-back"


def test_recovery_rejects_journal_selected_foreign_target_without_mutation(
    tmp_path: Path,
) -> None:
    transaction = _transaction()
    disposable = create_disposable_root(tmp_path)
    fixture = build_python_fixture(disposable)
    preview = _preview()
    _, candidates = _write_transaction_inputs(fixture.root, preview)
    context = _context(
        transaction, fixture.root, disposable.root, preview, candidates=candidates
    )
    _stage_and_backup(transaction, context, candidates)
    foreign = tmp_path / "foreign"
    foreign.mkdir()
    protected = foreign / "protected.txt"
    protected.write_bytes(b"do not read or mutate\n")
    before = snapshot_paths((foreign,))
    _rewrite_journal(
        context,
        target=str(foreign.resolve()),
        target_fingerprint=transaction.target_fingerprint(foreign),
    )

    with pytest.raises(transaction.RecoveryRequiredError, match="journal"):
        transaction.recover(
            context.journal_path,
            action="rollback",
            workspace=context.workspace,
            target=context.target,
            authorization=context.authorization,
        )

    assert snapshot_paths((foreign,)) == before


def test_recovery_rejects_forged_equal_authorization_without_mutation(
    tmp_path: Path,
) -> None:
    transaction = _transaction()
    disposable = create_disposable_root(tmp_path)
    fixture = build_python_fixture(disposable)
    preview = _preview()
    _, candidates = _write_transaction_inputs(fixture.root, preview)
    context = _context(
        transaction, fixture.root, disposable.root, preview, candidates=candidates
    )
    _stage_and_backup(transaction, context, candidates)
    before = snapshot_paths((fixture.root, context.workspace, context.backup_root))
    forged = replace(context.authorization)

    with pytest.raises(transaction.AuthorizationError, match="registered"):
        transaction.recover(
            context.journal_path,
            action="rollback",
            workspace=context.workspace,
            target=context.target,
            authorization=forged,
        )

    assert snapshot_paths((fixture.root, context.workspace, context.backup_root)) == before


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("preview_hash", "b" * 64),
        ("target_head", "c" * 40),
        ("backup_root", "foreign-backup"),
        ("recovery_command", "run forged recovery"),
    ),
)
def test_recovery_rejects_journal_authorization_field_tampering_without_mutation(
    tmp_path: Path, field: str, value: str
) -> None:
    transaction = _transaction()
    disposable = create_disposable_root(tmp_path)
    fixture = build_python_fixture(disposable)
    preview = _preview()
    _, candidates = _write_transaction_inputs(fixture.root, preview)
    context = _context(
        transaction, fixture.root, disposable.root, preview, candidates=candidates
    )
    _stage_and_backup(transaction, context, candidates)
    tampered = value
    if field == "backup_root":
        tampered = str((tmp_path / value).resolve())
        Path(tampered).mkdir()
    _rewrite_journal(context, **{field: tampered})
    before = snapshot_paths((fixture.root, context.workspace, context.backup_root))

    with pytest.raises(
        (transaction.AuthorizationError, transaction.RecoveryRequiredError)
    ):
        transaction.recover(
            context.journal_path,
            action="rollback",
            workspace=context.workspace,
            target=context.target,
            authorization=context.authorization,
        )

    assert snapshot_paths((fixture.root, context.workspace, context.backup_root)) == before


def test_cleanup_rejects_forged_equal_authorization_without_deleting_evidence(
    tmp_path: Path,
) -> None:
    transaction = _transaction()
    disposable = create_disposable_root(tmp_path)
    fixture = build_python_fixture(disposable)
    preview = _preview()
    _, candidates = _write_transaction_inputs(fixture.root, preview)
    context = _context(
        transaction, fixture.root, disposable.root, preview, candidates=candidates
    )
    _stage_and_backup(transaction, context, candidates)
    transaction.promote(context)
    before = snapshot_paths((context.workspace, context.backup_root))

    with pytest.raises(transaction.AuthorizationError, match="registered"):
        transaction.cleanup(
            context.journal_path,
            workspace=context.workspace,
            target=context.target,
            authorization=replace(context.authorization),
        )

    assert snapshot_paths((context.workspace, context.backup_root)) == before


def test_fixture_authorization_registry_rejects_reused_identity_after_capability_dies(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    transaction = _transaction()
    first_parent = tmp_path / "first"
    first_parent.mkdir()
    first_disposable = create_disposable_root(first_parent)
    first_fixture = build_python_fixture(first_disposable)
    preview = _preview()
    first_workspace = _workspace(first_disposable.root, first_fixture.root)
    first_authorization = _fixture_authorization(
        transaction,
        first_fixture.root,
        first_disposable.root,
        first_workspace,
        preview,
    )
    stale_identity = id(first_authorization)
    first_reference = weakref.ref(first_authorization)
    del first_authorization
    gc.collect()
    assert first_reference() is None

    second_parent = tmp_path / "second"
    second_parent.mkdir()
    second_disposable = create_disposable_root(second_parent)
    second_fixture = build_python_fixture(second_disposable)
    second_workspace = _workspace(second_disposable.root, second_fixture.root)
    second_authorization = _fixture_authorization(
        transaction,
        second_fixture.root,
        second_disposable.root,
        second_workspace,
        preview,
    )
    forged = replace(second_authorization)
    monkeypatch.setattr(transaction, "id", lambda _value: stale_identity, raising=False)

    with pytest.raises(transaction.AuthorizationError, match="registered"):
        transaction._validate_registered_authorization(forged)


def test_owner_authorization_registry_rejects_reused_identity_after_capability_dies(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    transaction = _transaction()
    disposable = create_disposable_root(tmp_path)
    fixture = build_python_fixture(disposable)
    preview = _preview()
    workspace = _workspace(disposable.root, fixture.root)
    backup = disposable.root / "owner-backup"
    authorization = _owner_authorization(
        transaction, fixture.root, workspace, preview, backup
    )
    stale_identity = id(authorization)
    authorization_reference = weakref.ref(authorization)
    forged = replace(authorization)
    del authorization
    gc.collect()
    assert authorization_reference() is None
    monkeypatch.setattr(transaction, "id", lambda _value: stale_identity, raising=False)

    with pytest.raises(transaction.AuthorizationError, match="registered"):
        transaction._validate_registered_authorization(forged)


@pytest.mark.parametrize(
    "tamper",
    (
        lambda item: item["preimage"].update({"sha256": "not-a-hash"}),
        lambda item: item["preimage"].update({"size": -1}),
        lambda item: item["preimage"].update({"portable_mode": 0o1000}),
        lambda item: item["candidate"].update({"sha256": "A" * 64}),
        lambda item: item["candidate"].update({"size": True}),
        lambda item: item.update({"operation": "execute"}),
        lambda item: item["backup"].update({"sha256": "d" * 64}),
    ),
)
def test_recovery_rejects_malformed_nested_operation_records(
    tmp_path: Path, tamper
) -> None:
    transaction = _transaction()
    disposable = create_disposable_root(tmp_path)
    fixture = build_python_fixture(disposable)
    preview = _preview()
    _, candidates = _write_transaction_inputs(fixture.root, preview)
    context = _context(
        transaction, fixture.root, disposable.root, preview, candidates=candidates
    )
    _stage_and_backup(transaction, context, candidates)
    payload = _journal(context)
    tamper(payload["operations"][0])
    Path(context.journal_path).write_text(
        json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    before = snapshot_paths((fixture.root, context.workspace, context.backup_root))

    with pytest.raises(transaction.RecoveryRequiredError, match="journal"):
        transaction.recover(
            context.journal_path,
            action="rollback",
            workspace=context.workspace,
            target=context.target,
            authorization=context.authorization,
        )

    assert snapshot_paths((fixture.root, context.workspace, context.backup_root)) == before


def test_successful_promotion_uses_atomic_replace_per_path_and_preserves_unrelated_bytes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    transaction = _transaction()
    disposable = create_disposable_root(tmp_path)
    fixture = build_node_express_fixture(disposable)
    preview = _preview()
    proposal, candidates = _write_transaction_inputs(fixture.root, preview)
    unrelated = fixture.root / "host-owned/windows-notes.txt"
    protected_before = snapshot_paths((unrelated, proposal))
    context = _context(transaction, fixture.root, disposable.root, preview, candidates=candidates)
    _stage_and_backup(transaction, context, candidates)
    calls: list[tuple[Path, Path]] = []
    real_replace = transaction.os.replace

    def tracked_replace(source, destination) -> None:
        calls.append((Path(source), Path(destination)))
        real_replace(source, destination)

    monkeypatch.setattr(transaction.os, "replace", tracked_replace)
    result = transaction.promote(context)

    destinations = [destination.relative_to(fixture.root).as_posix() for _, destination in calls]
    assert destinations == list(candidates)
    assert all(source.parent == destination.parent for source, destination in calls)
    assert all(not source.exists() for source, _ in calls)
    assert result.exit_code == 0
    assert (fixture.root / "host-owned/replace.txt").read_bytes() == candidates["host-owned/replace.txt"]
    assert (fixture.root / "spec-driven-development/created.txt").read_bytes() == candidates["spec-driven-development/created.txt"]
    assert (fixture.root / "spec-driven-development/ledger/fleet.db").read_bytes() == candidates["spec-driven-development/ledger/fleet.db"]
    assert snapshot_paths((unrelated, proposal)) == protected_before
    assert _journal(context)["state"] == "committed"


@pytest.mark.parametrize(
    "fail_at",
    ("before-first-promotion", "after-replace", "after-create", "after-runtime-initialize"),
)
def test_representative_operation_failures_trigger_verified_reverse_rollback(
    tmp_path: Path, fail_at: str
) -> None:
    transaction = _transaction()
    disposable = create_disposable_root(tmp_path, name=f"fixtures-{fail_at}")
    fixture = build_python_fixture(disposable)
    preview = _preview()
    proposal, candidates = _write_transaction_inputs(fixture.root, preview)
    paths = (
        fixture.root / "host-owned/replace.txt",
        fixture.root / "spec-driven-development/created.txt",
        fixture.root / "spec-driven-development/ledger/fleet.db",
        proposal,
    )
    before = snapshot_paths(paths)
    context = _context(transaction, fixture.root, disposable.root, preview, candidates=candidates)
    _stage_and_backup(transaction, context, candidates)

    result = transaction.promote(context, injector=_injector(transaction, fail_at))

    assert result.exit_code == 1
    assert result.status == "rolled-back"
    assert snapshot_paths(paths) == before
    assert _journal(context)["state"] == "rolled-back"


def test_verified_rollback_restores_exact_bytes_newlines_existence_and_mode(tmp_path: Path) -> None:
    transaction = _transaction()
    disposable = create_disposable_root(tmp_path)
    fixture = build_node_express_fixture(disposable)
    before_bytes = b"first\r\nsecond\r\n"
    preview = _preview(replacement_before=before_bytes)
    proposal, candidates = _write_transaction_inputs(
        fixture.root, preview, replacement_before=before_bytes
    )
    replacement = fixture.root / "host-owned/replace.txt"
    if os.name != "nt":
        replacement.chmod(0o604)
    before = snapshot_paths((
        replacement,
        fixture.root / "spec-driven-development/created.txt",
        fixture.root / "spec-driven-development/ledger/fleet.db",
        proposal,
    ))
    context = _context(transaction, fixture.root, disposable.root, preview, candidates=candidates)
    _stage_and_backup(transaction, context, candidates)
    transaction.promote(context)

    result = transaction.rollback(context)

    assert result.exit_code == 1
    assert result.verified is True
    assert replacement.read_bytes() == before_bytes
    assert b"\r\n" in replacement.read_bytes()
    assert snapshot_paths((
        replacement,
        fixture.root / "spec-driven-development/created.txt",
        fixture.root / "spec-driven-development/ledger/fleet.db",
        proposal,
    )) == before


@pytest.mark.parametrize("failure", ("rollback-replace", "rollback-remove", "open-handle"))
def test_rollback_or_open_handle_failure_returns_exit_three_and_retains_recovery(
    tmp_path: Path, failure: str
) -> None:
    transaction = _transaction()
    disposable = create_disposable_root(tmp_path, name=f"fixtures-{failure}")
    fixture = build_python_fixture(disposable)
    preview = _preview()
    _, candidates = _write_transaction_inputs(fixture.root, preview)
    context = _context(transaction, fixture.root, disposable.root, preview, candidates=candidates)
    _stage_and_backup(transaction, context, candidates)
    transaction.promote(context)

    result = transaction.rollback(context, injector=_injector(transaction, failure))

    assert result.exit_code == 3
    assert result.status == "recovery-required"
    assert result.recovery_command == RECOVERY_COMMAND
    assert "recovery" in result.message.lower()
    assert Path(context.journal_path).exists()
    assert Path(context.stage_root).exists()
    assert Path(context.backup_root).exists()
    assert _journal(context)["state"] == "recovery-required"
    with pytest.raises(transaction.RecoveryRequiredError):
        transaction.preflight(
            preview,
            context.authorization,
            fixture.root,
            context.workspace,
            target_head=HEAD,
            candidate_bytes=candidates,
            reviewed_proposal=fixture.root / ".sdd-proposal",
        )


def test_startup_recovery_resolves_unknown_operation_from_preimage_or_candidate_hash(
    tmp_path: Path
) -> None:
    transaction = _transaction()
    disposable = create_disposable_root(tmp_path)
    fixture = build_node_express_fixture(disposable)
    preview = _preview()
    proposal, candidates = _write_transaction_inputs(fixture.root, preview)
    paths = (
        fixture.root / "host-owned/replace.txt",
        fixture.root / "spec-driven-development/created.txt",
        fixture.root / "spec-driven-development/ledger/fleet.db",
        proposal,
    )
    original = snapshot_paths(paths)
    context = _context(transaction, fixture.root, disposable.root, preview, candidates=candidates)
    _stage_and_backup(transaction, context, candidates)
    with pytest.raises(transaction.InjectedInterruption):
        transaction.promote(
            context,
            injector=_injector(transaction, "replace:applied:after-flush"),
        )

    inspection = transaction.inspect_recovery(
        context.journal_path,
        workspace=context.workspace,
        target=context.target,
        authorization=context.authorization,
    )
    assert inspection.operation_states["host-owned/replace.txt"] in {"preimage", "candidate"}
    assert inspection.operation_states["spec-driven-development/created.txt"] in {"absent", "candidate"}
    result = transaction.recover(
        context.journal_path,
        action="rollback",
        workspace=context.workspace,
        target=context.target,
        authorization=context.authorization,
    )

    assert result.exit_code == 0
    assert result.verified is True
    assert snapshot_paths(paths) == original
    assert _journal(context)["state"] == "rolled-back"


def test_recovery_refuses_unknown_third_hash_and_retains_exit_three_evidence(tmp_path: Path) -> None:
    transaction = _transaction()
    disposable = create_disposable_root(tmp_path)
    fixture = build_python_fixture(disposable)
    preview = _preview()
    _, candidates = _write_transaction_inputs(fixture.root, preview)
    context = _context(transaction, fixture.root, disposable.root, preview, candidates=candidates)
    _stage_and_backup(transaction, context, candidates)
    with pytest.raises(transaction.InjectedInterruption):
        transaction.promote(context, injector=_injector(transaction, "replace:applied:after-flush"))
    (fixture.root / "host-owned/replace.txt").write_bytes(b"unknown third state\n")

    result = transaction.recover(
        context.journal_path,
        action="rollback",
        workspace=context.workspace,
        target=context.target,
        authorization=context.authorization,
    )

    assert result.exit_code == 3
    assert result.status == "recovery-required"
    assert Path(context.journal_path).exists()
    assert Path(context.stage_root).exists()
    assert Path(context.backup_root).exists()
    assert _journal(context)["state"] == "recovery-required"


def test_cleanup_only_removes_explicitly_eligible_committed_or_rolled_back_transaction(tmp_path: Path) -> None:
    transaction = _transaction()
    disposable = create_disposable_root(tmp_path)
    fixture = build_node_express_fixture(disposable)
    preview = _preview()
    _, candidates = _write_transaction_inputs(fixture.root, preview)
    context = _context(transaction, fixture.root, disposable.root, preview, candidates=candidates)
    _stage_and_backup(transaction, context, candidates)

    with pytest.raises(transaction.CleanupNotEligibleError):
        transaction.cleanup(
            context.journal_path,
            workspace=context.workspace,
            target=context.target,
            authorization=context.authorization,
        )
    assert Path(context.journal_path).exists()
    assert Path(context.backup_root).exists()

    transaction.promote(context)
    result = transaction.cleanup(
        context.journal_path,
        workspace=context.workspace,
        target=context.target,
        authorization=context.authorization,
    )

    assert result.exit_code == 0
    assert not Path(context.journal_path).exists()
    assert not Path(context.stage_root).exists()
    assert not Path(context.backup_root).exists()
    assert (fixture.root / "host-owned/replace.txt").read_bytes() == candidates["host-owned/replace.txt"]


def test_cleanup_revalidates_evidence_tree_immediately_before_deletion(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    transaction = _transaction()
    disposable = create_disposable_root(tmp_path)
    fixture = build_node_express_fixture(disposable)
    preview = _preview()
    _, candidates = _write_transaction_inputs(fixture.root, preview)
    context = _context(transaction, fixture.root, disposable.root, preview, candidates=candidates)
    _stage_and_backup(transaction, context, candidates)
    transaction.promote(context)
    real_evidence_deletion_path = transaction._evidence_deletion_path

    def substitute_before_cleanup(workspace: Path, path: Path) -> Path:
        if Path(path) == context.stage_root:
            raise transaction.TransactionError("transaction evidence is linked or reparsed")
        return real_evidence_deletion_path(workspace, path)

    monkeypatch.setattr(transaction, "_evidence_deletion_path", substitute_before_cleanup)

    with pytest.raises(transaction.TransactionError, match="linked|reparse"):
        transaction.cleanup(
            context.journal_path,
            workspace=context.workspace,
            target=context.target,
            authorization=context.authorization,
        )

    assert Path(context.stage_root).exists()
    assert Path(context.backup_root).exists()
    assert Path(context.journal_path).exists()


def test_cleanup_rejects_ordinary_directory_replacement_of_trusted_backup_root(
    tmp_path: Path,
) -> None:
    transaction = _transaction()
    disposable = create_disposable_root(tmp_path)
    fixture = build_node_express_fixture(disposable)
    preview = _preview()
    _, candidates = _write_transaction_inputs(fixture.root, preview)
    context = _context(transaction, fixture.root, disposable.root, preview, candidates=candidates)
    _stage_and_backup(transaction, context, candidates)
    transaction.promote(context)
    original_backup = context.backup_root.with_name(f"{context.backup_root.name}-original")
    context.backup_root.rename(original_backup)
    context.backup_root.mkdir()
    protected = context.backup_root / "protected.txt"
    protected.write_bytes(b"replacement backup bytes\n")

    with pytest.raises(transaction.TransactionError, match="journal|filesystem identity"):
        transaction.cleanup(
            context.journal_path,
            workspace=context.workspace,
            target=context.target,
            authorization=context.authorization,
        )

    assert protected.read_bytes() == b"replacement backup bytes\n"
    assert original_backup.is_dir()
    assert context.journal_path.is_file()


def test_cleanup_rejects_backup_root_replacement_at_deletion_boundary(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    transaction = _transaction()
    disposable = create_disposable_root(tmp_path)
    fixture = build_node_express_fixture(disposable)
    preview = _preview()
    _, candidates = _write_transaction_inputs(fixture.root, preview)
    context = _context(transaction, fixture.root, disposable.root, preview, candidates=candidates)
    _stage_and_backup(transaction, context, candidates)
    transaction.promote(context)
    original_backup = context.backup_root.with_name(f"{context.backup_root.name}-original")
    protected = context.backup_root / "protected.txt"
    real_evidence_deletion_path = transaction._evidence_deletion_path

    def substitute_at_deletion_boundary(workspace: Path, path: Path) -> Path:
        if Path(path) == context.backup_root:
            context.backup_root.rename(original_backup)
            context.backup_root.mkdir()
            protected.write_bytes(b"replacement backup bytes\n")
        return real_evidence_deletion_path(workspace, path)

    monkeypatch.setattr(transaction, "_evidence_deletion_path", substitute_at_deletion_boundary)

    with pytest.raises(transaction.TransactionError, match="filesystem identity"):
        transaction.cleanup(
            context.journal_path,
            workspace=context.workspace,
            target=context.target,
            authorization=context.authorization,
        )

    assert protected.read_bytes() == b"replacement backup bytes\n"
    assert original_backup.is_dir()
    assert context.journal_path.is_file()


def test_restart_recovery_rejects_copied_journal_in_replaced_workspace(
    tmp_path: Path,
) -> None:
    transaction = _transaction()
    disposable = create_disposable_root(tmp_path)
    fixture = build_node_express_fixture(disposable)
    preview = _preview()
    _, candidates = _write_transaction_inputs(fixture.root, preview)
    context = _context(transaction, fixture.root, disposable.root, preview, candidates=candidates)
    _stage_and_backup(transaction, context, candidates)
    journal_bytes = context.journal_path.read_bytes()
    lock_bytes = context.lock_path.read_bytes()
    original_workspace = context.workspace.with_name(f"{context.workspace.name}-original")
    context.workspace.rename(original_workspace)
    context.workspace.mkdir()
    copied_journal = json.loads(journal_bytes)
    copied_journal["workspace_identity"] = transaction._identity_json(
        transaction._filesystem_identity(context.workspace)
    )
    copied_journal_bytes = (
        json.dumps(copied_journal, sort_keys=True, separators=(",", ":")) + "\n"
    ).encode("utf-8")
    context.journal_path.write_bytes(copied_journal_bytes)
    context.lock_path.write_bytes(lock_bytes)

    with pytest.raises(transaction.TransactionError, match="journal|authorization"):
        transaction.startup_recover(
            context.journal_path,
            action="rollback",
            workspace=context.workspace,
            target=context.target,
            authorization=context.authorization,
        )

    assert original_workspace.is_dir()
    assert context.journal_path.read_bytes() == copied_journal_bytes


def test_cleanup_rejects_recovery_required_and_never_silently_deletes_evidence(tmp_path: Path) -> None:
    transaction = _transaction()
    disposable = create_disposable_root(tmp_path)
    fixture = build_python_fixture(disposable)
    preview = _preview()
    _, candidates = _write_transaction_inputs(fixture.root, preview)
    context = _context(transaction, fixture.root, disposable.root, preview, candidates=candidates)
    _stage_and_backup(transaction, context, candidates)
    transaction.promote(context)
    transaction.rollback(context, injector=_injector(transaction, "rollback-replace"))
    evidence_before = snapshot_paths((context.journal_path, context.stage_root, context.backup_root))

    with pytest.raises(transaction.CleanupNotEligibleError):
        transaction.cleanup(
            context.journal_path,
            workspace=context.workspace,
            target=context.target,
            authorization=context.authorization,
        )

    assert snapshot_paths((context.journal_path, context.stage_root, context.backup_root)) == evidence_before


def test_active_transaction_lock_blocks_concurrent_preflight_and_stale_lock_is_recovered_explicitly(
    tmp_path: Path
) -> None:
    transaction = _transaction()
    disposable = create_disposable_root(tmp_path)
    fixture = build_node_express_fixture(disposable)
    preview = _preview()
    _, candidates = _write_transaction_inputs(fixture.root, preview)
    workspace = _workspace(disposable.root, fixture.root)
    authorization = _fixture_authorization(
        transaction, fixture.root, disposable.root, workspace, preview
    )
    first = _context(
        transaction,
        fixture.root,
        disposable.root,
        preview,
        authorization=authorization,
        candidates=candidates,
        workspace=workspace,
    )

    with pytest.raises(transaction.TransactionLockedError):
        transaction.preflight(
            preview,
            authorization,
            fixture.root,
            workspace,
            target_head=HEAD,
            candidate_bytes=candidates,
            reviewed_proposal=fixture.root / ".sdd-proposal",
        )

    Path(first.lock_path).write_text(
        json.dumps({"schema_version": "1", "transaction_id": first.transaction_id, "pid": 99999999}) + "\n",
        encoding="utf-8",
    )
    with pytest.raises(transaction.RecoveryRequiredError):
        transaction.preflight(
            preview,
            authorization,
            fixture.root,
            workspace,
            target_head=HEAD,
            candidate_bytes=candidates,
            reviewed_proposal=fixture.root / ".sdd-proposal",
        )
    assert Path(first.journal_path).exists()


def test_candidate_hash_drift_after_preflight_fails_before_promotion_and_preserves_proposal(
    tmp_path: Path
) -> None:
    transaction = _transaction()
    disposable = create_disposable_root(tmp_path)
    fixture = build_python_fixture(disposable)
    preview = _preview()
    proposal, candidates = _write_transaction_inputs(fixture.root, preview)
    context = _context(transaction, fixture.root, disposable.root, preview, candidates=candidates)
    before = snapshot_paths((fixture.root, proposal))

    def stale_materializer(stage_root: Path, operation) -> None:
        destination = stage_root / operation.destination
        destination.parent.mkdir(parents=True, exist_ok=True)
        data = candidates[operation.destination]
        if operation.destination.endswith("replace.txt"):
            data = b"stale candidate bytes\n"
        destination.write_bytes(data)

    with pytest.raises(transaction.StagingError, match="hash"):
        transaction.stage_candidate(
            context,
            stale_materializer,
            lambda *_args: SimpleNamespace(exit_code=0),
        )

    assert snapshot_paths((fixture.root, proposal)) == before
    assert list(Path(context.backup_root).iterdir()) == []


def test_transaction_module_is_stdlib_only_and_has_no_shell_or_real_host_escape() -> None:
    transaction = _transaction()
    source = Path(transaction.__file__).read_text(encoding="utf-8")

    forbidden_imports = (
        "import requests",
        "from requests",
        "import click",
        "from click",
        "import rich",
        "from rich",
    )
    assert not any(item in source for item in forbidden_imports)
    assert "shell=True" not in source
    assert "tempfile.gettempdir" not in source
    assert "Path.home()" not in source
    assert f'/{SENTINEL_NAME}' not in source
