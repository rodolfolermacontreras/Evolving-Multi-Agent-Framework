"""Bounded, host-only readiness checks for an installed SDD bundle.

Structural readiness is intentionally separate from framework health.  It is
safe to run against a staged candidate and never executes host quality commands.
Quality commands run only through the explicit quality profile after their
execution policy and outside-rollback side effects have been disclosed.
"""

from __future__ import annotations

import argparse
import base64
from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import sqlite3
import subprocess
import sys
from types import SimpleNamespace
from typing import Callable, Iterable, Mapping, Sequence

SCHEMA_VERSION = "1"
QUALITY_NAMES = ("test", "lint", "typecheck", "build")
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
CONSTITUTION_FILES = (
    "mission.md",
    "tech-stack.md",
    "principles.md",
    "roadmap.md",
    "decision-policy.md",
    "quality-policy.md",
)
_PLACEHOLDER = re.compile(r"\{\{[A-Z][A-Z0-9_]*\}\}")
_FRONTMATTER_PATHS = (
    ".github/agents/",
    ".github/prompts/",
    ".github/skills/",
)
_FORBIDDEN_FINGERPRINTS = (
    "evolving-multi-agent-framework",
    "brownfield bootstrap preserves proposals",
)


class ReadinessConfigurationError(ValueError):
    """Host-readiness configuration is invalid and cannot be executed safely."""


class ContainmentUnavailableError(OSError):
    """The operating system cannot provide the required process containment."""


@dataclass(frozen=True, slots=True)
class CheckResult:
    id: str
    label: str
    status: str
    detail: str

    def __post_init__(self) -> None:
        if self.status not in {"PASS", "FAIL", "N/A"}:
            raise ValueError("readiness status must be PASS, FAIL, or N/A")


@dataclass(frozen=True, slots=True)
class ReadinessReport:
    schema_version: str
    mode: str
    checks: tuple[CheckResult, ...]
    exit_code: int


@dataclass(frozen=True, slots=True)
class StagedRootView:
    host_root: Path
    stage_root: Path
    allowed_paths: frozenset[str]


def staged_root_view(
    host_root: Path,
    stage_root: Path,
    allowed_paths: Iterable[str],
) -> StagedRootView:
    """Create a read-only, allowlisted candidate-over-host root composition."""

    host = Path(host_root).resolve()
    stage = Path(stage_root).resolve()
    allowed = frozenset(str(PurePosixPath(path)) for path in allowed_paths)
    for relative in allowed:
        _safe_path(host, relative)
        _safe_path(stage, relative)
    return StagedRootView(host, stage, allowed)


def root_view_path(root_view: Path | StagedRootView, relative: str) -> Path:
    if isinstance(root_view, StagedRootView):
        if relative not in root_view.allowed_paths:
            raise ReadinessConfigurationError(f"unlisted staged root path: {relative}")
        staged = _safe_path(root_view.stage_root, relative)
        return staged if staged.exists() else _safe_path(root_view.host_root, relative)
    return _safe_path(Path(root_view), relative)


def _host_root(root_view: Path | StagedRootView) -> Path:
    return root_view.host_root if isinstance(root_view, StagedRootView) else Path(root_view)


def _result(check_id: str, status: str, detail: str) -> CheckResult:
    return CheckResult(check_id, check_id.replace("-", " "), status, detail)


def readiness_exit_code(
    checks: Iterable[CheckResult],
    *,
    configuration_valid: bool = True,
    recovery_required: bool = False,
) -> int:
    """Map a bounded report to the public 0/1/2/3 exit contract."""

    if recovery_required:
        return 3
    if not configuration_valid:
        return 2
    return 1 if any(check.status == "FAIL" for check in checks) else 0


def _entries(bundle: object) -> tuple[object, ...]:
    value = getattr(bundle, "entries", None)
    if not isinstance(value, (tuple, list)):
        raise ReadinessConfigurationError("bundle entries are missing")
    return tuple(value)


