"""RED-5 bounded host-readiness contract for SDD-058.

Covers R-025 through R-028A and V-34 through V-38A. The tests use only
harmless ``tmp_path`` fixtures and stubbed subprocesses; they never inspect or
mutate a real host and never run a host-provided quality command.
"""

from __future__ import annotations

import base64
import importlib
import json
import os
import sys
import time
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import pytest

CLI_DIR = Path(__file__).resolve().parent
if str(CLI_DIR) not in sys.path:
    sys.path.insert(0, str(CLI_DIR))

STRUCTURAL_CHECK_IDS = (
    "bundle-receipt-dependency-integrity",
    "managed-asset-integrity",
    "confirmed-identity-config-instructions",
    "constitution-files",
    "installed-source-frontmatter",
    "unresolved-placeholders",
    "runtime-seed-forbidden-fingerprints",
    "ledger-schema-adoption-receipt",
    "gitignore-tracked-safety",
    "quality-command-token-validity",
)
FRAMEWORK_NA_ROWS = (
    ("framework-governance", "framework governance"),
    ("framework-stale-doc", "framework stale-doc"),
    ("framework-current-pi", "framework current-PI"),
    ("framework-test-baseline", "framework test baseline"),
    ("framework-generated-surfaces", "generated framework surfaces"),
)
QUALITY_NAMES = ("test", "lint", "typecheck", "build")


def _readiness():
    """Import the intentionally absent production module inside each test."""

    return importlib.import_module("host_readiness")


def _quality(
    *,
    argv: tuple[str, ...] = ("python", "-c", "print('fixture quality')"),
    cwd: str = ".",
    timeout: int = 17,
    environment_policy: str = "minimal",
    network_policy: str = "deny",
) -> dict[str, object]:
    return {
        "state": "configured",
        "argv": list(argv),
        "cwd": cwd,
        "timeout_seconds": timeout,
        "environment_policy": environment_policy,
        "network_policy": network_policy,
    }


def _not_configured() -> dict[str, object]:
    return {
        "state": "not-configured",
        "argv": [],
        "cwd": None,
        "timeout_seconds": None,
        "environment_policy": "minimal",
        "network_policy": "deny",
    }


def _identity(commands: dict[str, dict[str, object]]) -> SimpleNamespace:
    field = SimpleNamespace(
        value=commands,
        classification="human",
        ambiguity="none",
        confirmed_by="Fixture Owner",
        confirmed_at="2026-07-12T12:00:00Z",
    )
    return SimpleNamespace(fields={"quality_commands": field})


def _all_not_configured_identity() -> SimpleNamespace:
    return _identity({name: _not_configured() for name in QUALITY_NAMES})


def _pass(readiness, check_id: str = "fixture"):
    return readiness.CheckResult(check_id, check_id.replace("-", " "), "PASS", "ok")


def _fail(readiness, check_id: str = "fixture"):
    return readiness.CheckResult(check_id, check_id.replace("-", " "), "FAIL", "not ready")


