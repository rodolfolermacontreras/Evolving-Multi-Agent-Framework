"""Host identity validation, sanitization, and deterministic rendering.

This module is the executable form of ADR-026 Appendix B.  It is deliberately
stdlib-only and creates immutable value objects only after untrusted input has
been validated and remote credentials have been excluded.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import date, datetime, timezone
import hashlib
import json
from pathlib import PurePosixPath
import re
from typing import Any, Mapping, Sequence
from urllib.parse import urlsplit, urlunsplit


FIELD_ORDER = (
    "project_name",
    "repo_url",
    "default_branch",
    "owner",
    "team",
    "mission",
    "article_xi_cutover",
    "stack",
    "quality_commands",
    "branch_convention",
    "commit_convention",
    "source_documents",
    "approval_boundaries",
    "worktree_profile",
)
RENDERER_ORDER = (
    "project_config",
    "copilot_instructions",
    "constitution",
    "rosters",
    "seeds",
)
PROJECT_CONFIG_ORDER = (
    "schema_version",
    "project_name",
    "repo_url",
    "default_branch",
    "owner",
    "team",
    "article_xi_cutover",
    "quality_commands",
    "branch_convention",
    "commit_convention",
    "approval_boundaries",
)
QUALITY_ORDER = ("test", "lint", "typecheck", "build")
FIELD_MEMBERS = (
    "value",
    "classification",
    "evidence_paths",
    "ambiguity",
    "confidence",
    "confirmed_by",
    "confirmed_at",
)
QUALITY_MEMBERS = (
    "state",
    "argv",
    "cwd",
    "timeout_seconds",
    "environment_policy",
    "network_policy",
)
_CLASSIFICATIONS = {"evidence", "default", "human"}
_AMBIGUITIES = {"none", "multiple", "missing", "conflict"}
_ALLOWED_CLASSIFICATIONS = {
    "project_name": {"evidence", "human"},
    "repo_url": {"evidence", "human"},
    "default_branch": {"evidence", "human"},
    "owner": {"human"},
    "team": {"human"},
    "mission": {"human"},
    "article_xi_cutover": {"default", "human"},
    "stack": {"evidence", "human"},
    "quality_commands": {"human"},
    "branch_convention": {"evidence", "human"},
    "commit_convention": {"evidence", "human"},
    "source_documents": {"evidence", "human"},
    "approval_boundaries": {"human"},
    "worktree_profile": {"human"},
}
_SECRET_EXPANSION = re.compile(r"(?:\$\{[^}]+\}|%[^%]+%)")
_SECRET_ASSIGNMENT = re.compile(r"(?i)(?:password|passwd|token|secret|api[_-]?key)\s*[=:]")
_SECRET_FLAG = re.compile(r"(?i)^--?(?:password|passwd|token|secret|api[_-]?key)$")
_TOKEN = re.compile(r"\{\{([A-Z][A-Z0-9_]*)\}\}")
_FULL_SHA = re.compile(r"[0-9a-f]{40}")
_DATE = re.compile(r"\d{4}-\d{2}-\d{2}")
_SCP_REMOTE = re.compile(r"(?P<user>[^@/:]+)@(?P<host>[^/:]+):(?P<path>.+)")


class IdentityError(ValueError):
    """Base class for safe host-identity errors."""


class IdentityValidationError(IdentityError):
    """The identity does not conform to Appendix B."""


class IdentityConfirmationError(IdentityError):
    """A required host decision has not been confirmed."""


class RemoteSanitizationError(IdentityValidationError):
    """A remote cannot be safely normalized without owner confirmation."""


class TemplateSubstitutionError(IdentityValidationError):
    """A bounded renderer template violates its token contract."""


@dataclass(frozen=True)
class IdentityField:
    value: Any
    classification: str
    evidence_paths: tuple[str, ...]
    ambiguity: str
    confidence: float | None
    confirmed_by: str | None
    confirmed_at: str | None


@dataclass(frozen=True)
class HostIdentityManifest:
    schema_version: str
    generated_at: str
    target_head: str
    fields: dict[str, IdentityField]
    renderers: dict[str, str]


@dataclass(frozen=True)
class SanitizedRemote:
    value: str
    requires_confirmation: bool


@dataclass(frozen=True)
class IdentityInputOwnership:
    classification: str
    action: str
    requires_preview_approval: bool
    requires_backup: bool
    content_hash: str


def _fail(subject: str, detail: str = "is invalid") -> None:
    raise IdentityValidationError(f"host identity {subject} {detail}; review and confirm it")


def _is_nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _safe_string(value: str, subject: str) -> None:
    if _SECRET_EXPANSION.search(value) or _SECRET_ASSIGNMENT.search(value):
        _fail(subject, "contains disallowed secret-like input")
    if "\x00" in value or "\r" in value:
        _fail(subject)


def _utc_timestamp(value: Any, subject: str, *, nullable: bool = False) -> None:
    if value is None and nullable:
        return
    if not isinstance(value, str) or not value.endswith("Z"):
        _fail(subject, "must be a UTC ISO-8601 timestamp")
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError:
        _fail(subject, "must be a UTC ISO-8601 timestamp")
    if parsed.tzinfo != timezone.utc:
        _fail(subject, "must be a UTC ISO-8601 timestamp")


def _posix_relative(value: Any, subject: str, *, dot_allowed: bool = False) -> bool:
    if not _is_nonempty_string(value) or "\\" in value:
        return False
    if value == ".":
        return dot_allowed
    path = PurePosixPath(value)
    return not path.is_absolute() and ".." not in path.parts and value == path.as_posix()


def _string_array(
    value: Any,
    subject: str,
    *,
    nonempty: bool = False,
    paths: bool = False,
) -> None:
    if not isinstance(value, list) or (nonempty and not value):
        _fail(subject, "must be a sorted string array")
    if any(not _is_nonempty_string(item) for item in value):
        _fail(subject, "must be a sorted string array")
    if value != sorted(value) or len(value) != len(set(value)):
        _fail(subject, "must be sorted and unique")
    for item in value:
        _safe_string(item, subject)
        if paths and not _posix_relative(item, subject):
            _fail(subject, "must contain POSIX-relative paths")


def _validate_quality_commands(value: Any) -> None:
    if not isinstance(value, dict) or tuple(value) != QUALITY_ORDER:
        _fail("quality_commands", "must contain the exact ordered command set")
    for name, command in value.items():
        if not isinstance(command, dict) or tuple(command) != QUALITY_MEMBERS:
            _fail(f"quality_commands.{name}", "has an invalid command schema")
        state = command["state"]
        argv = command["argv"]
        cwd = command["cwd"]
        timeout = command["timeout_seconds"]
        if state not in {"configured", "not-configured"}:
            _fail(f"quality_commands.{name}.state")
        if not isinstance(argv, list) or any(not _is_nonempty_string(arg) for arg in argv):
            _fail(f"quality_commands.{name}.argv")
        for arg in argv:
            _safe_string(arg, f"quality_commands.{name}.argv")
        if any(_SECRET_FLAG.fullmatch(arg) for arg in argv):
            _fail(f"quality_commands.{name}.argv", "contains a disallowed credential flag")
        if cwd is not None and not _posix_relative(cwd, f"quality_commands.{name}.cwd", dot_allowed=True):
            _fail(f"quality_commands.{name}.cwd")
        if timeout is not None and (
            isinstance(timeout, bool) or not isinstance(timeout, int) or not 1 <= timeout <= 3600
        ):
            _fail(f"quality_commands.{name}.timeout_seconds")
        if command["environment_policy"] not in {"minimal", "inherit-confirmed"}:
            _fail(f"quality_commands.{name}.environment_policy")
        if command["network_policy"] not in {"deny", "allow-confirmed"}:
            _fail(f"quality_commands.{name}.network_policy")
        if state == "configured" and (not argv or cwd is None or timeout is None):
            _fail(f"quality_commands.{name}", "is incomplete for configured state")
        if state == "not-configured" and (argv or cwd is not None or timeout is not None):
            _fail(f"quality_commands.{name}", "is inconsistent with not-configured state")


def sanitize_remote(raw: str) -> SanitizedRemote:
    """Normalize a remote without retaining raw credentials in any result."""

    if not _is_nonempty_string(raw) or _SECRET_EXPANSION.search(raw):
        raise RemoteSanitizationError(
            "remote requires a sanitized value and explicit owner confirmation"
        )
    candidate = raw.strip()
    scp = _SCP_REMOTE.fullmatch(candidate)
    if scp:
        if scp.group("user") != "git":
            raise RemoteSanitizationError(
                "remote uses a nonstandard SSH identity; sanitize and confirm it"
            )
        if not scp.group("path"):
            raise RemoteSanitizationError("remote is incomplete; sanitize and confirm it")
        return SanitizedRemote(candidate, False)

    try:
        parsed = urlsplit(candidate)
    except ValueError:
        raise RemoteSanitizationError("remote is malformed; sanitize and confirm it") from None
    if parsed.scheme not in {"http", "https", "ssh"} or not parsed.hostname:
        raise RemoteSanitizationError("remote is ambiguous; sanitize and confirm it")

    requires_confirmation = bool(parsed.query or parsed.fragment)
    if parsed.scheme == "ssh":
        if parsed.password is not None or parsed.username not in {None, "git"}:
            raise RemoteSanitizationError(
                "remote SSH identity is ambiguous; sanitize and confirm it"
            )
        netloc = f"git@{parsed.hostname}" if parsed.username == "git" else parsed.hostname
        if parsed.port is not None:
            netloc += f":{parsed.port}"
    else:
        requires_confirmation = requires_confirmation or parsed.username is not None
        netloc = parsed.hostname
        if parsed.port is not None:
            netloc += f":{parsed.port}"
    clean = urlunsplit((parsed.scheme, netloc, parsed.path, "", ""))
    return SanitizedRemote(clean, requires_confirmation)


def _validate_field_value(name: str, field: IdentityField) -> None:
    value = field.value
    if name in {
        "project_name", "default_branch", "owner", "mission",
        "branch_convention", "commit_convention",
    }:
        if not _is_nonempty_string(value):
            _fail(name, "must be a non-empty string")
        _safe_string(value, name)
    elif name in {"repo_url", "team"}:
        if value is not None and not _is_nonempty_string(value):
            _fail(name, "must be a non-empty string or null")
        if isinstance(value, str):
            _safe_string(value, name)
        if name == "repo_url" and value is not None:
            sanitized = sanitize_remote(value)
            if sanitized.value != value or sanitized.requires_confirmation:
                _fail(name, "must already contain its confirmed sanitized value")
    elif name == "article_xi_cutover":
        if not isinstance(value, str) or not _DATE.fullmatch(value):
            _fail(name, "must use YYYY-MM-DD")
        try:
            date.fromisoformat(value)
        except ValueError:
            _fail(name, "must be a calendar date")
    elif name == "stack":
        if not isinstance(value, list) or any(not _is_nonempty_string(item) for item in value):
            _fail(name, "must be a canonical string array")
        if len(value) != len(set(value)):
            _fail(name, "must be unique")
        technology_order = {
            "express": 0,
            "node": 1,
            "python": 0,
            "pytest": 1,
        }
        primary_first = sorted(
            value,
            key=lambda item: (technology_order.get(item, 2), item),
        )
        if value != primary_first:
            _fail(name, "must place the primary runtime before sorted tooling")
        for item in value:
            _safe_string(item, name)
    elif name == "quality_commands":
        _validate_quality_commands(value)
    elif name == "source_documents":
        _string_array(value, name, paths=True)
    elif name == "approval_boundaries":
        _string_array(value, name, nonempty=True)
    elif name == "worktree_profile":
        if not isinstance(value, bool):
            _fail(name, "must be boolean")


def validate_identity(manifest: HostIdentityManifest) -> HostIdentityManifest:
    """Validate the exact immutable Appendix B schema and confirmation rules."""

    if not isinstance(manifest, HostIdentityManifest):
        _fail("manifest", "has the wrong object type")
    if manifest.schema_version != "1":
        _fail("schema_version", "must be version 1")
    _utc_timestamp(manifest.generated_at, "generated_at")
    if not isinstance(manifest.target_head, str) or not _FULL_SHA.fullmatch(manifest.target_head):
        _fail("target_head", "must be a full lowercase commit SHA")
    if not isinstance(manifest.fields, dict) or tuple(manifest.fields) != FIELD_ORDER:
        _fail("fields", "must contain the exact ordered field set")
    if not isinstance(manifest.renderers, dict) or tuple(manifest.renderers) != RENDERER_ORDER:
        _fail("renderers", "must contain the exact renderer registry")
    if any(not _is_nonempty_string(version) for version in manifest.renderers.values()):
        _fail("renderers", "must use non-empty explicit versions")

    for name, field in manifest.fields.items():
        if not isinstance(field, IdentityField):
            _fail(name, "has the wrong field type")
        if field.classification not in _CLASSIFICATIONS or field.classification not in _ALLOWED_CLASSIFICATIONS[name]:
            _fail(name, "has an invalid classification")
        if not isinstance(field.evidence_paths, tuple):
            _fail(name, "has invalid evidence paths")
        paths = list(field.evidence_paths)
        _string_array(paths, f"{name}.evidence_paths", paths=True)
        if field.classification == "evidence" and not paths:
            _fail(name, "requires evidence paths")
        if field.classification != "evidence" and paths:
            _fail(name, "must not claim evidence paths")
        if field.ambiguity not in _AMBIGUITIES:
            _fail(name, "has invalid ambiguity")
        if field.confidence is not None and (
            isinstance(field.confidence, bool)
            or not isinstance(field.confidence, (int, float))
            or not 0 <= field.confidence <= 1
        ):
            _fail(name, "has invalid confidence")
        if field.classification == "human" and field.confidence is not None:
            _fail(name, "human values require null confidence")
        if field.classification != "human" and field.confidence is None:
            _fail(name, "derived values require confidence")
        if field.confirmed_by is not None and not _is_nonempty_string(field.confirmed_by):
            _fail(name, "has invalid confirmer")
        _utc_timestamp(field.confirmed_at, f"{name}.confirmed_at", nullable=True)
        if (field.confirmed_by is None) != (field.confirmed_at is None):
            _fail(name, "has incomplete confirmation metadata")
        _validate_field_value(name, field)
        if field.ambiguity != "none":
            raise IdentityConfirmationError(
                f"host identity {name} has unresolved ambiguity; review and confirm it"
            )
        if field.confirmed_by is None:
            raise IdentityConfirmationError(
                f"host identity {name} is unconfirmed; supply and confirm the host decision"
            )
    return manifest


def _parse_field(name: str, raw: Any) -> IdentityField:
    if not isinstance(raw, dict) or tuple(raw) != FIELD_MEMBERS:
        _fail(name, "has an invalid field schema")
    evidence = raw["evidence_paths"]
    if not isinstance(evidence, list):
        _fail(name, "has invalid evidence paths")
    return IdentityField(
        value=raw["value"],
        classification=raw["classification"],
        evidence_paths=tuple(evidence),
        ambiguity=raw["ambiguity"],
        confidence=raw["confidence"],
        confirmed_by=raw["confirmed_by"],
        confirmed_at=raw["confirmed_at"],
    )


def load_identity(path: Any) -> HostIdentityManifest:
    """Load JSON into validated objects without exposing source paths in errors."""

    try:
        with open(path, "r", encoding="utf-8", newline="") as stream:
            raw = json.load(stream)
    except (OSError, UnicodeError, json.JSONDecodeError):
        raise IdentityValidationError(
            "host identity file is unreadable or malformed; review and regenerate it"
        ) from None
    expected = ("schema_version", "generated_at", "target_head", "fields", "renderers")
    if not isinstance(raw, dict) or tuple(raw) != expected:
        _fail("manifest", "must contain the exact ordered top-level members")
    if not isinstance(raw["fields"], dict) or tuple(raw["fields"]) != FIELD_ORDER:
        _fail("fields", "must contain the exact ordered field set")
    if not isinstance(raw["renderers"], dict):
        _fail("renderers")
    manifest = HostIdentityManifest(
        schema_version=raw["schema_version"],
        generated_at=raw["generated_at"],
        target_head=raw["target_head"],
        fields={name: _parse_field(name, value) for name, value in raw["fields"].items()},
        renderers=dict(raw["renderers"]),
    )
    return validate_identity(manifest)


def confirm_identity(
    manifest: HostIdentityManifest,
    confirmations: Mapping[str, Mapping[str, Any]],
) -> HostIdentityManifest:
    """Return a newly confirmed manifest; the input manifest is never mutated."""

    unknown = set(confirmations) - set(FIELD_ORDER)
    if unknown:
        _fail("confirmations", "contains unknown fields")
    fields = dict(manifest.fields)
    for name, confirmation in confirmations.items():
        if not isinstance(confirmation, Mapping):
            _fail(name, "has invalid confirmation data")
        allowed = {"value", "confirmed_by", "confirmed_at", "ambiguity", "classification", "confidence", "evidence_paths"}
        if set(confirmation) - allowed:
            _fail(name, "has unknown confirmation members")
        updates = dict(confirmation)
        if "evidence_paths" in updates:
            if not isinstance(updates["evidence_paths"], (list, tuple)):
                _fail(name, "has invalid evidence paths")
            updates["evidence_paths"] = tuple(updates["evidence_paths"])
        fields[name] = replace(fields[name], **updates)
    return validate_identity(replace(manifest, fields=fields))


def draft_identity(evidence: Mapping[str, Any], adoption_date: str) -> HostIdentityManifest:
    """Draft an unconfirmed manifest from approved evidence and one safe date default."""

    if not _DATE.fullmatch(adoption_date):
        _fail("article_xi_cutover", "must use YYYY-MM-DD")
    now = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    fields: dict[str, IdentityField] = {}
    for name in FIELD_ORDER:
        item = evidence.get(name, {})
        if not isinstance(item, Mapping):
            _fail(name, "has invalid evidence")
        if name == "article_xi_cutover" and not item:
            fields[name] = IdentityField(adoption_date, "default", (), "none", 1.0, None, None)
            continue
        value = item.get("value")
        paths = item.get("evidence_paths", ())
        fields[name] = IdentityField(
            value=value,
            classification=item.get("classification", "evidence"),
            evidence_paths=tuple(paths),
            ambiguity=item.get("ambiguity", "missing" if value is None else "none"),
            confidence=item.get("confidence", 1.0),
            confirmed_by=None,
            confirmed_at=None,
        )
    return HostIdentityManifest(
        "1", now, str(evidence.get("target_head", "")), fields,
        {name: "1" for name in RENDERER_ORDER},
    )


def _json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, separators=(",", ":")) + "\n").encode("utf-8")


def render_project_config(identity: HostIdentityManifest) -> bytes:
    validate_identity(identity)
    config = {
        key: identity.schema_version if key == "schema_version" else identity.fields[key].value
        for key in PROJECT_CONFIG_ORDER
    }
    return _json_bytes(config)


def _command_text(command: Mapping[str, Any]) -> str:
    return " ".join(command["argv"]) if command["state"] == "configured" else "not configured"


def _clean_rendered(outputs: Mapping[str, bytes]) -> dict[str, bytes]:
    clean: dict[str, bytes] = {}
    for path, data in outputs.items():
        if not _posix_relative(path, "renderer path"):
            _fail("renderer path")
        try:
            text = bytes(data).decode("utf-8").replace("\r\n", "\n").replace("\r", "\n")
        except (TypeError, UnicodeError):
            _fail("renderer output", "must be UTF-8")
        if not text.endswith("\n"):
            text += "\n"
        if "{{" in text or "}}" in text or "TODO" in text or _SECRET_EXPANSION.search(text) or _SECRET_ASSIGNMENT.search(text):
            _fail("renderer output", "contains unresolved or secret-like content")
        clean[path] = text.encode("utf-8")
    return clean


def render_copilot_instructions(identity: HostIdentityManifest) -> bytes:
    validate_identity(identity)
    field = identity.fields
    team = field["team"].value or "No team assigned"
    docs = ", ".join(field["source_documents"].value)
    stack = ", ".join(field["stack"].value)
    quality = "\n".join(
        f"- {name}: {_command_text(field['quality_commands'].value[name])}"
        for name in QUALITY_ORDER
    )
    approvals = "\n".join(f"- {item}" for item in field["approval_boundaries"].value)
    text = f"""# Copilot instructions for {field['project_name'].value}