def _managed_hashes(receipt: object) -> Mapping[str, str]:
    value = getattr(receipt, "managed_hashes", None)
    if not isinstance(value, Mapping):
        raise ReadinessConfigurationError("adoption receipt managed hashes are missing")
    if any(not isinstance(path, str) or not isinstance(digest, str) for path, digest in value.items()):
        raise ReadinessConfigurationError("adoption receipt managed hashes are invalid")
    return value


def _safe_path(root: Path, relative: str) -> Path:
    if not isinstance(relative, str) or not relative or "\\" in relative:
        raise ReadinessConfigurationError("readiness path is not POSIX-relative")
    if relative == ".":
        return root
    pure = PurePosixPath(relative)
    if pure.is_absolute() or any(part in {"", ".", ".."} for part in pure.parts):
        raise ReadinessConfigurationError("readiness path escapes the host root")
    candidate = (root / pure).resolve()
    if candidate != root and root not in candidate.parents:
        raise ReadinessConfigurationError("readiness path escapes the host root")
    return candidate


def _check_bundle_receipt(root: Path, bundle: object, identity: object, receipt: object) -> CheckResult:
    del root, identity
    try:
        entries = _entries(bundle)
        destinations = [getattr(entry, "destination", None) for entry in entries]
        if not entries or any(not isinstance(path, str) or not path for path in destinations):
            raise ReadinessConfigurationError("bundle destinations are invalid")
        if len(destinations) != len(set(destinations)):
            raise ReadinessConfigurationError("bundle destinations are duplicated")
        members = set(destinations)
        for entry in entries:
            dependencies = getattr(entry, "dependencies", ())
            if not isinstance(dependencies, (tuple, list)) or any(dep not in members for dep in dependencies):
                raise ReadinessConfigurationError("bundle dependency closure is invalid")
        hashes = _managed_hashes(receipt)
        if any(path not in members for path in hashes):
            raise ReadinessConfigurationError("receipt names a non-bundle destination")
        for name in ("schema_version", "bundle_id", "framework_revision"):
            left = getattr(bundle, name, None)
            right = getattr(receipt, name, left)
            if left is not None and right is not None and left != right:
                raise ReadinessConfigurationError(f"receipt {name} does not match the bundle")
    except ReadinessConfigurationError as exc:
        return _result(STRUCTURAL_CHECK_IDS[0], "FAIL", str(exc))
    return _result(STRUCTURAL_CHECK_IDS[0], "PASS", "bundle, receipt, and dependency closure are valid")


def _check_managed_integrity(root: Path, bundle: object, identity: object, receipt: object) -> CheckResult:
    del bundle, identity
    try:
        hashes = _managed_hashes(receipt)
        drift: list[str] = []
        for relative, expected in sorted(hashes.items()):
            path = root_view_path(root, relative)
            actual = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None
            if actual != expected:
                drift.append(relative)
    except (OSError, ReadinessConfigurationError) as exc:
        return _result(STRUCTURAL_CHECK_IDS[1], "FAIL", f"managed integrity could not be established: {exc}")
    if drift:
        return _result(STRUCTURAL_CHECK_IDS[1], "FAIL", "managed asset drift: " + ", ".join(drift))
    return _result(STRUCTURAL_CHECK_IDS[1], "PASS", "all receipt-managed assets match")


def _identity_fields(identity: object) -> Mapping[str, object]:
    fields = getattr(identity, "fields", None)
    if not isinstance(fields, Mapping):
        raise ReadinessConfigurationError("confirmed host identity fields are missing")
    return fields


def _check_identity(root: Path, bundle: object, identity: object, receipt: object) -> CheckResult:
    del bundle, receipt
    try:
        fields = _identity_fields(identity)
        for name, field in fields.items():
            if getattr(field, "ambiguity", None) != "none" or not getattr(field, "confirmed_by", None):
                raise ReadinessConfigurationError(f"host identity field {name} is not confirmed")
        required = (
            root_view_path(root, "project.config.json"),
            root_view_path(root, ".github/copilot-instructions.md"),
        )
        if any(not path.is_file() for path in required):
            raise ReadinessConfigurationError("host config or Copilot instructions are missing")
    except ReadinessConfigurationError as exc:
        return _result(STRUCTURAL_CHECK_IDS[2], "FAIL", str(exc))
    return _result(STRUCTURAL_CHECK_IDS[2], "PASS", "identity, host config, and Copilot instructions are confirmed")