def test_run_structural_checks_invokes_exact_bounded_checker_composition(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    readiness = _readiness()
    calls: list[str] = []

    assert tuple(readiness.STRUCTURAL_CHECK_IDS) == STRUCTURAL_CHECK_IDS
    assert tuple(readiness.STRUCTURAL_CHECKERS) == STRUCTURAL_CHECK_IDS
    for check_id in STRUCTURAL_CHECK_IDS:
        def checker(*_args, _check_id=check_id, **_kwargs):
            calls.append(_check_id)
            return _pass(readiness, _check_id)

        monkeypatch.setitem(readiness.STRUCTURAL_CHECKERS, check_id, checker)

    report = readiness.run_structural_checks(
        tmp_path, object(), object(), object(), staged=False
    )

    assert calls == list(STRUCTURAL_CHECK_IDS)
    required = [check.id for check in report.checks if check.status != "N/A"]
    assert required == list(STRUCTURAL_CHECK_IDS)
    assert report.mode == "structural-final"
    assert report.exit_code == 0


def test_run_structural_checks_reports_exact_five_framework_rows_na(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    readiness = _readiness()
    for check_id in STRUCTURAL_CHECK_IDS:
        monkeypatch.setitem(
            readiness.STRUCTURAL_CHECKERS,
            check_id,
            lambda *_args, _id=check_id, **_kwargs: _pass(readiness, _id),
        )

    report = readiness.run_structural_checks(
        tmp_path, object(), object(), object(), staged=False
    )

    framework_rows = [
        (check.id, check.label, check.status)
        for check in report.checks
        if check.id.startswith("framework-")
        or check.id == "framework-generated-surfaces"
    ]
    assert framework_rows == [(*row, "N/A") for row in FRAMEWORK_NA_ROWS]
    assert all(status != "PASS" for _, _, status in framework_rows)


def test_host_readiness_does_not_import_or_invoke_framework_doctor(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    bootstrap_sentinel = mock.Mock(side_effect=AssertionError("framework doctor invoked"))
    fake_bootstrap = SimpleNamespace(run_doctor=bootstrap_sentinel)
    monkeypatch.setitem(sys.modules, "bootstrap", fake_bootstrap)
    sys.modules.pop("host_readiness", None)

    readiness = _readiness()
    for check_id in STRUCTURAL_CHECK_IDS:
        monkeypatch.setitem(
            readiness.STRUCTURAL_CHECKERS,
            check_id,
            lambda *_args, _id=check_id, **_kwargs: _pass(readiness, _id),
        )
    report = readiness.run_structural_checks(
        tmp_path, object(), object(), object(), staged=False
    )

    assert report.exit_code == 0
    bootstrap_sentinel.assert_not_called()
    source = Path(readiness.__file__).read_text(encoding="utf-8")
    assert "import bootstrap" not in source
    assert "run_doctor" not in source


def test_readiness_exit_code_maps_pass_failure_configuration_and_recovery() -> None:
    readiness = _readiness()

    assert readiness.readiness_exit_code((_pass(readiness),)) == 0
    assert readiness.readiness_exit_code((_pass(readiness), _fail(readiness))) == 1
    assert readiness.readiness_exit_code(
        (_pass(readiness),), configuration_valid=False
    ) == 2
    assert readiness.readiness_exit_code(
        (_fail(readiness),), recovery_required=True
    ) == 3


def test_main_returns_usage_exit_two_for_invalid_configuration(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    readiness = _readiness()
    invalid = tmp_path / "invalid-identity.json"
    invalid.write_text("{}\n", encoding="utf-8")

    result = readiness.main(["--root", str(tmp_path), "--identity", str(invalid)])

    assert result == 2
    assert "host readiness" in capsys.readouterr().err.lower()


def test_format_readiness_summary_uses_bounded_host_only_wording() -> None:
    readiness = _readiness()
    passed = readiness.ReadinessReport("1", "structural-final", (_pass(readiness),), 0)
    failed = readiness.ReadinessReport("1", "structural-final", (_fail(readiness),), 1)
    recovery = readiness.ReadinessReport("1", "structural-final", (_fail(readiness),), 3)

    success_text = readiness.format_readiness_summary(passed, installed=True)
    failure_text = readiness.format_readiness_summary(failed, installed=True)
    recovery_text = readiness.format_readiness_summary(recovery, installed=True)

    assert success_text == "installed; host readiness PASS"
    assert "framework" not in success_text.lower()
    assert "ready" not in failure_text.lower()
    assert "pass" not in failure_text.lower()
    assert "recovery required" in recovery_text.lower()
    assert "ready" not in recovery_text.lower()
    assert "framework" not in failure_text.lower() + recovery_text.lower()


def test_staged_structural_readiness_never_runs_quality_commands(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    readiness = _readiness()
    for check_id in STRUCTURAL_CHECK_IDS:
        monkeypatch.setitem(
            readiness.STRUCTURAL_CHECKERS,
            check_id,
            lambda *_args, _id=check_id, **_kwargs: _pass(readiness, _id),
        )
    quality = mock.Mock(side_effect=AssertionError("quality command ran during apply"))
    monkeypatch.setattr(readiness, "run_quality_checks", quality)
    subprocess_run = mock.Mock(side_effect=AssertionError("subprocess ran during apply"))
    monkeypatch.setattr(readiness.subprocess, "run", subprocess_run)

    report = readiness.run_structural_checks(
        tmp_path, object(), _all_not_configured_identity(), object(), staged=True
    )

    assert report.mode == "structural-staged"
    assert report.exit_code == 0
    quality.assert_not_called()
    subprocess_run.assert_not_called()


def test_staged_root_view_composes_candidate_and_preserved_host_without_broad_copy(
    tmp_path: Path,
) -> None:
    readiness = _readiness()
    host = tmp_path / "host"
    stage = tmp_path / "stage"
    (host / "preserved").mkdir(parents=True)
    (stage / "candidate").mkdir(parents=True)
    (host / "preserved/host.txt").write_bytes(b"host bytes\r\n")
    (host / "unlisted-framework-source.py").write_bytes(b"must not be visible\n")
    (stage / "candidate/new.txt").write_bytes(b"candidate bytes\n")

    view = readiness.staged_root_view(
        host,
        stage,
        ("candidate/new.txt", "preserved/host.txt"),
    )

    assert readiness.root_view_path(view, "candidate/new.txt").read_bytes() == b"candidate bytes\n"
    assert readiness.root_view_path(view, "preserved/host.txt").read_bytes() == b"host bytes\r\n"
    with pytest.raises(readiness.ReadinessConfigurationError, match="unlisted"):
        readiness.root_view_path(view, "unlisted-framework-source.py")
    assert list(stage.rglob("*")) == [stage / "candidate", stage / "candidate/new.txt"]


def test_run_quality_checks_discloses_policy_before_token_array_execution(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    readiness = _readiness()
    work = tmp_path / "service"
    work.mkdir()
    commands = {name: _not_configured() for name in QUALITY_NAMES}
    commands["test"] = _quality(cwd="service", network_policy="allow-confirmed")
    identity = _identity(commands)
    events: list[tuple[str, object]] = []

    def disclosure_sink(text: str) -> None:
        events.append(("disclosure", text))

    def fake_execute(argv, cwd, timeout, environment):
        events.append(("run", (argv, cwd, timeout, environment)))
        return SimpleNamespace(returncode=0, stdout="fixture ok\n", stderr="")

    monkeypatch.setattr(readiness, "_execute_quality_command", fake_execute)
    report = readiness.run_quality_checks(tmp_path, identity, disclosure_sink)

    assert events[0][0] == "disclosure"
    disclosure = str(events[0][1]).lower()
    for required in (
        "cwd",
        "argv",
        "17",
        "minimal",
        "allow-confirmed",
        "outside rollback",
        "filesystem",
        "external",
    ):
        assert required in disclosure
    argv, cwd, timeout, environment = events[1][1]
    assert argv == ["python", "-c", "print('fixture quality')"]
    assert cwd == work
    assert timeout == 17
    assert isinstance(environment, dict)
    assert environment is not os.environ
    assert report.exit_code == 0


def test_run_quality_checks_maps_command_failure_to_exit_one(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    readiness = _readiness()
    commands = {name: _not_configured() for name in QUALITY_NAMES}
    commands["lint"] = _quality(
        argv=("python", "-c", "raise SystemExit(7)"),
        network_policy="allow-confirmed",
    )
    identity = _identity(commands)
    monkeypatch.setattr(
        readiness,
        "_execute_quality_command",
        lambda *_args, **_kwargs: SimpleNamespace(returncode=7, stdout="", stderr="fixture failure"),
    )

    report = readiness.run_quality_checks(tmp_path, identity, lambda _text: None)

    lint = next(check for check in report.checks if check.id == "quality-lint")
    assert lint.status == "FAIL"
    assert report.exit_code == 1


def test_run_quality_checks_reports_confirmed_not_configured_as_na(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    readiness = _readiness()
    subprocess_run = mock.Mock(side_effect=AssertionError("N/A command executed"))
    monkeypatch.setattr(readiness.subprocess, "run", subprocess_run)

    report = readiness.run_quality_checks(
        tmp_path, _all_not_configured_identity(), lambda _text: None
    )

    assert [(check.id, check.status) for check in report.checks] == [
        (f"quality-{name}", "N/A") for name in QUALITY_NAMES
    ]
    assert report.exit_code == 0
    subprocess_run.assert_not_called()


def test_run_quality_checks_rejects_unsafe_cwd_argv_timeout_and_policy(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    readiness = _readiness()
    unsafe_commands = (
        _quality(cwd="../outside"),
        _quality(argv=()),
        _quality(timeout=0),
        _quality(timeout=3601),
        _quality(environment_policy="inherit"),
        _quality(network_policy="allow"),
    )
    subprocess_run = mock.Mock(side_effect=AssertionError("invalid command executed"))
    monkeypatch.setattr(readiness.subprocess, "run", subprocess_run)

    for unsafe in unsafe_commands:
        commands = {name: _not_configured() for name in QUALITY_NAMES}
        commands["test"] = unsafe
        with pytest.raises(readiness.ReadinessConfigurationError):
            readiness.run_quality_checks(
                tmp_path, _identity(commands), lambda _text: None
            )

    subprocess_run.assert_not_called()


def test_run_quality_checks_never_uses_shell_even_when_argument_contains_metacharacters(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    readiness = _readiness()
    commands = {name: _not_configured() for name in QUALITY_NAMES}
    commands["build"] = _quality(
        argv=("python", "-c", "print('literal')", "&&", "not-a-command"),
        network_policy="allow-confirmed",
    )
    identity = _identity(commands)
    stdin = mock.Mock()
    process = SimpleNamespace(
        communicate=lambda timeout=None: ("", ""),
        stdin=stdin,
        pid=12345,
        returncode=0,
    )
    boundary = SimpleNamespace(
        assign=lambda _process: None,
        terminate_and_verify=lambda _process: None,
    )
    subprocess_popen = mock.Mock(return_value=process)
    monkeypatch.setattr(readiness.subprocess, "Popen", subprocess_popen)
    monkeypatch.setattr(readiness, "_WindowsJobObject", lambda: boundary)

    readiness.run_quality_checks(tmp_path, identity, lambda _text: None)

    args, kwargs = subprocess_popen.call_args
    broker_argv = args[0]
    decoded = json.loads(base64.b64decode(broker_argv[3]).decode("utf-8"))
    assert decoded == ["python", "-c", "print('literal')", "&&", "not-a-command"]
    assert kwargs["shell"] is False
    stdin.write.assert_called_once_with("start\n")


def test_deny_policy_refuses_before_launch_when_enforcing_executor_is_unavailable(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    readiness = _readiness()
    commands = {name: _not_configured() for name in QUALITY_NAMES}
    commands["test"] = _quality()
    launched = mock.Mock(side_effect=AssertionError("deny command launched"))
    monkeypatch.setattr(readiness.subprocess, "run", launched)

    with pytest.raises(readiness.ReadinessConfigurationError, match="network|deny|enforce"):
        readiness.run_quality_checks(tmp_path, _identity(commands), lambda _text: None)

    launched.assert_not_called()


def test_gitignore_unexpected_return_code_fails_closed_and_redacts_diagnostics(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    readiness = _readiness()
    (tmp_path / ".git").mkdir()
    secret = "GIT_TOKEN_CANARY"
    monkeypatch.setattr(
        readiness.subprocess,
        "run",
        lambda *_args, **_kwargs: SimpleNamespace(
            returncode=128, stdout="", stderr=f"fatal: --token {secret}"
        ),
    )
    receipt = SimpleNamespace(managed_hashes={"managed.txt": "0" * 64})

    result = readiness._check_gitignore(tmp_path, object(), object(), receipt)

    assert result.status == "FAIL"
    assert "128" in result.detail
    assert secret not in result.detail


def test_managed_python_control_literals_do_not_fail_host_content_portability_scans(
    tmp_path: Path,
) -> None:
    readiness = _readiness()
    control = tmp_path / "spec-driven-development/cli/control.py"
    control.parent.mkdir(parents=True)
    control.write_text(
        'TEMPLATE_HELP = "Host project name used for {{PROJECT_NAME}} placeholders."\n'
        'FORBIDDEN_FINGERPRINTS = ("evolving-multi-agent-framework",)\n',
        encoding="utf-8",
    )
    (tmp_path / "spec-driven-development/backlog").mkdir(parents=True)
    (tmp_path / "spec-driven-development/backlog/IDEAS.md").write_text("# Ideas\n", encoding="utf-8")
    (tmp_path / "spec-driven-development/backlog/BACKLOG.md").write_text("# Backlog\n", encoding="utf-8")
    receipt = SimpleNamespace(
        managed_hashes={"spec-driven-development/cli/control.py": "0" * 64}
    )

    placeholders = readiness._check_placeholders(tmp_path, object(), object(), receipt)
    runtime_seed = readiness._check_runtime_seed(tmp_path, object(), object(), receipt)

    assert placeholders.status == "PASS"
    assert runtime_seed.status == "PASS"


def test_quality_evidence_redacts_argv_output_and_exception_canaries(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    readiness = _readiness()
    commands = {name: _not_configured() for name in QUALITY_NAMES}
    commands["test"] = _quality(network_policy="allow-confirmed")
    identity = _identity(commands)
    disclosures: list[str] = []
    secret = "QUALITY_SECRET_CANARY"
    monkeypatch.setattr(
        readiness,
        "_execute_quality_command",
        lambda *_args, **_kwargs: SimpleNamespace(
            returncode=7, stdout=secret, stderr=f"--password {secret}"
        ),
        raising=False,
    )

    report = readiness.run_quality_checks(tmp_path, identity, disclosures.append)
    evidence = repr((disclosures, report))

    assert secret not in evidence


def test_quality_timeout_executor_terminates_descendant_boundary_before_return(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    readiness = _readiness()
    events: list[str] = []
    process = SimpleNamespace(
        communicate=lambda timeout=None: (_ for _ in ()).throw(
            readiness.subprocess.TimeoutExpired(["fixture"], timeout)
        ),
        returncode=None,
    )
    contained = SimpleNamespace(process=process)
    monkeypatch.setattr(readiness, "_spawn_contained_process", lambda *_a, **_k: contained, raising=False)
    monkeypatch.setattr(readiness, "_terminate_process_tree", lambda _p: events.append("tree-terminated"), raising=False)

    result = readiness._execute_quality_command(
        ["fixture"], tmp_path, 1, readiness._minimal_environment()
    )

    assert events == ["tree-terminated"]
    assert result.returncode != 0


def test_quality_command_fails_before_launch_when_containment_is_unavailable(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    readiness = _readiness()
    if os.name != "nt":
        pytest.skip("Windows Job Object construction failure contract")
    launch = mock.Mock(side_effect=AssertionError("quality command launched"))
    monkeypatch.setattr(readiness.subprocess, "Popen", launch)
    monkeypatch.setattr(
        readiness,
        "_WindowsJobObject",
        mock.Mock(side_effect=readiness.ContainmentUnavailableError("unavailable")),
    )

    with pytest.raises(readiness.ContainmentUnavailableError, match="unavailable"):
        readiness._execute_quality_command(
            ["fixture"], tmp_path, 1, readiness._minimal_environment()
        )

    launch.assert_not_called()


def test_non_windows_quality_command_fails_before_process_launch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    readiness = _readiness()
    launch = mock.Mock(side_effect=AssertionError("quality command launched"))
    monkeypatch.setattr(readiness.os, "name", "posix")
    monkeypatch.setattr(readiness.subprocess, "Popen", launch)

    with pytest.raises(readiness.ContainmentUnavailableError, match="only available on Windows"):
        readiness._execute_quality_command(
            ["fixture"], tmp_path, 1, readiness._minimal_environment()
        )

    launch.assert_not_called()


def test_quality_command_propagates_unverifiable_boundary_termination(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    readiness = _readiness()
    process = SimpleNamespace(
        communicate=lambda timeout=None: ("", ""),
        returncode=0,
    )
    contained = SimpleNamespace(process=process)
    monkeypatch.setattr(readiness, "_spawn_contained_process", lambda *_a, **_k: contained)
    monkeypatch.setattr(
        readiness,
        "_terminate_process_tree",
        mock.Mock(side_effect=RuntimeError("descendants remain active")),
    )

    with pytest.raises(RuntimeError, match="descendants remain active"):
        readiness._execute_quality_command(
            ["fixture"], tmp_path, 1, readiness._minimal_environment()
        )


def test_quality_timeout_terminates_real_descendant_process_before_return(
    tmp_path: Path,
) -> None:
    readiness = _readiness()
    child_pid_path = tmp_path / "child.pid"
    child = tmp_path / "child.py"
    child.write_text("import time\nwhile True:\n    time.sleep(1)\n", encoding="utf-8")
    parent = tmp_path / "parent.py"
    parent.write_text(
        "import pathlib, subprocess, sys, time\n"
        "process = subprocess.Popen([sys.executable, sys.argv[1]])\n"
        "pathlib.Path(sys.argv[2]).write_text(str(process.pid), encoding='utf-8')\n"
        "while True:\n"
        "    time.sleep(1)\n",
        encoding="utf-8",
    )

    result = readiness._execute_quality_command(
        [sys.executable, str(parent), str(child), str(child_pid_path)],
        tmp_path,
        1,
        readiness._minimal_environment(),
    )

    assert result.returncode == 124
    assert child_pid_path.is_file()
    child_pid = int(child_pid_path.read_text(encoding="utf-8"))
    deadline = time.monotonic() + 2
    while time.monotonic() < deadline and _pid_is_active(child_pid):
        time.sleep(0.05)
    assert _pid_is_active(child_pid) is False


@pytest.mark.skipif(os.name != "nt", reason="Windows Job Object contract")
def test_windows_quality_process_uses_genuine_job_object_containment(
    tmp_path: Path,
) -> None:
    readiness = _readiness()
    contained = readiness._spawn_contained_process(
        [sys.executable, "-c", "print('contained')"],
        tmp_path,
        readiness._minimal_environment(),
    )

    try:
        assert contained.kind == "windows-job-object"
        stdout, _stderr = contained.process.communicate(timeout=5)
        assert stdout.strip() == "contained"
    finally:
        contained.terminate_and_verify()


@pytest.mark.skipif(not sys.platform.startswith("linux"), reason="Linux refusal contract")
def test_linux_quality_process_refuses_before_user_command(
    tmp_path: Path,
) -> None:
    readiness = _readiness()
    marker = tmp_path / "user-command-started"
    argv = [sys.executable, "-c", f"from pathlib import Path; Path({str(marker)!r}).touch()"]

    with pytest.raises(readiness.ContainmentUnavailableError, match="Windows"):
        readiness._spawn_contained_process(
            argv,
            tmp_path,
            readiness._minimal_environment(),
        )

    assert marker.exists() is False


def _pid_is_active(pid: int) -> bool:
    if os.name != "nt":
        try:
            os.kill(pid, 0)
        except OSError:
            return False
        return True

    import ctypes
    from ctypes import wintypes

    process = ctypes.WinDLL("kernel32", use_last_error=True).OpenProcess(
        0x1000, False, pid
    )
    if not process:
        return False
    try:
        exit_code = wintypes.DWORD()
        if not ctypes.WinDLL("kernel32", use_last_error=True).GetExitCodeProcess(
            process, ctypes.byref(exit_code)
        ):
            return False
        return exit_code.value == 259
    finally:
        ctypes.WinDLL("kernel32", use_last_error=True).CloseHandle(process)