## Host identity

- Owner: {field['owner'].value}
- Team: {team}
- Mission: {field['mission'].value}
- Default branch: {field['default_branch'].value}
- Stack: {stack}
- Source documents: {docs}

## Development conventions

- Branches: {field['branch_convention'].value}
- Commits: {field['commit_convention'].value}

## Quality commands

{quality}

## Approval boundaries

{approvals}
"""
    return _clean_rendered({".github/copilot-instructions.md": text.encode("utf-8")})[
        ".github/copilot-instructions.md"
    ]


def render_constitution(
    identity: HostIdentityManifest,
    reviewed_proposal: Mapping[str, bytes | str],
) -> dict[str, bytes]:
    validate_identity(identity)
    field = identity.fields
    outputs: dict[str, bytes] = {}
    for name in sorted(reviewed_proposal):
        if PurePosixPath(name).name != name or not name.endswith(".md"):
            _fail("constitution proposal path")
        value = reviewed_proposal[name]
        outputs[f"spec-driven-development/constitution/{name}"] = (
            value if isinstance(value, bytes) else value.encode("utf-8")
        )
    governance = f"""# Host governance

Project: {field['project_name'].value}
Owner: {field['owner'].value}
Mission: {field['mission'].value}
Default branch: {field['default_branch'].value}
Article XI cutover: {field['article_xi_cutover'].value}
Source documents: {', '.join(field['source_documents'].value)}
"""
    outputs["spec-driven-development/constitution/host-governance.md"] = governance.encode("utf-8")
    return _clean_rendered(outputs)


def render_rosters(identity: HostIdentityManifest, bundle: Any) -> dict[str, bytes]:
    validate_identity(identity)
    outputs: dict[str, bytes] = {}
    for plural in ("agents", "skills", "prompts"):
        values = getattr(bundle, plural, None)
        if not isinstance(values, Sequence) or isinstance(values, (str, bytes)):
            _fail(f"rosters.{plural}")
        items = list(values)
        if any(not _is_nonempty_string(item) for item in items) or len(items) != len(set(items)):
            _fail(f"rosters.{plural}", "must be a unique string sequence")
        payload = {
            "schema_version": "1",
            "project_name": identity.fields["project_name"].value,
            plural: items,
        }
        outputs[f"spec-driven-development/roster/{plural}.json"] = _json_bytes(payload)
    return _clean_rendered(outputs)


def render_seeds(identity: HostIdentityManifest) -> dict[str, bytes]:
    validate_identity(identity)
    field = identity.fields
    ideas = f"""# Ideas