def _check_constitution(root: Path, bundle: object, identity: object, receipt: object) -> CheckResult:
    del bundle, identity, receipt
    missing = [
        name
        for name in CONSTITUTION_FILES
        if not root_view_path(root, f"spec-driven-development/constitution/{name}").is_file()
    ]
    if missing:
        return _result(STRUCTURAL_CHECK_IDS[3], "FAIL", "missing constitution files: " + ", ".join(missing))
    return _result(STRUCTURAL_CHECK_IDS[3], "PASS", "all six constitution files exist")


def _check_frontmatter(root: Path, bundle: object, identity: object, receipt: object) -> CheckResult:
    del identity, receipt
    try:
        relevant = [
            str(getattr(entry, "destination"))
            for entry in _entries(bundle)
            if str(getattr(entry, "destination", "")).startswith(_FRONTMATTER_PATHS)
            and str(getattr(entry, "destination", "")).endswith((".md", ".agent.md", ".prompt.md"))
            and getattr(entry, "enabled", True)
        ]
        invalid = []
        for relative in relevant:
            path = root_view_path(root, relative)
            if not path.is_file() or not path.read_text(encoding="utf-8").startswith("---\n"):
                invalid.append(relative)
    except (OSError, UnicodeError, ReadinessConfigurationError) as exc:
        return _result(STRUCTURAL_CHECK_IDS[4], "FAIL", f"installed frontmatter could not be established: {exc}")
    if invalid:
        return _result(STRUCTURAL_CHECK_IDS[4], "FAIL", "missing installed frontmatter: " + ", ".join(invalid))
    return _result(STRUCTURAL_CHECK_IDS[4], "PASS", "installed agent, prompt, and skill frontmatter is present")


def _managed_text(root: Path, receipt: object) -> Iterable[tuple[str, str]]:
    for relative in sorted(_managed_hashes(receipt)):
        path = root_view_path(root, relative)
        if path.is_file() and path.suffix.casefold() in {".md", ".json", ".py", ".sql", ".txt"}:
            yield relative, path.read_text(encoding="utf-8")


def _managed_host_content(root: Path, receipt: object) -> Iterable[tuple[str, str]]:
    return (
        (relative, text)
        for relative, text in _managed_text(root, receipt)
        if not relative.casefold().endswith(".py")
    )


def _check_placeholders(root: Path, bundle: object, identity: object, receipt: object) -> CheckResult:
    del bundle, identity
    try:
        unresolved = [relative for relative, text in _managed_host_content(root, receipt) if _PLACEHOLDER.search(text)]
    except (OSError, UnicodeError, ReadinessConfigurationError) as exc:
        return _result(STRUCTURAL_CHECK_IDS[5], "FAIL", f"placeholder scan could not be established: {exc}")
    if unresolved:
        return _result(STRUCTURAL_CHECK_IDS[5], "FAIL", "unresolved placeholders: " + ", ".join(unresolved))
    return _result(STRUCTURAL_CHECK_IDS[5], "PASS", "no unresolved managed placeholders remain")


def _check_runtime_seed(root: Path, bundle: object, identity: object, receipt: object) -> CheckResult:
    del bundle, identity
    try:
        text_files = tuple(_managed_host_content(root, receipt))
        hits = [relative for relative, text in text_files if any(mark in text.casefold() for mark in _FORBIDDEN_FINGERPRINTS)]
        ideas = root_view_path(root, "spec-driven-development/backlog/IDEAS.md")
        backlog = root_view_path(root, "spec-driven-development/backlog/BACKLOG.md")
        if not ideas.is_file() or not backlog.is_file():
            raise ReadinessConfigurationError("positive host runtime seeds are missing")
    except (OSError, UnicodeError, ReadinessConfigurationError) as exc:
        return _result(STRUCTURAL_CHECK_IDS[6], "FAIL", str(exc))
    if hits:
        return _result(STRUCTURAL_CHECK_IDS[6], "FAIL", "forbidden framework fingerprints: " + ", ".join(hits))
    return _result(STRUCTURAL_CHECK_IDS[6], "PASS", "runtime seeds exist without forbidden framework fingerprints")


