"""RED-1 fixture isolation and verified-fixture authorization tests for SDD-058."""

from __future__ import annotations

import importlib
import hashlib
import json
import os
import shutil
import stat
import subprocess
import sys
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace

import pytest

CLI_DIR = Path(__file__).resolve().parent
FRAMEWORK_ROOT = CLI_DIR.parents[1]
if str(CLI_DIR) not in sys.path:
    sys.path.insert(0, str(CLI_DIR))

from brownfield_test_fixtures import (  # noqa: E402
    FailureInjector,
    InjectedFixtureFailure,
    build_node_express_fixture,
    build_python_fixture,
    copy_sentinel,
    create_disposable_root,
    make_link,
    sentinel_identifies,
    snapshot_git_status,
    snapshot_paths,
)

PROTECTED_PATHS = (
    FRAMEWORK_ROOT / "spec-driven-development" / "ledger" / "fleet.db",
    FRAMEWORK_ROOT / "spec-driven-development" / "exec" / "state.md",
    FRAMEWORK_ROOT / "spec-driven-development" / "exec" / "state.html",
    FRAMEWORK_ROOT / "spec-driven-development" / "exec" / "work-index.md",
    FRAMEWORK_ROOT / "spec-driven-development" / "specs" / "2026-07-12-brownfield-bootstrap-correctness",
)
SCENARIO_CELLS = (
    pytest.param("node", "windows", id="node-express-windows"),
    pytest.param("node", "posix", id="node-express-posix"),
    pytest.param("python", "windows", id="python-windows"),
    pytest.param("python", "posix", id="python-posix"),
)


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), *args], check=True, capture_output=True,
        text=True, encoding="utf-8",
    ).stdout.strip()


def _production_compat():
    """Import the intentionally absent production API only inside RED tests."""

    return importlib.import_module("brownfield_compat")


def _module(name: str):
    return importlib.import_module(name)


