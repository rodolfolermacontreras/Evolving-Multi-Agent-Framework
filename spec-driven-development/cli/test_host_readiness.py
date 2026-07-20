"""RED-5 bounded host-readiness contract for SDD-058.

Covers R-025 through R-028A and V-34 through V-38A. The tests use only
harmless ``tmp_path`` fixtures and stubbed subprocesses; they never inspect or
mutate a real host and never run a host-provided quality command.
"""

from __future__ import annotations

import importlib
import os
import sys
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
    commands["test"] = _quality(cwd="service")
    identity = _identity(commands)
    events: list[tuple[str, object]] = []

    def disclosure_sink(text: str) -> None:
        events.append(("disclosure", text))

    def fake_run(argv, **kwargs):
        events.append(("run", (argv, kwargs)))
        return SimpleNamespace(returncode=0, stdout="fixture ok\n", stderr="")

    monkeypatch.setattr(readiness.subprocess, "run", fake_run)
    report = readiness.run_quality_checks(tmp_path, identity, disclosure_sink)

    assert events[0][0] == "disclosure"
    disclosure = str(events[0][1]).lower()
    for required in (
        "cwd",
        "argv",
        "17",
        "minimal",
        "deny",
        "outside rollback",
        "filesystem",
        "external",
    ):
        assert required in disclosure
    argv, kwargs = events[1][1]
    assert argv == ["python", "-c", "print('fixture quality')"]
    assert kwargs["cwd"] == work
    assert kwargs["timeout"] == 17
    assert kwargs["shell"] is False
    assert isinstance(kwargs["env"], dict)
    assert kwargs["env"] is not os.environ
    assert report.exit_code == 0


def test_run_quality_checks_maps_command_failure_to_exit_one(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    readiness = _readiness()
    commands = {name: _not_configured() for name in QUALITY_NAMES}
    commands["lint"] = _quality(argv=("python", "-c", "raise SystemExit(7)"))
    identity = _identity(commands)
    monkeypatch.setattr(
        readiness.subprocess,
        "run",
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
        argv=("python", "-c", "print('literal')", "&&", "not-a-command")
    )
    identity = _identity(commands)
    subprocess_run = mock.Mock(
        return_value=SimpleNamespace(returncode=0, stdout="", stderr="")
    )
    monkeypatch.setattr(readiness.subprocess, "run", subprocess_run)

    readiness.run_quality_checks(tmp_path, identity, lambda _text: None)

    args, kwargs = subprocess_run.call_args
    assert args[0] == ["python", "-c", "print('literal')", "&&", "not-a-command"]
    assert kwargs["shell"] is False