def _check_ledger(root: Path, bundle: object, identity: object, receipt: object) -> CheckResult:
    del bundle, identity
    database = root_view_path(root, "spec-driven-development/ledger/fleet.db")
    schema = root_view_path(root, "spec-driven-development/ledger/schema.sql")
    try:
        if not database.is_file() or not schema.is_file():
            raise ReadinessConfigurationError("ledger database or schema is missing")
        expected_schema = getattr(receipt, "ledger_schema_sha256", None)
        actual_schema = hashlib.sha256(schema.read_bytes()).hexdigest()
        if expected_schema is not None and expected_schema != actual_schema:
            raise ReadinessConfigurationError("ledger schema does not match the adoption receipt")
        expected_rows = getattr(receipt, "adoption_operational_rows", None)
        if expected_rows is None:
            expected_rows = getattr(receipt, "operational_rows", None)
        if expected_rows is not None and any(value != 0 for value in expected_rows.values()):
            raise ReadinessConfigurationError("adoption receipt does not record a zero-row ledger")
        with sqlite3.connect(f"file:{database.as_posix()}?mode=ro", uri=True) as connection:
            tables = {row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        if not {"dispatches", "decisions"}.issubset(tables):
            raise ReadinessConfigurationError("ledger schema is incomplete")
    except (OSError, sqlite3.Error, AttributeError, ReadinessConfigurationError) as exc:
        return _result(STRUCTURAL_CHECK_IDS[7], "FAIL", str(exc))
    return _result(STRUCTURAL_CHECK_IDS[7], "PASS", "ledger schema exists and adoption receipt records zero operational rows")


def _check_gitignore(root: Path, bundle: object, identity: object, receipt: object) -> CheckResult:
    del bundle, identity
    try:
        managed = tuple(_managed_hashes(receipt))
        host = _host_root(root)
        if not (host / ".git").exists():
            raise ReadinessConfigurationError("host Git metadata is missing")
        result = subprocess.run(
            ["git", "-C", str(host), "check-ignore", "--stdin"],
            input="".join(f"{path}\n" for path in managed),
            capture_output=True,
            text=True,
            shell=False,
            timeout=30,
        )
        ignored = tuple(line for line in result.stdout.splitlines() if line)
        if result.returncode not in {0, 1}:
            raise ReadinessConfigurationError(
                f"git check-ignore failed with return code {result.returncode}"
            )
        if ignored:
            raise ReadinessConfigurationError("managed paths are ignored: " + ", ".join(ignored))
    except (OSError, subprocess.SubprocessError, ReadinessConfigurationError) as exc:
        return _result(STRUCTURAL_CHECK_IDS[8], "FAIL", str(exc))
    return _result(STRUCTURAL_CHECK_IDS[8], "PASS", "managed files are not excluded by host ignore rules")


def _quality_commands(identity: object) -> Mapping[str, object]:
    fields = _identity_fields(identity)
    field = fields.get("quality_commands")
    if field is None or getattr(field, "ambiguity", None) != "none" or not getattr(field, "confirmed_by", None):
        raise ReadinessConfigurationError("quality command configuration is not confirmed")
    commands = getattr(field, "value", None)
    if not isinstance(commands, Mapping) or tuple(commands) != QUALITY_NAMES:
        raise ReadinessConfigurationError("quality command set is invalid")
    return commands


def _validated_quality_command(root: Path, name: str, command: object) -> tuple[list[str], Path, int]:
    if not isinstance(command, Mapping):
        raise ReadinessConfigurationError(f"quality command {name} is invalid")
    state = command.get("state")
    argv = command.get("argv")
    cwd = command.get("cwd")
    timeout = command.get("timeout_seconds")
    environment_policy = command.get("environment_policy")
    network_policy = command.get("network_policy")
    if state not in {"configured", "not-configured"}:
        raise ReadinessConfigurationError(f"quality command {name} has invalid state")
    if environment_policy != "minimal" or network_policy not in {"deny", "allow-confirmed"}:
        raise ReadinessConfigurationError(f"quality command {name} requires unsupported policy")
    if state == "not-configured":
        if argv != [] or cwd is not None or timeout is not None:
            raise ReadinessConfigurationError(f"quality command {name} has inconsistent N/A configuration")
        return [], root, 1
    if not isinstance(argv, list) or not argv or any(not isinstance(arg, str) or not arg for arg in argv):
        raise ReadinessConfigurationError(f"quality command {name} requires non-empty argv tokens")
    if isinstance(timeout, bool) or not isinstance(timeout, int) or not 1 <= timeout <= 3600:
        raise ReadinessConfigurationError(f"quality command {name} timeout must be 1..3600 seconds")
    work = _safe_path(root, cwd)
    if not work.is_dir():
        raise ReadinessConfigurationError(f"quality command {name} cwd does not exist")
    return list(argv), work, timeout


def _check_quality_tokens(root: Path, bundle: object, identity: object, receipt: object) -> CheckResult:
    del bundle, receipt
    try:
        for name, command in _quality_commands(identity).items():
            _validated_quality_command(_host_root(root), name, command)
    except ReadinessConfigurationError as exc:
        return _result(STRUCTURAL_CHECK_IDS[9], "FAIL", str(exc))
    return _result(STRUCTURAL_CHECK_IDS[9], "PASS", "confirmed quality command tokens and policies are valid")


STRUCTURAL_CHECKERS: dict[str, Callable[[Path, object, object, object], CheckResult]] = {
    "bundle-receipt-dependency-integrity": _check_bundle_receipt,
    "managed-asset-integrity": _check_managed_integrity,
    "confirmed-identity-config-instructions": _check_identity,
    "constitution-files": _check_constitution,
    "installed-source-frontmatter": _check_frontmatter,
    "unresolved-placeholders": _check_placeholders,
    "runtime-seed-forbidden-fingerprints": _check_runtime_seed,
    "ledger-schema-adoption-receipt": _check_ledger,
    "gitignore-tracked-safety": _check_gitignore,
    "quality-command-token-validity": _check_quality_tokens,
}


def _recovery_required(receipt: object) -> bool:
    if getattr(receipt, "recovery_required", False):
        return True
    return getattr(receipt, "transaction_state", None) in {"interrupted", "recovery-required"}


def run_structural_checks(
    root_view: Path | StagedRootView,
    bundle: object,
    identity: object,
    receipt: object,
    *,
    staged: bool,
) -> ReadinessReport:
    """Run exactly the portable structural profile; never run host quality."""

    root = root_view if isinstance(root_view, StagedRootView) else Path(root_view).resolve()
    checks = tuple(
        STRUCTURAL_CHECKERS[check_id](root, bundle, identity, receipt)
        for check_id in STRUCTURAL_CHECK_IDS
    ) + tuple(CheckResult(check_id, label, "N/A", "framework-only check") for check_id, label in FRAMEWORK_NA_ROWS)
    return ReadinessReport(
        SCHEMA_VERSION,
        "structural-staged" if staged else "structural-final",
        checks,
        readiness_exit_code(checks, recovery_required=_recovery_required(receipt)),
    )


def _minimal_environment() -> dict[str, str]:
    allowed = ("PATH", "PATHEXT", "SYSTEMROOT", "COMSPEC", "TEMP", "TMP", "HOME")
    return {name: os.environ[name] for name in allowed if name in os.environ}


def _redact(value: object) -> str:
    text = str(value)
    text = re.sub(
        r"(?i)(--?(?:password|passwd|token|secret|api[_-]?key))(?:\s+|=)\S+",
        r"\1 [REDACTED]",
        text,
    )
    text = re.sub(r"(?i)(?:password|passwd|token|secret|api[_-]?key)\s*[=:]\s*\S+", "[REDACTED]", text)
    return text


_BROKER_SCRIPT = (
    "import base64,json,subprocess,sys;"
    "sys.stdin.buffer.readline();"
    "argv=json.loads(base64.b64decode(sys.argv[1]));"
    "raise SystemExit(subprocess.run(argv, shell=False).returncode)"
)


@dataclass
class _ContainedProcess:
    process: subprocess.Popen[str]
    kind: str
    boundary: object
    _closed: bool = False

    def terminate_and_verify(self) -> None:
        if self._closed:
            return
        try:
            self.boundary.terminate_and_verify(self.process)
        finally:
            self._closed = True


class _WindowsJobObject:
    def __init__(self) -> None:
        import ctypes
        from ctypes import wintypes

        class BasicLimitInformation(ctypes.Structure):
            _fields_ = (
                ("PerProcessUserTimeLimit", ctypes.c_longlong),
                ("PerJobUserTimeLimit", ctypes.c_longlong),
                ("LimitFlags", wintypes.DWORD),
                ("MinimumWorkingSetSize", ctypes.c_size_t),
                ("MaximumWorkingSetSize", ctypes.c_size_t),
                ("ActiveProcessLimit", wintypes.DWORD),
                ("Affinity", ctypes.c_size_t),
                ("PriorityClass", wintypes.DWORD),
                ("SchedulingClass", wintypes.DWORD),
            )

        class IoCounters(ctypes.Structure):
            _fields_ = tuple((name, ctypes.c_ulonglong) for name in (
                "ReadOperationCount", "WriteOperationCount", "OtherOperationCount",
                "ReadTransferCount", "WriteTransferCount", "OtherTransferCount",
            ))

        class ExtendedLimitInformation(ctypes.Structure):
            _fields_ = (
                ("BasicLimitInformation", BasicLimitInformation),
                ("IoInfo", IoCounters),
                ("ProcessMemoryLimit", ctypes.c_size_t),
                ("JobMemoryLimit", ctypes.c_size_t),
                ("PeakProcessMemoryUsed", ctypes.c_size_t),
                ("PeakJobMemoryUsed", ctypes.c_size_t),
            )

        class BasicAccountingInformation(ctypes.Structure):
            _fields_ = (
                ("TotalUserTime", ctypes.c_longlong),
                ("TotalKernelTime", ctypes.c_longlong),
                ("ThisPeriodTotalUserTime", ctypes.c_longlong),
                ("ThisPeriodTotalKernelTime", ctypes.c_longlong),
                ("TotalPageFaultCount", wintypes.DWORD),
                ("TotalProcesses", wintypes.DWORD),
                ("ActiveProcesses", wintypes.DWORD),
                ("TotalTerminatedProcesses", wintypes.DWORD),
            )

        self._ctypes = ctypes
        self._kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        self._kernel32.CreateJobObjectW.argtypes = (ctypes.c_void_p, wintypes.LPCWSTR)
        self._kernel32.CreateJobObjectW.restype = wintypes.HANDLE
        self._kernel32.SetInformationJobObject.argtypes = (
            wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD
        )
        self._kernel32.SetInformationJobObject.restype = wintypes.BOOL
        self._kernel32.AssignProcessToJobObject.argtypes = (wintypes.HANDLE, wintypes.HANDLE)
        self._kernel32.AssignProcessToJobObject.restype = wintypes.BOOL
        self._kernel32.QueryInformationJobObject.argtypes = (
            wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD,
            ctypes.POINTER(wintypes.DWORD),
        )
        self._kernel32.QueryInformationJobObject.restype = wintypes.BOOL
        self._kernel32.TerminateJobObject.argtypes = (wintypes.HANDLE, wintypes.UINT)
        self._kernel32.TerminateJobObject.restype = wintypes.BOOL
        self._kernel32.CloseHandle.argtypes = (wintypes.HANDLE,)
        self._kernel32.CloseHandle.restype = wintypes.BOOL
        self._accounting_type = BasicAccountingInformation
        self._handle = self._kernel32.CreateJobObjectW(None, None)
        if not self._handle:
            raise ContainmentUnavailableError(ctypes.get_last_error(), "Windows Job Object creation failed")
        limits = ExtendedLimitInformation()
        limits.BasicLimitInformation.LimitFlags = 0x00002000
        if not self._kernel32.SetInformationJobObject(
            self._handle, 9, ctypes.byref(limits), ctypes.sizeof(limits)
        ):
            error = ctypes.get_last_error()
            self._kernel32.CloseHandle(self._handle)
            self._handle = None
            raise ContainmentUnavailableError(error, "Windows Job Object configuration failed")

    def assign(self, process: subprocess.Popen[str]) -> None:
        if not self._kernel32.AssignProcessToJobObject(self._handle, int(process._handle)):
            raise ContainmentUnavailableError(
                self._ctypes.get_last_error(), "quality process could not enter a Windows Job Object"
            )

    def _active_processes(self) -> int:
        accounting = self._accounting_type()
        if not self._kernel32.QueryInformationJobObject(
            self._handle, 1, self._ctypes.byref(accounting), self._ctypes.sizeof(accounting), None
        ):
            raise RuntimeError("Windows Job Object termination could not be verified")
        return int(accounting.ActiveProcesses)

    def terminate_and_verify(self, process: subprocess.Popen[str]) -> None:
        try:
            if not self._kernel32.TerminateJobObject(self._handle, 1):
                raise RuntimeError("Windows Job Object could not be terminated")
            try:
                process.communicate(timeout=5)
            except (OSError, subprocess.SubprocessError, ValueError):
                pass
            if self._active_processes() != 0:
                raise RuntimeError("Windows Job Object descendants remain active")
        finally:
            if self._handle:
                self._kernel32.CloseHandle(self._handle)
                self._handle = None


def _spawn_contained_process(
    argv: Sequence[str], cwd: Path, environment: Mapping[str, str]
) -> _ContainedProcess:
    if os.name != "nt":
        raise ContainmentUnavailableError(
            "quality process containment is only available on Windows"
        )
    encoded_argv = base64.b64encode(json.dumps(list(argv)).encode("utf-8")).decode("ascii")
    boundary = _WindowsJobObject()
    options: dict[str, object] = {
        "cwd": cwd,
        "env": dict(environment),
        "shell": False,
        "stdin": subprocess.PIPE,
        "stdout": subprocess.PIPE,
        "stderr": subprocess.PIPE,
        "text": True,
    }
    process = subprocess.Popen(
        [sys.executable, "-c", _BROKER_SCRIPT, encoded_argv], **options
    )
    try:
        boundary.assign(process)
        if process.stdin is None:
            raise ContainmentUnavailableError("quality containment broker has no control pipe")
        process.stdin.write("start\n")
        process.stdin.flush()
        process.stdin.close()
        process.stdin = None
        return _ContainedProcess(
            process,
            "windows-job-object",
            boundary,
        )
    except Exception:
        try:
            boundary.terminate_and_verify(process)
        finally:
            if process.poll() is None:
                process.kill()
        raise


def _terminate_process_tree(contained: _ContainedProcess) -> None:
    contained.terminate_and_verify()


def _execute_quality_command(
    argv: Sequence[str], cwd: Path, timeout: int, environment: Mapping[str, str]
) -> SimpleNamespace:
    contained = _spawn_contained_process(argv, cwd, environment)
    process = contained.process
    try:
        stdout, stderr = process.communicate(timeout=timeout)
        return_code = process.returncode
    except subprocess.TimeoutExpired:
        _terminate_process_tree(contained)
        return SimpleNamespace(returncode=124, stdout="", stderr="quality command timed out")
    _terminate_process_tree(contained)
    return SimpleNamespace(returncode=return_code, stdout=stdout, stderr=stderr)


def run_quality_checks(
    root: Path,
    identity: object,
    disclosure_sink: Callable[[str], None],
) -> ReadinessReport:
    """Run explicitly configured quality commands with no shell and no rollback claim."""

    resolved_root = Path(root).resolve()
    checks: list[CheckResult] = []
    for name, command in _quality_commands(identity).items():
        argv, cwd, timeout = _validated_quality_command(resolved_root, name, command)
        check_id = f"quality-{name}"
        if command["state"] == "not-configured":
            checks.append(CheckResult(check_id, f"quality {name}", "N/A", "confirmed not-configured"))
            continue
        if command["network_policy"] == "deny":
            raise ReadinessConfigurationError(
                f"quality command {name} network deny cannot be enforced by this executor"
            )
        disclosure_sink(
            f"quality {name}: cwd={cwd}; argv=[redacted]; timeout={timeout}s; "
            "environment=minimal; network=allow-confirmed; filesystem and external side effects are outside rollback"
        )
        try:
            completed = _execute_quality_command(argv, cwd, timeout, _minimal_environment())
        except (OSError, subprocess.SubprocessError) as exc:
            checks.append(CheckResult(check_id, f"quality {name}", "FAIL", _redact(exc)))
            continue
        detail = _redact((completed.stderr or completed.stdout or "command completed").strip())
        status = "PASS" if completed.returncode == 0 else "FAIL"
        checks.append(CheckResult(check_id, f"quality {name}", status, detail))
    frozen = tuple(checks)
    return ReadinessReport(SCHEMA_VERSION, "quality", frozen, readiness_exit_code(frozen))


def format_readiness_summary(report: ReadinessReport, *, installed: bool) -> str:
    """Return bounded wording that cannot be confused with framework health."""

    prefix = "installed; " if installed else ""
    if report.exit_code == 0:
        return prefix + "host readiness PASS"
    if report.exit_code == 3:
        return prefix + "host recovery required"
    if report.exit_code == 2:
        return prefix + "host configuration invalid"
    return prefix + "host checks failed"


def _namespace(value: object) -> object:
    if isinstance(value, dict):
        return SimpleNamespace(**{key: _namespace(item) for key, item in value.items()})
    if isinstance(value, list):
        return tuple(_namespace(item) for item in value)
    return value


def _load_json(path: Path, label: str) -> object:
    try:
        return _namespace(json.loads(path.read_text(encoding="utf-8")))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ReadinessConfigurationError(f"host readiness {label} is invalid: {exc}") from None


def _load_identity(path: Path) -> object:
    try:
        from brownfield_identity import load_identity

        return load_identity(path)
    except (ImportError, ValueError, OSError, TypeError) as exc:
        raise ReadinessConfigurationError(f"host readiness identity is invalid: {exc}") from None


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run bounded host readiness checks (not framework health).")
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Installed host root.")
    parser.add_argument("--identity", type=Path, required=True, help="Confirmed host identity JSON.")
    parser.add_argument("--bundle", type=Path, help="Installed bundle manifest JSON.")
    parser.add_argument("--receipt", type=Path, help="Installed adoption receipt JSON.")
    parser.add_argument("--run-quality", action="store_true", help="Explicitly run configured host quality commands.")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the distinct host-doctor entry point and return its public exit code."""

    parser = _parser()
    try:
        args = parser.parse_args(argv)
        root = args.root.resolve()
        identity = _load_identity(args.identity)
        if args.run_quality:
            report = run_quality_checks(root, identity, lambda text: print(text, file=sys.stderr))
        else:
            bundle_path = args.bundle or root / "spec-driven-development" / ".adoption" / "bundle-manifest.json"
            receipt_path = args.receipt or root / "spec-driven-development" / ".adoption" / "receipt.json"
            report = run_structural_checks(
                root,
                _load_json(bundle_path, "bundle manifest"),
                identity,
                _load_json(receipt_path, "adoption receipt"),
                staged=False,
            )
    except ReadinessConfigurationError as exc:
        print(f"host readiness configuration error: {exc}", file=sys.stderr)
        return 2
    for check in report.checks:
        print(f"[{check.status}] {check.label}: {check.detail}")
    print(format_readiness_summary(report, installed=True))
    return report.exit_code


if __name__ == "__main__":
    raise SystemExit(main())