Seed for {field['project_name'].value}.
Mission: {field['mission'].value}
Owner: {field['owner'].value}
Source documents: {', '.join(field['source_documents'].value)}
"""
    backlog = f"""# Backlog

Project: {field['project_name'].value}
Default branch: {field['default_branch'].value}
Stack: {', '.join(field['stack'].value)}
No backlog items have been approved.
"""
    return _clean_rendered({
        "spec-driven-development/backlog/IDEAS.md": ideas.encode("utf-8"),
        "spec-driven-development/backlog/BACKLOG.md": backlog.encode("utf-8"),
    })


def substitute_bounded_tokens(
    template: str,
    values: Mapping[str, str],
    *,
    allowed_tokens: Sequence[str],
) -> str:
    """Replace only exact registered tokens, rejecting drift in either direction."""

    if not isinstance(template, str):
        raise TemplateSubstitutionError("renderer template must be text")
    allowed = tuple(allowed_tokens)
    if len(allowed) != len(set(allowed)) or any(not re.fullmatch(r"[A-Z][A-Z0-9_]*", item) for item in allowed):
        raise TemplateSubstitutionError("renderer token registry is invalid")
    found = _TOKEN.findall(template)
    residue = _TOKEN.sub("", template)
    if "{{" in residue or "}}" in residue:
        raise TemplateSubstitutionError("renderer template contains malformed tokens")
    found_set = set(found)
    if not found_set <= set(allowed):
        raise TemplateSubstitutionError("renderer template contains an unknown required token")
    if set(values) != found_set or any(token not in allowed for token in values):
        raise TemplateSubstitutionError("renderer values do not exactly match used registered tokens")
    if any(not isinstance(value, str) for value in values.values()):
        raise TemplateSubstitutionError("renderer token values must be text")
    return _TOKEN.sub(lambda match: values[match.group(1)], template)


def classify_existing_identity_inputs(
    existing: Mapping[str, bytes],
    *,
    managed_hashes: Mapping[str, str],
) -> dict[str, IdentityInputOwnership]:
    """Classify immutable byte inputs without retaining or disclosing their content."""

    result: dict[str, IdentityInputOwnership] = {}
    for path, content in existing.items():
        if not _posix_relative(path, "identity input path") or not isinstance(content, bytes):
            _fail("identity input")
        digest = hashlib.sha256(content).hexdigest()
        managed = managed_hashes.get(path) == digest
        result[path] = IdentityInputOwnership(
            classification="managed" if managed else "host-owned",
            action="replace" if managed else "preserve",
            requires_preview_approval=True,
            requires_backup=True,
            content_hash=digest,
        )
    return result