def _fixture(tmp_path: Path, stack: str):
    disposable = create_disposable_root(tmp_path)
    builder = build_node_express_fixture if stack == "node" else build_python_fixture
    return disposable, builder(disposable)


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _write_baseline(fixture, reviewed: bytes) -> Path:
    proposal = fixture.root / ".sdd-proposal"
    reviewed_path = proposal / "constitution/mission.md"
    reviewed_path.parent.mkdir(parents=True, exist_ok=True)
    reviewed_path.write_bytes(reviewed)
    snapshot = proposal / ".baseline/constitution/mission.md"
    snapshot.parent.mkdir(parents=True, exist_ok=True)
    snapshot.write_bytes(reviewed)
    manifest = {
        "schema_version": "1",
        "source_revision": fixture.head,
        "evidence_digest": "e" * 64,
        "bundle_version": "brownfield-core@1",
        "generated_at": "2026-07-12T00:00:00Z",
        "files": [{
            "path": "constitution/mission.md",
            "sha256": _sha(reviewed),
            "byte_length": len(reviewed),
            "baseline_path": ".baseline/constitution/mission.md",
            "renderer_id": "constitution",
            "renderer_version": "1",
            "evidence_dependencies": ["README.md"],
            "text_policy": "preserve",
        }],
    }
    (proposal / "baseline-manifest.json").write_text(
        json.dumps(manifest, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return proposal


def _one_file_preview(manifest, before: bytes | None, after: bytes):
    return manifest.Preview(
        "1",
        manifest.PREVIEW_CATEGORIES,
        (manifest.PreviewItem(
            category="create" if before is None else "replace",
            destination="spec-driven-development/managed.txt",
            reason="approved fixture mutation",
            ownership="managed",
            operation="copy",
            before_sha256=None if before is None else _sha(before),
            after_sha256=_sha(after),
            dependencies=(),
        ),),
    )


def _transaction_context(disposable, fixture, preview, candidate: bytes):
    transaction = _module("brownfield_transaction")
    manifest = _module("brownfield_manifest")
    workspace = disposable.root / "transaction-workspace"
    workspace.mkdir()
    backup = disposable.root / "backup"
    backup.mkdir()
    authorization = transaction.authorize_verified_fixture(
        target=fixture.root,
        fixture_root=disposable.root,
        workspace=workspace,
        preview_hash=manifest.preview_hash(preview),
        target_head=fixture.head,
        backup_location=str(backup),
        recovery_command="bootstrap brownfield recover --journal transaction.json --action rollback",
    )
    context = transaction.preflight(
        preview,
        authorization,
        fixture.root,
        workspace,
        target_head=fixture.head,
        candidate_bytes={"spec-driven-development/managed.txt": candidate},
        reviewed_proposal=fixture.root / ".sdd-proposal",
    )

    def materialize(stage_root: Path, operation) -> None:
        destination = stage_root / operation.destination
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(candidate)

    transaction.stage_candidate(
        context,
        materialize,
        lambda *_args: SimpleNamespace(exit_code=0),
    )
    transaction.backup(context)
    return transaction, context


def _bounded_mutation_snapshot(target: Path) -> dict[str, object]:
    """Snapshot only mutation markers; never recursively inspect an untrusted target."""

    markers = tuple(
        target / name
        for name in (".sdd-stage", ".sdd-backup", ".sdd-transaction.json")
    )
    return {
        "markers": snapshot_paths(markers),
        "protected": snapshot_paths(PROTECTED_PATHS),
        "checkout_status": snapshot_git_status(FRAMEWORK_ROOT),
    }


@pytest.fixture(scope="module", autouse=True)
def protected_checkout_snapshot():
    """Prove the full cross-platform module leaves bounded real-host state intact."""

    before_paths = snapshot_paths(PROTECTED_PATHS)
    before_status = snapshot_git_status(FRAMEWORK_ROOT)
    yield
    assert snapshot_paths(PROTECTED_PATHS) == before_paths
    assert snapshot_git_status(FRAMEWORK_ROOT) == before_status


def test_fixture_factory_builds_committed_offline_node_and_python_hosts(tmp_path: Path) -> None:
    disposable = create_disposable_root(tmp_path)
    node = build_node_express_fixture(disposable)
    python = build_python_fixture(disposable)

    assert node.branch == "main"
    assert python.branch == "trunk"
    for fixture in (node, python):
        assert _git(fixture.root, "branch", "--show-current") == fixture.branch
        assert _git(fixture.root, "rev-parse", "HEAD") == fixture.head
        assert _git(fixture.root, "status", "--porcelain") == ""
        assert Path(_git(fixture.root, "remote", "get-url", "origin")).resolve() == fixture.remote.resolve()
        assert fixture.remote.is_dir()
        assert _git(fixture.root, "rev-parse", f"origin/{fixture.branch}") == fixture.head

    assert (node.root / "package.json").is_file()
    assert (node.root / "package-lock.json").is_file()
    assert (node.root / "src/app.js").is_file()
    assert (node.root / "test/app.test.js").is_file()
    assert (node.root / ".github/dependabot.yml").is_file()
    assert (node.root / ".sdd-proposal/constitution/mission.md").read_bytes().endswith(b"\r\n")
    assert (python.root / "pyproject.toml").is_file()
    assert (python.root / "src/fixture_library/__init__.py").is_file()
    assert (python.root / "tests/test_identity.py").is_file()
    assert not (python.root / ".github/copilot-instructions.md").exists()


def test_fixture_snapshots_preserve_newlines_modes_and_injected_replace(tmp_path: Path) -> None:
    disposable = create_disposable_root(tmp_path)
    node = build_node_express_fixture(disposable)
    python = build_python_fixture(disposable)
    crlf = node.root / "host-owned/windows-notes.txt"
    lf = python.root / "host-owned/posix-notes.txt"
    executable = python.root / "tools/quality-check"
    before = snapshot_paths((crlf, lf, executable))

    assert b"\r\n" in crlf.read_bytes()
    assert b"\r\n" not in lf.read_bytes()
    if os.name != "nt":
        assert executable.stat().st_mode & stat.S_IXUSR

    source = disposable.root / "rename-source"
    destination = disposable.root / "rename-destination"
    source.write_bytes(b"candidate\n")
    injector = FailureInjector("before-replace")
    with pytest.raises(InjectedFixtureFailure, match="before-replace"):
        from brownfield_test_fixtures import replace_with_injection
        replace_with_injection(source, destination, injector)
    assert source.read_bytes() == b"candidate\n"
    assert not destination.exists()
    assert snapshot_paths((crlf, lf, executable)) == before


def test_fixture_sentinel_is_bound_and_cannot_be_copied(tmp_path: Path) -> None:
    disposable = create_disposable_root(tmp_path)
    copied_root = tmp_path / "copied-fixture-sentinel"
    copy_sentinel(disposable.root, copied_root)

    assert sentinel_identifies(disposable.root)
    assert not sentinel_identifies(copied_root)


def test_verified_fixture_api_rejects_unauthorized_targets_before_mutation(
    tmp_path: Path,
) -> None:
    disposable = create_disposable_root(tmp_path)
    fixture = build_node_express_fixture(disposable)
    sibling = tmp_path / "sibling-real-looking-repo"
    sibling.mkdir()
    ancestor = FRAMEWORK_ROOT.parent
    temp_looking = tmp_path / "tmp-sdd-fixture-looking-name"
    temp_looking.mkdir()
    copied = tmp_path / "copied-sentinel"
    copy_sentinel(disposable.root, copied)
    link_target = tmp_path / "link-target"
    link_target.mkdir()
    linked = tmp_path / "linked-target"
    linked_created = make_link(linked, link_target)

    targets = [FRAMEWORK_ROOT, ancestor, sibling, temp_looking, copied]
    targets.append(linked if linked_created else linked / "nonexistent-equivalent")
    compat = _production_compat()
    authorize = compat.authorize_disposable_fixture

    for target in targets:
        before = _bounded_mutation_snapshot(target)
        with pytest.raises(compat.FixtureAuthorizationError):
            authorize(target=target, temporary_root=tmp_path)
        assert _bounded_mutation_snapshot(target) == before
        assert not (target / ".sdd-stage").exists()
        assert not (target / ".sdd-backup").exists()
        assert not (target / ".sdd-transaction.json").exists()

    authorization = authorize(target=fixture.root, temporary_root=tmp_path)
    assert authorization.target == fixture.root.resolve()


def test_verified_fixture_api_cannot_authorize_real_checkout_with_fixture_sentinel(
    tmp_path: Path,
) -> None:
    disposable = create_disposable_root(tmp_path)
    copied = tmp_path / "real-checkout-copy-sentinel"
    copied.mkdir()
    shutil.copyfile(disposable.sentinel, copied / disposable.sentinel.name)

    compat = _production_compat()
    with pytest.raises(compat.FixtureAuthorizationError):
        compat.authorize_disposable_fixture(target=copied, temporary_root=tmp_path)


@pytest.mark.parametrize(("stack", "platform"), SCENARIO_CELLS)
def test_scenario_matrix_draft_baseline_identity_refresh_and_legacy_adoption(
    tmp_path: Path, stack: str, platform: str
) -> None:
    proposal_api = _module("brownfield_proposal")
    identity_api = _module("brownfield_identity")
    inventory_api = _module("brownfield_inventory")
    disposable, fixture = _fixture(tmp_path, stack)
    del disposable, platform
    evidence = inventory_api.collect_repository_evidence(fixture.root)
    assert evidence.default_branch == fixture.branch
    assert evidence.target_head == fixture.head
    assert evidence.stack == (("node",) if stack == "node" else ("python",))
    identity = identity_api.draft_identity(
        {
            "target_head": fixture.head,
            "project_name": {
                "value": evidence.project_name,
                "evidence_paths": ["package.json" if stack == "node" else "pyproject.toml"],
            },
            "default_branch": {
                "value": fixture.branch,
                "evidence_paths": [".git/HEAD"],
            },
            "stack": {
                "value": list(evidence.stack),
                "evidence_paths": ["package.json" if stack == "node" else "pyproject.toml"],
            },
        },
        "2026-07-12",
    )
    assert identity.target_head == fixture.head
    assert identity.fields["project_name"].value == evidence.project_name
    assert identity.fields["default_branch"].value == fixture.branch

    baseline = b"# Mission\n\nBaseline.\n"
    proposal = _write_baseline(fixture, baseline)
    loaded = proposal_api.load_and_validate_baseline(proposal)
    assert loaded.files[0].path == "constitution/mission.md"
    outcomes = {
        proposal_api.classify_refresh(baseline, baseline, baseline).value,
        proposal_api.classify_refresh(baseline, baseline, b"upstream\n").value,
        proposal_api.classify_refresh(baseline, b"user\n", baseline).value,
        proposal_api.classify_refresh(baseline, b"same\n", b"same\n").value,
        proposal_api.classify_refresh(baseline, b"user\n", b"upstream\n").value,
    }
    assert outcomes == {"unchanged", "upstream-only", "user-only", "convergent", "conflict"}

    legacy = fixture.root / "legacy-proposal"
    reviewed = legacy / "constitution/mission.md"
    reviewed.parent.mkdir(parents=True)
    reviewed.write_bytes(b"owner bytes\r\n")
    adoption = proposal_api.plan_baseline_adoption(
        legacy, {"constitution/mission.md": b"owner bytes\r\n"}
    )
    assert adoption.legacy_baseline_adoption
    assert not adoption.requires_resolution
    assert reviewed.read_bytes() == b"owner bytes\r\n"


@pytest.mark.parametrize(("stack", "platform"), SCENARIO_CELLS)
def test_scenario_matrix_preview_paths_text_newlines_and_permissions_are_semantic(
    tmp_path: Path, stack: str, platform: str
) -> None:
    manifest = _module("brownfield_manifest")
    disposable, fixture = _fixture(tmp_path, stack)
    del disposable
    before = b"host\r\nowned\r\n" if stack == "node" else b"host\nowned\n"
    after = "managed café\n".encode("utf-8")
    proposal = fixture.root / ".sdd-proposal"
    preserved = fixture.root / (
        "host-owned/windows-notes.txt" if stack == "node" else "host-owned/posix-notes.txt"
    )
    dry_run_paths = (proposal, preserved, fixture.root / "spec-driven-development")
    dry_run_before = snapshot_paths(dry_run_paths)
    preview = _one_file_preview(manifest, before, after)
    canonical = manifest.canonical_preview_bytes(preview)
    payload = json.loads(canonical)
    flattened = [item for category in manifest.PREVIEW_CATEGORIES for item in payload[category]]

    assert canonical.endswith(b"\n") and b"\r\n" not in canonical
    assert [item["destination"] for item in flattened] == ["spec-driven-development/managed.txt"]
    assert all("\\" not in item["destination"] for item in flattened)
    assert str(tmp_path).replace("\\", "/") not in canonical.decode("utf-8")
    assert manifest.preview_hash(preview) == _sha(canonical)
    assert snapshot_paths(dry_run_paths) == dry_run_before

    preserved_before = preserved.read_bytes()
    generated = fixture.root / "generated-utf8-lf.txt"
    generated.write_bytes(after)
    assert generated.read_text(encoding="utf-8") == "managed café\n"
    assert b"\r\n" not in generated.read_bytes()
    assert preserved.read_bytes() == preserved_before

    executable = fixture.root / "semantic-permission.txt"
    executable.write_bytes(b"same semantics\n")
    if platform == "posix" and os.name != "nt":
        executable.chmod(0o755)
        assert executable.stat().st_mode & stat.S_IXUSR
    else:
        executable.chmod(stat.S_IREAD | stat.S_IWRITE)
    assert executable.read_bytes() == b"same semantics\n"


@pytest.mark.parametrize(("stack", "platform"), SCENARIO_CELLS)
def test_scenario_matrix_clean_allowlist_seed_and_readiness_contract(
    tmp_path: Path, stack: str, platform: str
) -> None:
    manifest = _module("brownfield_manifest")
    readiness = _module("host_readiness")
    disposable, fixture = _fixture(tmp_path, stack)
    bundle = manifest.build_core_manifest(
        FRAMEWORK_ROOT,
        SimpleNamespace(fields={
            "worktree_profile": SimpleNamespace(value=False, confirmed_by="Fixture Owner")
        }),
    )
    registry = {
        entry.renderer_id: entry.renderer_version
        for entry in bundle.entries
        if entry.renderer_id is not None
    }
    validated = manifest.validate_manifest(
        bundle, FRAMEWORK_ROOT, disposable.root / "candidate", registry
    )
    seeds = manifest.build_clean_seed_bytes(validated)
    report = (
        readiness.CheckResult("fixture-allowlist", "fixture allowlist", "PASS", "closed"),
        readiness.CheckResult("fixture-seeds", "fixture seeds", "PASS", "clean"),
    )

    assert tuple(entry.destination for entry in validated.entries) == validated.topological_order
    assert manifest.find_forbidden_fingerprints(seeds) == ()
    assert all(b"\r\n" not in content for content in seeds.values())
    assert readiness.readiness_exit_code(report) == 0
    assert not (fixture.root / "spec-driven-development/ledger/fleet.db").exists()
    assert platform in {"windows", "posix"}


@pytest.mark.parametrize(("stack", "platform"), SCENARIO_CELLS)
def test_scenario_matrix_permission_link_and_rename_equivalents_fail_closed(
    tmp_path: Path, stack: str, platform: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    inventory = _module("brownfield_inventory")
    disposable, fixture = _fixture(tmp_path, stack)
    destination = fixture.root / "rename-destination.txt"
    source = fixture.root / "rename-source.txt"
    source.write_bytes(b"candidate\n")
    before = snapshot_paths((source, destination))
    with pytest.raises(InjectedFixtureFailure):
        from brownfield_test_fixtures import replace_with_injection
        replace_with_injection(source, destination, FailureInjector("before-replace"))
    assert snapshot_paths((source, destination)) == before

    external = disposable.root / "external"
    external.mkdir()
    link = fixture.root / "linked-destination"
    created = make_link(link, external)
    if not created:
        monkeypatch.setattr(
            inventory,
            "_link_kind",
            lambda path, info=None: "junction" if Path(path) == link else None,
        )
        link.mkdir()
    with pytest.raises(inventory.PathSafetyError, match="link|junction|reparse"):
        inventory.safe_relative_path(
            "linked-destination/file.txt",
            fixture.root,
            "fixture destination",
            allow_missing=True,
        )
    assert platform in {"windows", "posix"}


@pytest.mark.parametrize(("stack", "platform"), SCENARIO_CELLS)
def test_scenario_matrix_apply_failure_recovery_rerun_and_migration(
    tmp_path: Path, stack: str, platform: str
) -> None:
    manifest = _module("brownfield_manifest")
    migration = _module("brownfield_migration")
    disposable, fixture = _fixture(tmp_path, stack)
    _write_baseline(fixture, b"# Mission\n")
    candidate = "managed UTF-8 café\n".encode("utf-8")
    preview = _one_file_preview(manifest, None, candidate)
    managed = fixture.root / "spec-driven-development/managed.txt"
    protected = (
        managed,
        fixture.root / ".sdd-proposal/constitution/mission.md",
    )
    before = snapshot_paths(protected)
    assert manifest.canonical_preview_bytes(preview) == manifest.canonical_preview_bytes(
        manifest.Preview("1", manifest.PREVIEW_CATEGORIES, tuple(reversed(preview.items)))
    )
    transaction, context = _transaction_context(disposable, fixture, preview, candidate)
    failed = transaction.promote(
        context, injector=transaction.FailureInjector(fail_at="after-create")
    )
    assert (failed.exit_code, failed.status, failed.verified) == (1, "rolled-back", True)
    assert snapshot_paths(protected) == before

    success_root = create_disposable_root(tmp_path, name=f"success-{stack}-{platform}")
    success_fixture = (
        build_node_express_fixture(success_root)
        if stack == "node" else build_python_fixture(success_root)
    )
    success_proposal = _write_baseline(success_fixture, b"# Mission\r\n")
    proposal_before = success_proposal.joinpath("constitution/mission.md").read_bytes()
    transaction, successful = _transaction_context(
        success_root, success_fixture, preview, candidate
    )
    committed = transaction.promote(successful)
    installed = success_fixture.root / "spec-driven-development/managed.txt"
    assert (committed.exit_code, committed.status, committed.verified) == (0, "committed", True)
    assert installed.read_bytes() == candidate
    assert b"\r\n" not in installed.read_bytes()
    assert success_proposal.joinpath("constitution/mission.md").read_bytes() == proposal_before

    interrupted_root = create_disposable_root(tmp_path, name=f"interrupted-{stack}-{platform}")
    interrupted_fixture = (
        build_node_express_fixture(interrupted_root)
        if stack == "node" else build_python_fixture(interrupted_root)
    )
    _write_baseline(interrupted_fixture, b"# Mission\n")
    transaction, interrupted = _transaction_context(
        interrupted_root, interrupted_fixture, preview, candidate
    )
    with pytest.raises(transaction.InjectedInterruption):
        transaction.promote(
            interrupted,
            injector=transaction.FailureInjector(fail_at="create:applied:after-flush"),
        )
    recovered = transaction.recover(
        interrupted.journal_path,
        action="rollback",
        workspace=interrupted.workspace,
        target=interrupted.target,
        authorization=interrupted.authorization,
    )
    assert (recovered.exit_code, recovered.status, recovered.verified) == (0, "rolled-back", True)
    assert not (interrupted_fixture.root / "spec-driven-development/managed.txt").exists()

    managed_current = migration.InstallationClassification(
        migration.InstallationClass.MANAGED_CURRENT,
        ("all managed bytes match",),
        (),
        True,
        "no migration required",
    )
    rerun = migration.plan_migration(managed_current, SimpleNamespace(entries=()), None, None)
    assert rerun.status == "no-op"
    assert not rerun.side_effects and not rerun.write_receipt and not rerun.write_operational_ledger

    drift = replace(
        managed_current,
        installation_class=migration.InstallationClass.MANAGED_DRIFT,
    )
    blocked = migration.plan_migration(drift, SimpleNamespace(entries=()), None, None)
    assert blocked.status == "blocked"
    assert blocked.requires_approval
    assert not blocked.side_effects

    contaminated = replace(
        managed_current,
        installation_class=migration.InstallationClass.MIXED_CONTAMINATED,
        reasons=("managed state coexists with fixture contamination",),
    )
    contaminated_plan = migration.plan_migration(
        contaminated, SimpleNamespace(entries=()), None, None
    )
    assert contaminated_plan.status == "blocked"
    assert contaminated_plan.requires_approval
    assert not contaminated_plan.side_effects


def test_doctor_workflow_runs_cross_platform_sdd058_matrix_before_public_gate() -> None:
    workflow = FRAMEWORK_ROOT / ".github/workflows/doctor.yml"
    text = workflow.read_text(encoding="utf-8")
    focused = "Run focused SDD-058 suite"
    doctor = "python spec-driven-development/cli/bootstrap.py doctor --mode ci"
    expected_tests = (
        "test_brownfield_cli.py",
        "test_brownfield_cross_platform.py",
        "test_brownfield_identity.py",
        "test_brownfield_inventory.py",
        "test_brownfield_manifest.py",
        "test_brownfield_migration.py",
        "test_brownfield_proposal.py",
        "test_brownfield_transaction.py",
        "test_host_readiness.py",
    )

    assert "os: [ubuntu-latest, windows-latest]" in text
    assert "python-version: ['3.12']" in text
    assert "permissions:\n  contents: read" in text
    assert all(name in text for name in expected_tests)
    assert text.index(focused) < text.index(doctor)
    assert all(forbidden not in text.lower() for forbidden in (
        "secrets.", "azure/login", "deploy", "id-token: write"
    ))
