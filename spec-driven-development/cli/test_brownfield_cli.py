"""RED-7 canonical brownfield compatibility and CLI contract for SDD-058.

These tests deliberately exercise only parser/adapter boundaries and disposable
paths.  They never create or mutate a real host.  T-058-018 supplies the missing
``brownfield_compat`` service and replaces the unsafe brownfield dispatcher.
"""

from __future__ import annotations

import dataclasses
import hashlib
import importlib
import inspect
import io
import json
import os
import sys
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from types import SimpleNamespace

import pytest

CLI_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(CLI_DIR))

import bootstrap  # noqa: E402
import brownfield_manifest  # noqa: E402
import brownfield_transaction  # noqa: E402
from brownfield_test_fixtures import (  # noqa: E402
    build_python_fixture,
    create_disposable_root,
)


ACTIONS = (
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
REQUEST_FIELDS = (
    "action",
    "target",
    "proposal_root",
    "identity_path",
    "migration",
    "run_quality",
    "preview_approval",
    "owner_approval_path",
    "transaction_workspace",
)
RESULT_FIELDS = (
    "exit_code",
    "status",
    "message",
    "preview",
    "receipt_path",
    "readiness",
    "recovery_command",
)


def _compat():
    """Import the production surface that T-058-018 must implement."""
    return importlib.import_module("brownfield_compat")


def _capture_main(argv: list[str]) -> tuple[int, str, str]:
    stdout = io.StringIO()
    stderr = io.StringIO()
    with redirect_stdout(stdout), redirect_stderr(stderr):
        exit_code = bootstrap.main(argv)
    return exit_code, stdout.getvalue(), stderr.getvalue()


def _legacy_args(*, target: Path, draft_only: bool = False, apply: bool = False):
    return SimpleNamespace(
        command="brownfield",
        target_path=str(target),
        owner=None,
        draft_only=draft_only,
        apply=apply,
    )


def _result(compat, exit_code: int, message: str, *, status: str = "ok", recovery: str | None = None):
    return compat.BrownfieldResult(
        exit_code=exit_code,
        status=status,
        message=message,
        preview=None,
        receipt_path=None,
        readiness=None,
        recovery_command=recovery,
    )


def _request(compat, action: str, target: Path, **changes):
    values = {
        "action": action,
        "target": target,
        "proposal_root": target / ".sdd-proposal",
        "identity_path": None,
        "migration": None,
        "run_quality": False,
        "preview_approval": None,
        "owner_approval_path": None,
        "transaction_workspace": target.parent / f"transaction-{action}",
    }
    values.update(changes)
    return compat.BrownfieldRequest(**values)


def _confirm_drafted_identity(path: Path) -> None:
    payload = json.loads(path.read_text(encoding="utf-8"))
    values = {
        "project_name": "fixture-python-library",
        "repo_url": "https://example.invalid/fixture-python-library.git",
        "default_branch": "trunk",
        "owner": "Fixture Owner",
        "team": "Fixture Team",
        "mission": "Maintain a deterministic fixture library.",
        "article_xi_cutover": "2026-07-13",
        "stack": ["python"],
        "quality_commands": {
            name: {
                "state": "not-configured",
                "argv": [],
                "cwd": None,
                "timeout_seconds": None,
                "environment_policy": "minimal",
                "network_policy": "deny",
            }
            for name in ("test", "lint", "typecheck", "build")
        },
        "branch_convention": "trunk-based",
        "commit_convention": "type: short description",
        "source_documents": ["README.md"],
        "approval_boundaries": ["owner approval before apply"],
        "worktree_profile": False,
    }
    for name, value in values.items():
        payload["fields"][name].update({
            "value": value,
            "classification": "human",
            "evidence_paths": [],
            "ambiguity": "none",
            "confidence": None,
            "confirmed_by": "Fixture Owner",
            "confirmed_at": "2026-07-13T12:00:00Z",
        })
    path.write_text(
        json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def test_brownfield_contract_exposes_frozen_request_and_result_dataclasses() -> None:
    compat = _compat()

    assert dataclasses.is_dataclass(compat.BrownfieldRequest)
    assert dataclasses.is_dataclass(compat.BrownfieldResult)
    assert tuple(field.name for field in dataclasses.fields(compat.BrownfieldRequest)) == REQUEST_FIELDS
    assert tuple(field.name for field in dataclasses.fields(compat.BrownfieldResult)) == RESULT_FIELDS
    assert compat.SUPPORTED_ACTIONS == ACTIONS
    assert compat.BrownfieldRequest.__dataclass_params__.frozen
    assert compat.BrownfieldResult.__dataclass_params__.frozen
    assert tuple(inspect.signature(compat.execute).parameters) == ("request", "fixture_authorization")
    assert inspect.signature(compat.execute).parameters["fixture_authorization"].kind is inspect.Parameter.KEYWORD_ONLY


@pytest.mark.parametrize("action", ACTIONS)
def test_parse_args_canonical_action_maps_all_request_inputs(action: str, tmp_path: Path) -> None:
    target = tmp_path / "host"
    proposal = tmp_path / "reviewed-proposal"
    identity = tmp_path / "identity.json"
    migration = tmp_path / "migration.json"
    owner_receipt = tmp_path / "owner-approval.json"
    workspace = tmp_path / "transaction-workspace"
    argv = [
        "brownfield",
        str(target),
        "--action",
        action,
        "--proposal-root",
        str(proposal),
        "--identity",
        str(identity),
        "--migration",
        str(migration),
        "--preview-hash",
        "a" * 64,
        "--owner-approval",
        str(owner_receipt),
        "--transaction-workspace",
        str(workspace),
    ]
    if action == "host-doctor":
        argv.append("--run-quality")

    args = bootstrap.parse_args(argv)
    compat = _compat()
    request = compat.request_from_args(args)

    assert request.action == action
    assert request.target == target
    assert request.proposal_root == proposal
    assert request.identity_path == identity
    assert request.migration == migration
    assert request.run_quality is (action == "host-doctor")
    assert request.preview_approval == "a" * 64
    assert request.owner_approval_path == owner_receipt
    assert request.transaction_workspace == workspace


@pytest.mark.parametrize(
    ("draft_only", "apply", "expected_action", "expected_proposal_use"),
    (
        (False, False, "draft", False),
        (True, False, "draft", False),
        (False, True, "preview", True),
    ),
)
def test_adapt_legacy_brownfield_maps_only_safe_non_overwriting_behavior(
    tmp_path: Path,
    draft_only: bool,
    apply: bool,
    expected_action: str,
    expected_proposal_use: bool,
) -> None:
    compat = _compat()
    request = compat.adapt_legacy_brownfield(
        _legacy_args(target=tmp_path / "host", draft_only=draft_only, apply=apply)
    )

    assert request.action == expected_action
    assert request.target == tmp_path / "host"
    assert (request.proposal_root is not None) is expected_proposal_use
    assert request.preview_approval is None
    assert request.owner_approval_path is None


def test_adapt_legacy_apply_never_requests_generation_refresh_or_broad_copy(tmp_path: Path) -> None:
    compat = _compat()
    request = compat.adapt_legacy_brownfield(
        _legacy_args(target=tmp_path / "host", apply=True)
    )

    assert request.action == "preview"
    serialized = repr(request).casefold()
    assert "refresh" not in serialized
    assert "archaeology" not in serialized
    assert "broad" not in serialized
    assert "force" not in serialized


def test_main_apply_routes_once_through_canonical_service_without_old_helpers(monkeypatch, tmp_path: Path) -> None:
    compat = _compat()
    target = tmp_path / "host"
    owner_receipt = tmp_path / "owner.json"
    calls = []

    def unsafe(*_args, **_kwargs):
        pytest.fail("legacy archaeology/proposal/broad-copy helper was reachable")

    for name in (
        "create_archaeology_report",
        "draft_constitution_proposal",
        "apply_brownfield_framework",
        "copy_directory",
    ):
        monkeypatch.setattr(bootstrap, name, unsafe)

    def execute(request, *, fixture_authorization=None):
        calls.append((request, fixture_authorization))
        return _result(compat, 0, "preview ready", status="preview")

    monkeypatch.setattr(compat, "execute", execute)
    exit_code, stdout, stderr = _capture_main([
        "brownfield",
        str(target),
        "--action",
        "apply",
        "--preview-hash",
        "b" * 64,
        "--owner-approval",
        str(owner_receipt),
    ])

    assert exit_code == 0
    assert stdout == "preview ready\n"
    assert stderr == ""
    assert len(calls) == 1
    request, fixture_authorization = calls[0]
    assert request.action == "apply"
    assert request.owner_approval_path == owner_receipt
    assert fixture_authorization is None


def test_main_explicit_migrate_routes_to_canonical_migration_action(monkeypatch, tmp_path: Path) -> None:
    compat = _compat()
    observed = []

    def execute(request, *, fixture_authorization=None):
        observed.append((request, fixture_authorization))
        return _result(compat, 0, "migration preview ready", status="preview")

    monkeypatch.setattr(compat, "execute", execute)
    exit_code, stdout, stderr = _capture_main([
        "brownfield", str(tmp_path / "host"), "--action", "migrate",
        "--migration", str(tmp_path / "migration.json"),
    ])

    assert (exit_code, stdout, stderr) == (0, "migration preview ready\n", "")
    assert len(observed) == 1
    assert observed[0][0].action == "migrate"
    assert observed[0][0].migration == tmp_path / "migration.json"
    assert observed[0][1] is None


@pytest.mark.parametrize(
    ("result", "expected_exit", "expected_stdout", "expected_stderr"),
    (
        ((0, "preview ready", "preview", None), 0, "preview ready\n", ""),
        ((1, "identity is incomplete", "blocked", None), 1, "", "ERROR: identity is incomplete\n"),
        ((2, "invalid preview hash", "invalid", None), 2, "", "ERROR: invalid preview hash\n"),
        ((3, "recovery required", "recovery-required", "python recover.py"), 3, "", "ERROR: recovery required\nRecovery: python recover.py\n"),
    ),
)
def test_main_propagates_exact_result_exit_and_stream_contract(
    monkeypatch,
    tmp_path: Path,
    result,
    expected_exit: int,
    expected_stdout: str,
    expected_stderr: str,
) -> None:
    compat = _compat()
    exit_code, message, status, recovery = result
    monkeypatch.setattr(
        compat,
        "execute",
        lambda request, *, fixture_authorization=None: _result(
            compat, exit_code, message, status=status, recovery=recovery
        ),
    )

    actual = _capture_main([
        "brownfield", str(tmp_path / "host"), "--action", "preview"
    ])

    assert actual == (expected_exit, expected_stdout, expected_stderr)
    combined = (actual[1] + actual[2]).casefold()
    assert "traceback" not in combined
    if expected_exit:
        assert "installed" not in combined
        assert "readiness pass" not in combined
        assert "all checks passed" not in combined
        assert "framework health" not in combined


def test_main_unexpected_exception_is_redacted_actionable_and_never_overclaims(monkeypatch, tmp_path: Path) -> None:
    compat = _compat()
    secret = "cli-secret-canary-058"
    monkeypatch.setattr(
        compat,
        "execute",
        lambda request, *, fixture_authorization=None: (_ for _ in ()).throw(
            RuntimeError(f"internal failure containing {secret}")
        ),
    )

    exit_code, stdout, stderr = _capture_main([
        "brownfield", str(tmp_path / "host"), "--action", "preview"
    ])

    assert exit_code == 1
    assert stdout == ""
    assert stderr == "ERROR: Brownfield operation failed unexpectedly.\nRemediation: No mutation was claimed; inspect retained recovery evidence and retry.\n"
    assert secret not in stderr
    assert "traceback" not in stderr.casefold()
    assert "installed" not in stderr.casefold()
    assert "pass" not in stderr.casefold()


@pytest.mark.parametrize(
    "unsafe_option",
    (
        "--force",
        "--skip-conflicts",
        "--skip-backup",
        "--skip-recovery",
        "--warn-only",
        "--fixture-root",
        "--verified-fixture",
        "--fixture-authorization",
    ),
)
def test_parser_rejects_unsafe_bypass_and_fixture_options(unsafe_option: str, tmp_path: Path) -> None:
    with pytest.raises(SystemExit) as caught:
        bootstrap.parse_args([
            "brownfield", str(tmp_path / "host"), "--action", "apply", unsafe_option
        ])

    assert caught.value.code == 2


def test_environment_cannot_select_fixture_authorization(monkeypatch, tmp_path: Path) -> None:
    compat = _compat()
    for name in (
        "SDD_FIXTURE_ROOT",
        "SDD_VERIFIED_FIXTURE",
        "SDD_FIXTURE_AUTHORIZATION",
        "BROWNFIELD_FIXTURE_ROOT",
    ):
        monkeypatch.setenv(name, str(tmp_path / "forged-fixture"))

    args = bootstrap.parse_args([
        "brownfield", str(tmp_path / "host"), "--action", "preview"
    ])
    request = compat.request_from_args(args)

    assert tuple(field.name for field in dataclasses.fields(request)) == REQUEST_FIELDS
    assert "fixture" not in repr(request).casefold()
    assert not any("fixture" in name.casefold() for name in vars(args))


def test_verified_fixture_authorization_cannot_be_loaded_from_serialized_receipt(tmp_path: Path) -> None:
    receipt = tmp_path / "forged-fixture-receipt.json"
    receipt.write_text(
        json.dumps({
            "schema_version": "1",
            "kind": "verified-fixture",
            "target_fingerprint": "f" * 64,
            "target_head": "deadbeef",
            "preview_hash": "a" * 64,
            "backup_location": str(tmp_path / "backup"),
            "recovery_command": "python recover.py",
            "approved_by": "attacker",
            "approved_at": "2026-07-12T00:00:00Z",
        }),
        encoding="utf-8",
    )

    with pytest.raises(brownfield_transaction.AuthorizationError, match="only owner-receipt"):
        brownfield_transaction.load_owner_authorization(receipt)


@pytest.mark.parametrize(
    "argv",
    (
        ["brownfield", "host", "--action", "unknown"],
        ["brownfield", "host", "--action", "apply", "--preview-hash", "not-a-hash"],
        ["brownfield", "host", "--action", "host-doctor", "--run-quality", "--apply"],
        ["brownfield", "host", "--action", "recover", "--run-quality"],
    ),
)
def test_parser_rejects_malformed_or_incompatible_action_inputs(argv: list[str]) -> None:
    with pytest.raises(SystemExit) as caught:
        bootstrap.parse_args(argv)

    assert caught.value.code == 2


def test_shell_metacharacters_remain_data_and_never_reach_subprocess(monkeypatch, tmp_path: Path) -> None:
    compat = _compat()
    hostile = tmp_path / "identity;echo-INJECTION.json"
    observed = []

    monkeypatch.setattr(
        bootstrap.subprocess,
        "run",
        lambda *_args, **_kwargs: pytest.fail("CLI adapter executed host-provided input"),
    )

    def execute(request, *, fixture_authorization=None):
        observed.append(request)
        return _result(compat, 2, "identity input rejected", status="invalid")

    monkeypatch.setattr(compat, "execute", execute)
    exit_code, stdout, stderr = _capture_main([
        "brownfield", str(tmp_path / "host"), "--action", "preview",
        "--identity", str(hostile),
    ])

    assert exit_code == 2
    assert stdout == ""
    assert stderr == "ERROR: identity input rejected\n"
    assert observed[0].identity_path == hostile


def test_parse_args_preserves_greenfield_host_link_setup_and_framework_doctor() -> None:
    greenfield = bootstrap.parse_args([
        "greenfield", "python-library", "--project-name", "Host", "--owner", "Owner"
    ])
    host_link = bootstrap.parse_args(["host-link", "--target", "host"])
    setup = bootstrap.parse_args(["setup", "--skip-venv", "--skip-checks"])
    doctor = bootstrap.parse_args(["doctor", "--skip-tests", "--mode", "ci"])

    assert (greenfield.command, greenfield.archetype_name, greenfield.project_name) == (
        "greenfield", "python-library", "Host"
    )
    assert (host_link.command, host_link.apply, host_link.backup, host_link.force) == (
        "host-link", False, False, False
    )
    assert (setup.command, setup.skip_venv, setup.skip_checks) == ("setup", True, True)
    assert (doctor.command, doctor.skip_tests, doctor.mode) == ("doctor", True, "ci")


def test_brownfield_parser_does_not_change_process_environment(tmp_path: Path) -> None:
    before = dict(os.environ)
    bootstrap.parse_args([
        "brownfield", str(tmp_path / "host"), "--action", "preview"
    ])
    assert dict(os.environ) == before


def test_canonical_fixture_draft_apply_receipt_readiness_and_noop_rerun(tmp_path: Path) -> None:
    compat = _compat()
    disposable = create_disposable_root(tmp_path)
    fixture = build_python_fixture(disposable)
    authorization = compat.authorize_disposable_fixture(
        target=fixture.root,
        temporary_root=tmp_path,
    )

    draft_request = _request(compat, "draft", fixture.root)
    draft_preview = compat.execute(draft_request, fixture_authorization=authorization)
    assert draft_preview.exit_code == 0
    assert draft_preview.status == "preview"
    assert isinstance(draft_preview.preview, brownfield_manifest.Preview)
    assert not (fixture.root / ".sdd-proposal/baseline-manifest.json").exists()

    draft_hash = brownfield_manifest.preview_hash(draft_preview.preview)
    drafted = compat.execute(
        dataclasses.replace(draft_request, preview_approval=draft_hash),
        fixture_authorization=authorization,
    )
    proposal = fixture.root / ".sdd-proposal"
    assert drafted.exit_code == 0
    assert drafted.status == "drafted"
    assert (proposal / "archaeology.json").is_file()
    assert (proposal / "host-identity.json").is_file()
    assert (proposal / "baseline-manifest.json").is_file()
    assert (proposal / ".baseline/constitution/mission.md").is_file()
    draft_journal = draft_request.transaction_workspace / "transaction.json"
    assert json.loads(draft_journal.read_text(encoding="utf-8"))["state"] == "committed"
    assert json.loads(draft_journal.read_text(encoding="utf-8"))["reviewed_proposal"] == {
        "exists": False,
        "preview_hash": draft_hash,
    }

    _confirm_drafted_identity(proposal / "host-identity.json")
    reviewed = proposal / "constitution/mission.md"
    reviewed.write_bytes(b"# Mission\r\n\r\nFixture owner reviewed bytes.\r\n")
    reviewed_before = reviewed.read_bytes()

    preview_request = _request(compat, "preview", fixture.root)
    previewed = compat.execute(preview_request)
    assert previewed.exit_code == 0
    assert previewed.status == "preview"
    assert isinstance(previewed.preview, brownfield_manifest.Preview)
    receipt_item = next(
        item
        for item in previewed.preview.items
        if item.destination == "spec-driven-development/.adoption/receipt.json"
    )
    assert receipt_item.category == "create"
    assert receipt_item.after_sha256 is not None
    apply_hash = brownfield_manifest.preview_hash(previewed.preview)

    applied = compat.execute(
        dataclasses.replace(preview_request, action="apply", preview_approval=apply_hash),
        fixture_authorization=authorization,
    )
    assert applied.exit_code == 0
    assert applied.status == "installed"
    assert applied.receipt_path == fixture.root / "spec-driven-development/.adoption/receipt.json"
    assert applied.receipt_path.is_file()
    assert hashlib.sha256(applied.receipt_path.read_bytes()).hexdigest() == receipt_item.after_sha256
    assert applied.readiness.exit_code == 0
    assert reviewed.read_bytes() == reviewed_before

    transaction_journal = preview_request.transaction_workspace / "transaction.json"
    transaction_payload = json.loads(transaction_journal.read_text(encoding="utf-8"))
    assert transaction_payload["preview_hash"] == apply_hash
    assert tuple(item["destination"] for item in transaction_payload["operations"]) == tuple(
        item.destination
        for item in previewed.preview.items
        if item.category in {"create", "replace", "runtime-initialize"}
    )
    journal_before = transaction_journal.read_bytes()
    rerun = compat.execute(preview_request)
    assert rerun.exit_code == 0
    assert rerun.status == "no-op"
    assert transaction_journal.read_bytes() == journal_before
    assert not (fixture.root.parent / "transaction-preview-rerun").exists()


def test_apply_receipt_replace_failure_rolls_back_and_never_reports_readiness_success(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    compat = _compat()
    disposable = create_disposable_root(tmp_path)
    fixture = build_python_fixture(disposable)
    authorization = compat.authorize_disposable_fixture(
        target=fixture.root, temporary_root=tmp_path
    )
    draft = _request(compat, "draft", fixture.root)
    drafted_preview = compat.execute(draft, fixture_authorization=authorization)
    compat.execute(
        dataclasses.replace(
            draft,
            preview_approval=brownfield_manifest.preview_hash(drafted_preview.preview),
        ),
        fixture_authorization=authorization,
    )
    _confirm_drafted_identity(fixture.root / ".sdd-proposal/host-identity.json")
    request = _request(compat, "preview", fixture.root)
    previewed = compat.execute(request)
    receipt = fixture.root / "spec-driven-development/.adoption/receipt.json"
    real_replace = brownfield_transaction._ATOMIC_DESTINATION_REPLACE

    def fail_receipt(source, destination) -> None:
        if Path(destination) == receipt:
            raise OSError("fixture receipt failure")
        real_replace(source, destination)

    monkeypatch.setattr(
        brownfield_transaction, "_ATOMIC_DESTINATION_REPLACE", fail_receipt
    )
    result = compat.execute(
        dataclasses.replace(
            request,
            action="apply",
            preview_approval=brownfield_manifest.preview_hash(previewed.preview),
        ),
        fixture_authorization=authorization,
    )

    assert result.exit_code == 1
    assert result.status == "rolled-back"
    assert result.readiness is None
    assert "pass" not in result.message.casefold()
    assert not receipt.exists()


def test_host_doctor_quality_preserves_canonical_pre_execution_disclosure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    compat = _compat()
    identity = tmp_path / "host-identity.json"
    identity.write_text("{}\n", encoding="utf-8")
    loaded_identity = SimpleNamespace(fields={})
    disclosure = (
        "quality test: cwd=C:/fixture; argv=['python', '-m', 'pytest']; "
        "timeout=17s; environment=minimal; network=deny; filesystem and "
        "external side effects are outside rollback"
    )
    events: list[str] = []

    monkeypatch.setattr(
        compat.brownfield_identity,
        "load_identity",
        lambda path: loaded_identity,
    )

    def run_quality_checks(root, received_identity, disclosure_sink):
        assert root == tmp_path
        assert received_identity is loaded_identity
        disclosure_sink(disclosure)
        events.append("execute")
        return SimpleNamespace(exit_code=0)

    monkeypatch.setattr(
        compat.host_readiness,
        "run_quality_checks",
        run_quality_checks,
    )
    monkeypatch.setattr(
        compat.host_readiness,
        "format_readiness_summary",
        lambda report, *, installed: "host readiness PASS",
    )

    result = compat.execute(
        _request(
            compat,
            "host-doctor",
            tmp_path,
            identity_path=identity,
            run_quality=True,
        )
    )

    assert events == ["execute"]
    assert result.message.splitlines() == [disclosure, "host readiness PASS"]


def test_exactly_approved_refresh_and_migration_execute_through_transaction_engine(
    tmp_path: Path,
) -> None:
    compat = _compat()
    disposable = create_disposable_root(tmp_path)
    fixture = build_python_fixture(disposable)
    authorization = compat.authorize_disposable_fixture(
        target=fixture.root, temporary_root=tmp_path
    )
    draft = _request(compat, "draft", fixture.root)
    draft_preview = compat.execute(draft, fixture_authorization=authorization)
    compat.execute(
        dataclasses.replace(
            draft,
            preview_approval=brownfield_manifest.preview_hash(draft_preview.preview),
        ),
        fixture_authorization=authorization,
    )
    proposal = fixture.root / ".sdd-proposal"
    _confirm_drafted_identity(proposal / "host-identity.json")
    reviewed = proposal / "constitution/mission.md"
    reviewed_before = reviewed.read_bytes()

    refresh_request = _request(compat, "refresh", fixture.root)
    refresh_preview = compat.execute(refresh_request)
    assert isinstance(refresh_preview.preview, brownfield_manifest.Preview)
    refreshed = compat.execute(
        dataclasses.replace(
            refresh_request,
            preview_approval=brownfield_manifest.preview_hash(refresh_preview.preview),
        ),
        fixture_authorization=authorization,
    )
    assert refreshed.exit_code == 0
    assert refreshed.status == "refreshed"
    assert reviewed.read_bytes() == reviewed_before
    assert json.loads(
        (refresh_request.transaction_workspace / "transaction.json").read_text(encoding="utf-8")
    )["state"] == "committed"

    migration_request = _request(compat, "migrate", fixture.root)
    migration_preview = compat.execute(migration_request)
    assert isinstance(migration_preview.preview, brownfield_manifest.Preview)
    if migration_preview.status == "migration-plan":
        migrated = compat.execute(
            dataclasses.replace(
                migration_request,
                preview_approval=brownfield_manifest.preview_hash(migration_preview.preview),
            ),
            fixture_authorization=authorization,
        )
        assert migrated.exit_code == 0
        assert migrated.status == "migrated"
        assert migrated.receipt_path is not None and migrated.receipt_path.is_file()
    else:
        snapshot = tuple(fixture.root.rglob("*"))
        rerun = compat.execute(migration_request)
        assert rerun.status == "no-op"
        assert tuple(fixture.root.rglob("*")) == snapshot


def test_canonical_refresh_adoption_and_migration_return_exact_executable_previews(tmp_path: Path) -> None:
    compat = _compat()
    disposable = create_disposable_root(tmp_path)
    fixture = build_python_fixture(disposable)
    authorization = compat.authorize_disposable_fixture(
        target=fixture.root,
        temporary_root=tmp_path,
    )
    draft = _request(compat, "draft", fixture.root)
    preview = compat.execute(draft, fixture_authorization=authorization)
    compat.execute(
        dataclasses.replace(draft, preview_approval=brownfield_manifest.preview_hash(preview.preview)),
        fixture_authorization=authorization,
    )
    _confirm_drafted_identity(fixture.root / ".sdd-proposal/host-identity.json")

    refreshed = compat.execute(_request(compat, "refresh", fixture.root))
    assert refreshed.exit_code in {0, 1}
    assert refreshed.status == "refresh-plan"
    assert refreshed.preview.items
    assert isinstance(refreshed.preview, brownfield_manifest.Preview)

    migrated = compat.execute(_request(compat, "migrate", fixture.root))
    assert migrated.exit_code in {0, 1}
    assert migrated.status in {"migration-plan", "no-op"}
    if migrated.status == "migration-plan":
        assert isinstance(migrated.preview, brownfield_manifest.Preview)
    else:
        assert migrated.preview.mode == "migration"

    legacy = fixture.root / ".sdd-proposal"
    (legacy / "baseline-manifest.json").unlink()
    for snapshot in sorted((legacy / ".baseline").rglob("*"), reverse=True):
        snapshot.unlink() if snapshot.is_file() else snapshot.rmdir()
    (legacy / ".baseline").rmdir()
    adoption = compat.execute(_request(compat, "adopt-baseline", fixture.root))
    assert adoption.exit_code in {0, 1}
    assert adoption.status == "baseline-adoption-plan"
    assert isinstance(adoption.preview, brownfield_manifest.Preview)


def test_canonical_recover_and_cleanup_route_to_transaction_engine(monkeypatch, tmp_path: Path) -> None:
    compat = _compat()
    journal = tmp_path / "transaction.json"
    calls = []

    def recover(path, *, action):
        calls.append(("recover", path, action))
        return SimpleNamespace(exit_code=0, status="rolled-back", message="recovered", recovery_command="recover")

    def cleanup(path):
        calls.append(("cleanup", path))
        return SimpleNamespace(exit_code=0, status="cleaned", message="cleaned", recovery_command="recover")

    monkeypatch.setattr(brownfield_transaction, "recover", recover)
    monkeypatch.setattr(brownfield_transaction, "cleanup", cleanup)
    base = _request(
        compat,
        "recover",
        tmp_path / "host",
        transaction_workspace=journal,
    )

    assert compat.execute(base).status == "rolled-back"
    assert compat.execute(dataclasses.replace(base, action="cleanup")).status == "cleaned"
    assert calls == [("recover", journal, "rollback"), ("cleanup", journal)]
