"""RED-6 transactional apply, rollback, recovery, and cleanup contract.

Covers R-021 through R-024, R-036, R-044 and V-22, V-24, V-26,
V-28 through V-33, and V-53.  Every mutation-capable test is confined to a
positively identified disposable root below ``tmp_path``.  Owner receipts are
constructed for local fixture repositories only; no real host is inspected or
mutated.
"""

from __future__ import annotations

import hashlib
import importlib
import json
import os
import stat
import sys
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


def _fixture_authorization(transaction, target: Path, disposable_root: Path, preview: Preview):
    return transaction.authorize_verified_fixture(
        target=target,
        fixture_root=disposable_root,
        preview_hash=preview_hash(preview),
        target_head=HEAD,
        backup_location=str(disposable_root / "fixture-backup"),
        recovery_command=RECOVERY_COMMAND,
    )


def _owner_receipt_payload(transaction, target: Path, preview: Preview, backup: Path) -> dict[str, str]:
    return {
        "schema_version": "1",
        "kind": "owner-receipt",
        "target_fingerprint": transaction.target_fingerprint(target),
        "target_head": HEAD,
        "preview_hash": preview_hash(preview),
        "backup_location": str(backup.resolve()),
        "recovery_command": RECOVERY_COMMAND,
        "approved_by": "Fixture Owner",
        "approved_at": "2026-07-12T12:00:00Z",
    }


def _owner_authorization(transaction, target: Path, preview: Preview, backup: Path):
    receipt = target.parent / "fixture-owner-approval.json"
    receipt.write_text(
        json.dumps(
            _owner_receipt_payload(transaction, target, preview, backup),
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
    authorization = authorization or _fixture_authorization(
        transaction, target, disposable_root, preview
    )
    workspace = workspace or _workspace(disposable_root, target)
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
        "target_head",
        "preview_hash",
        "backup_location",
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
    authorization = _owner_authorization(transaction, fixture.root, preview, backup)
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
    backup = disposable.root / "owner-backup"
    authorization = _owner_authorization(transaction, fixture.root, preview, backup)

    context = _context(
        transaction,
        fixture.root,
        disposable.root,
        preview,
        authorization=authorization,
        candidates=candidates,
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
            preview_hash=preview_hash(preview),
            target_head=HEAD,
            backup_location=str(disposable.root / "backup"),
            recovery_command=RECOVERY_COMMAND,
        )

    assert snapshot_paths((targets[target_case], fixture.root)) == before


def test_verified_fixture_authorization_is_in_memory_only_and_not_owner_deserializable(tmp_path: Path) -> None:
    transaction = _transaction()
    disposable = create_disposable_root(tmp_path)
    fixture = build_python_fixture(disposable)
    preview = _preview()
    authorization = _fixture_authorization(transaction, fixture.root, disposable.root, preview)
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
    authorization = _fixture_authorization(transaction, fixture.root, disposable.root, preview)
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
    assert not Path(context.backup_root).exists()


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
    assert not Path(context.backup_root).exists()
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
        transaction, fixture.root, disposable.root, preview
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
    recovered = transaction.startup_recover(context.journal_path, action="rollback")
    assert recovered.exit_code == 0
    assert snapshot_paths((fixture.root / "host-owned/replace.txt", fixture.root / "spec-driven-development/created.txt", proposal)) == original
    assert _journal(context)["state"] == "rolled-back"


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

    inspection = transaction.inspect_recovery(context.journal_path)
    assert inspection.operation_states["host-owned/replace.txt"] in {"preimage", "candidate"}
    assert inspection.operation_states["spec-driven-development/created.txt"] in {"absent", "candidate"}
    result = transaction.recover(context.journal_path, action="rollback")

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

    result = transaction.recover(context.journal_path, action="rollback")

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
        transaction.cleanup(context.journal_path)
    assert Path(context.journal_path).exists()
    assert Path(context.backup_root).exists()

    transaction.promote(context)
    result = transaction.cleanup(context.journal_path)

    assert result.exit_code == 0
    assert not Path(context.journal_path).exists()
    assert not Path(context.stage_root).exists()
    assert not Path(context.backup_root).exists()
    assert (fixture.root / "host-owned/replace.txt").read_bytes() == candidates["host-owned/replace.txt"]


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
        transaction.cleanup(context.journal_path)

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
    authorization = _fixture_authorization(transaction, fixture.root, disposable.root, preview)
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
    assert not Path(context.backup_root).exists()


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
