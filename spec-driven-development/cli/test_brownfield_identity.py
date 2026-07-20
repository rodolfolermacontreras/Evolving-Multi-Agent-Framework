"""RED-3B host identity, sanitization, and deterministic renderer contract.

The tests are stdlib-only apart from pytest and write exclusively below ``tmp_path``.
They intentionally describe the production API approved by ADR-026 Appendix B.
"""

from __future__ import annotations

import copy
import importlib
import json
import re
import sys
from dataclasses import fields as dataclass_fields
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

CLI_DIR = Path(__file__).resolve().parent
if str(CLI_DIR) not in sys.path:
    sys.path.insert(0, str(CLI_DIR))

from brownfield_test_fixtures import (  # noqa: E402
    build_node_express_fixture,
    build_python_fixture,
    create_disposable_root,
    snapshot_paths,
)

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
RENDERER_ORDER = (
    "project_config",
    "copilot_instructions",
    "constitution",
    "rosters",
    "seeds",
)
QUALITY_ORDER = ("test", "lint", "typecheck", "build")
SECRET_CANARIES = (
    "IDENTITY_PASSWORD_CANARY",
    "IDENTITY_TOKEN_CANARY",
    "SECRET_REMOTE_TOKEN",
)
FRAMEWORK_CANARIES = (
    "Evolving Multi-Agent Framework",
    "rodolfolermacontreras/Evolving-Multi-Agent-Framework",
    "PI-9",
    "Sprint 24",
    "SDD-058",
)


def _identity():
    """Import the intentionally absent identity implementation inside each test."""

    return importlib.import_module("brownfield_identity")


def _quality(*, configured: bool = True, argv: list[str] | None = None) -> dict[str, Any]:
    if configured:
        return {
            "state": "configured",
            "argv": list(argv or ["python", "-m", "pytest"]),
            "cwd": ".",
            "timeout_seconds": 300,
            "environment_policy": "minimal",
            "network_policy": "deny",
        }
    return {
        "state": "not-configured",
        "argv": [],
        "cwd": None,
        "timeout_seconds": None,
        "environment_policy": "minimal",
        "network_policy": "deny",
    }


def _field(
    value: Any,
    classification: str,
    evidence_paths: list[str],
    *,
    ambiguity: str = "none",
    confidence: float | None = 1.0,
    confirmed_by: str | None = "Host Owner",
    confirmed_at: str | None = "2026-07-12T12:00:00Z",
) -> dict[str, Any]:
    return {
        "value": value,
        "classification": classification,
        "evidence_paths": evidence_paths,
        "ambiguity": ambiguity,
        "confidence": confidence,
        "confirmed_by": confirmed_by,
        "confirmed_at": confirmed_at,
    }


def _payload(*, stack: str = "python", team: str | None = "Platform Team") -> dict[str, Any]:
    python = stack == "python"
    qualities = {
        "test": _quality(argv=["python", "-m", "pytest"])
        if python
        else _quality(argv=["npm", "test"]),
        "lint": _quality(argv=["python", "-m", "ruff", "check", "."])
        if python
        else _quality(argv=["npm", "run", "lint"]),
        "typecheck": _quality(configured=False),
        "build": _quality(configured=False),
    }
    values = {
        "project_name": _field(
            "Acme Python Library" if python else "Acme Express Service",
            "evidence",
            ["pyproject.toml"] if python else ["package.json"],
        ),
        "repo_url": _field(
            "https://example.invalid/acme/python-library.git"
            if python
            else "git@example.invalid:acme/express-service.git",
            "evidence",
            [".git/config"],
        ),
        "default_branch": _field(
            "trunk" if python else "main", "evidence", [".git/HEAD"]
        ),
        "owner": _field("Host Owner", "human", [], confidence=None),
        "team": _field(team, "human", [], confidence=None),
        "mission": _field(
            "Provide dependable reusable Python components."
            if python
            else "Serve dependable customer-facing HTTP APIs.",
            "human",
            [],
            confidence=None,
        ),
        "article_xi_cutover": _field(
            "2026-07-12", "default", [], confidence=1.0
        ),
        "stack": _field(
            ["python", "pytest"] if python else ["express", "node"],
            "evidence",
            ["pyproject.toml"] if python else ["package-lock.json", "package.json"],
        ),
        "quality_commands": _field(qualities, "human", [], confidence=None),
        "branch_convention": _field(
            "feature/<topic>", "evidence", ["CONTRIBUTING.md"]
        ),
        "commit_convention": _field(
            "type: short description", "evidence", ["CONTRIBUTING.md"]
        ),
        "source_documents": _field(
            ["CONTRIBUTING.md", "README.md"], "evidence", ["README.md"]
        ),
        "approval_boundaries": _field(
            ["Dependency changes require owner approval", "Production changes require owner approval"],
            "human",
            [],
            confidence=None,
        ),
        "worktree_profile": _field(False, "human", [], confidence=None),
    }
    return {
        "schema_version": "1",
        "generated_at": "2026-07-12T12:00:00Z",
        "target_head": "a" * 40,
        "fields": {name: values[name] for name in FIELD_ORDER},
        "renderers": {name: "1" for name in RENDERER_ORDER},
    }


def _load(tmp_path: Path, payload: dict[str, Any]):
    path = tmp_path / "host-identity.json"
    path.write_text(
        json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    identity = _identity()
    manifest = identity.load_identity(path)
    identity.validate_identity(manifest)
    return manifest


def _flatten_rendered(rendered: Any) -> dict[str, bytes]:
    if isinstance(rendered, bytes):
        return {"output": rendered}
    if isinstance(rendered, dict):
        return {
            str(path): value if isinstance(value, bytes) else str(value).encode("utf-8")
            for path, value in rendered.items()
        }
    raise AssertionError(f"renderer returned unsupported type {type(rendered).__name__}")


def _assert_clean_bytes(outputs: dict[str, bytes], tmp_path: Path) -> None:
    assert outputs
    for path, data in outputs.items():
        assert isinstance(path, str) and path and "\\" not in path
        assert isinstance(data, bytes) and data.endswith(b"\n")
        text = data.decode("utf-8")
        assert "\r" not in text
        assert "TODO" not in text
        assert not re.search(r"\{\{[A-Z][A-Z0-9_]*\}\}", text)
        assert str(tmp_path) not in text
        for canary in SECRET_CANARIES + FRAMEWORK_CANARIES:
            assert canary not in text


def test_identity_manifest_accepts_exact_appendix_b_schema_and_order(tmp_path: Path) -> None:
    manifest = _load(tmp_path, _payload())

    assert manifest.schema_version == "1"
    assert manifest.target_head == "a" * 40
    assert tuple(manifest.fields) == FIELD_ORDER
    assert tuple(manifest.renderers) == RENDERER_ORDER
    for field in manifest.fields.values():
        assert tuple(item.name for item in dataclass_fields(field)) == (
            "value",
            "classification",
            "evidence_paths",
            "ambiguity",
            "confidence",
            "confirmed_by",
            "confirmed_at",
        )


@pytest.mark.parametrize(
    ("field_name", "bad_classification"),
    (
        ("project_name", "default"),
        ("repo_url", "default"),
        ("default_branch", "default"),
        ("owner", "evidence"),
        ("team", "evidence"),
        ("mission", "evidence"),
        ("article_xi_cutover", "evidence"),
        ("stack", "default"),
        ("quality_commands", "evidence"),
        ("approval_boundaries", "evidence"),
        ("worktree_profile", "evidence"),
    ),
)
def test_identity_manifest_enforces_field_specific_classification(
    tmp_path: Path, field_name: str, bad_classification: str
) -> None:
    payload = _payload()
    payload["fields"][field_name]["classification"] = bad_classification
    identity = _identity()
    path = tmp_path / "invalid-classification.json"
    path.write_text(json.dumps(payload) + "\n", encoding="utf-8")

    with pytest.raises(identity.IdentityValidationError, match=field_name):
        identity.load_identity(path)


@pytest.mark.parametrize(
    ("path", "bad_value"),
    (
        (("schema_version",), 1),
        (("generated_at",), "2026-07-12"),
        (("target_head",), "abc123"),
        (("fields", "project_name", "value"), ""),
        (("fields", "repo_url", "value"), 7),
        (("fields", "default_branch", "value"), None),
        (("fields", "owner", "value"), ""),
        (("fields", "team", "value"), 7),
        (("fields", "mission", "value"), ""),
        (("fields", "article_xi_cutover", "value"), "07/12/2026"),
        (("fields", "stack", "value"), ["pytest", "python"]),
        (("fields", "quality_commands", "value"), []),
        (("fields", "branch_convention", "value"), ""),
        (("fields", "commit_convention", "value"), ""),
        (("fields", "source_documents", "value"), ["README.md", "CONTRIBUTING.md"]),
        (("fields", "approval_boundaries", "value"), []),
        (("fields", "worktree_profile", "value"), 1),
    ),
)
def test_identity_manifest_rejects_each_wrong_field_type_or_canonical_form(
    tmp_path: Path, path: tuple[str, ...], bad_value: Any
) -> None:
    payload = _payload()
    target: Any = payload
    for component in path[:-1]:
        target = target[component]
    target[path[-1]] = bad_value
    identity = _identity()

    candidate = tmp_path / "invalid-identity.json"
    candidate.write_text(json.dumps(payload) + "\n", encoding="utf-8")
    with pytest.raises(identity.IdentityValidationError):
        identity.load_identity(candidate)


@pytest.mark.parametrize(
    ("member", "bad_value"),
    (
        ("classification", "inferred"),
        ("evidence_paths", ["z.txt", "a.txt"]),
        ("evidence_paths", [r"C:\\temp\\evidence.txt"]),
        ("ambiguity", "unknown"),
        ("confidence", -0.01),
        ("confidence", 1.01),
        ("confirmed_by", ""),
        ("confirmed_at", "2026-07-12"),
    ),
)
def test_identity_manifest_rejects_invalid_provenance_confirmation_and_confidence(
    tmp_path: Path, member: str, bad_value: Any
) -> None:
    payload = _payload()
    payload["fields"]["project_name"][member] = bad_value
    identity = _identity()
    path = tmp_path / "invalid-provenance.json"
    path.write_text(json.dumps(payload) + "\n", encoding="utf-8")

    with pytest.raises(identity.IdentityValidationError):
        identity.load_identity(path)


@pytest.mark.parametrize("mutation", ("unknown_top", "unknown_field", "missing_field", "unknown_renderer"))
def test_identity_manifest_rejects_unknown_or_missing_members(
    tmp_path: Path, mutation: str
) -> None:
    payload = _payload()
    if mutation == "unknown_top":
        payload["unexpected"] = True
    elif mutation == "unknown_field":
        payload["fields"]["framework_owner"] = _field("wrong", "human", [])
    elif mutation == "missing_field":
        del payload["fields"]["mission"]
    else:
        payload["renderers"]["free_form"] = "1"
    identity = _identity()
    path = tmp_path / "invalid-members.json"
    path.write_text(json.dumps(payload) + "\n", encoding="utf-8")

    with pytest.raises(identity.IdentityValidationError):
        identity.load_identity(path)


def test_identity_manifest_allows_explicit_confirmed_null_repo_and_team(tmp_path: Path) -> None:
    payload = _payload(team=None)
    payload["fields"]["repo_url"] = _field(None, "human", [], confidence=None)
    manifest = _load(tmp_path, payload)

    assert manifest.fields["repo_url"].value is None
    assert manifest.fields["team"].value is None
    assert manifest.fields["repo_url"].confirmed_by == "Host Owner"
    assert manifest.fields["team"].confirmed_at == "2026-07-12T12:00:00Z"


@pytest.mark.parametrize(
    "field_name",
    (
        "project_name", "repo_url", "default_branch", "owner", "team", "mission",
        "article_xi_cutover", "stack", "quality_commands", "branch_convention",
        "commit_convention", "source_documents", "approval_boundaries", "worktree_profile",
    ),
)
def test_identity_manifest_blocks_every_unconfirmed_required_decision(
    tmp_path: Path, field_name: str
) -> None:
    payload = _payload()
    payload["fields"][field_name]["confirmed_by"] = None
    payload["fields"][field_name]["confirmed_at"] = None
    identity = _identity()
    path = tmp_path / "unconfirmed.json"
    path.write_text(json.dumps(payload) + "\n", encoding="utf-8")

    with pytest.raises(identity.IdentityConfirmationError) as caught:
        identity.load_identity(path)

    message = str(caught.value)
    assert field_name in message
    assert str(tmp_path) not in message
    assert all(secret not in message for secret in SECRET_CANARIES)


@pytest.mark.parametrize("ambiguity", ("multiple", "missing", "conflict"))
def test_identity_manifest_blocks_each_unresolved_ambiguity(
    tmp_path: Path, ambiguity: str
) -> None:
    payload = _payload()
    payload["fields"]["repo_url"]["ambiguity"] = ambiguity
    identity = _identity()
    path = tmp_path / "ambiguous.json"
    path.write_text(json.dumps(payload) + "\n", encoding="utf-8")

    with pytest.raises(identity.IdentityConfirmationError, match="repo_url"):
        identity.load_identity(path)


@pytest.mark.parametrize("command", QUALITY_ORDER)
@pytest.mark.parametrize(
    "patch",
    (
        {"state": "configured", "argv": [], "cwd": ".", "timeout_seconds": 30},
        {"state": "configured", "argv": ["pytest"], "cwd": None, "timeout_seconds": 30},
        {"state": "configured", "argv": ["pytest"], "cwd": ".", "timeout_seconds": None},
        {"state": "not-configured", "argv": ["pytest"], "cwd": None, "timeout_seconds": None},
        {"state": "not-configured", "argv": [], "cwd": ".", "timeout_seconds": None},
        {"state": "not-configured", "argv": [], "cwd": None, "timeout_seconds": 30},
        {"state": "configured", "argv": ["pytest"], "cwd": "..", "timeout_seconds": 30},
        {"state": "configured", "argv": ["pytest"], "cwd": ".", "timeout_seconds": 0},
        {"state": "configured", "argv": ["pytest"], "cwd": ".", "timeout_seconds": 3601},
    ),
)
def test_quality_command_state_and_bounds_are_exact(
    tmp_path: Path, command: str, patch: dict[str, Any]
) -> None:
    payload = _payload()
    payload["fields"]["quality_commands"]["value"][command].update(patch)
    identity = _identity()
    path = tmp_path / "invalid-quality.json"
    path.write_text(json.dumps(payload) + "\n", encoding="utf-8")

    with pytest.raises(identity.IdentityValidationError, match=command):
        identity.load_identity(path)


@pytest.mark.parametrize("missing_or_extra", ("missing", "extra"))
def test_quality_commands_require_exact_ordered_command_set(
    tmp_path: Path, missing_or_extra: str
) -> None:
    payload = _payload()
    commands = payload["fields"]["quality_commands"]["value"]
    if missing_or_extra == "missing":
        del commands["build"]
    else:
        commands["deploy"] = _quality(configured=False)
    identity = _identity()
    path = tmp_path / "invalid-quality-members.json"
    path.write_text(json.dumps(payload) + "\n", encoding="utf-8")

    with pytest.raises(identity.IdentityValidationError):
        identity.load_identity(path)


@pytest.mark.parametrize(
    ("raw", "expected"),
    (
        ("https://user:IDENTITY_PASSWORD_CANARY@example.invalid/org/repo.git?token=IDENTITY_TOKEN_CANARY#frag", "https://example.invalid/org/repo.git"),
        ("https://IDENTITY_TOKEN_CANARY@example.invalid/org/repo.git", "https://example.invalid/org/repo.git"),
        ("ssh://git@example.invalid/org/repo.git", "ssh://git@example.invalid/org/repo.git"),
        ("git@example.invalid:org/repo.git", "git@example.invalid:org/repo.git"),
    ),
)
def test_sanitize_remote_removes_credentials_and_preserves_only_conventional_git_user(
    raw: str, expected: str
) -> None:
    identity = _identity()
    result = identity.sanitize_remote(raw)

    assert result.value == expected
    serialized = repr(result)
    assert all(secret not in serialized for secret in SECRET_CANARIES)
    assert "?" not in result.value and "#" not in result.value


@pytest.mark.parametrize(
    "raw",
    (
        "ssh://deploy@example.invalid/org/repo.git",
        "deploy@example.invalid:org/repo.git",
        "${SECRET_REMOTE_TOKEN}@example.invalid/org/repo.git",
        "https://${SECRET_REMOTE_TOKEN}@example.invalid/org/repo.git",
        "ssh://user:IDENTITY_PASSWORD_CANARY@example.invalid/org/repo.git",
    ),
)
def test_sanitize_remote_blocks_ambiguous_or_secret_bearing_input_without_disclosure(
    raw: str
) -> None:
    identity = _identity()

    with pytest.raises(identity.RemoteSanitizationError) as caught:
        identity.sanitize_remote(raw)

    message = str(caught.value)
    assert "remote" in message.lower()
    assert "confirm" in message.lower()
    assert raw not in message
    assert all(secret not in message for secret in SECRET_CANARIES)


def test_render_project_config_has_exact_keys_types_order_and_canonical_bytes(tmp_path: Path) -> None:
    manifest = _load(tmp_path, _payload(team=None))
    identity = _identity()

    first = identity.render_project_config(manifest)
    second = identity.render_project_config(manifest)
    assert first == second
    assert isinstance(first, bytes) and first.endswith(b"\n") and b"\r" not in first
    config = json.loads(first, object_pairs_hook=dict)
    assert tuple(config) == PROJECT_CONFIG_ORDER
    assert config["schema_version"] == "1"
    assert config["team"] is None
    assert isinstance(config["approval_boundaries"], list)
    assert tuple(config["quality_commands"]) == QUALITY_ORDER
    assert "mission" not in config and "stack" not in config and "source_documents" not in config
    _assert_clean_bytes({"project.config.json": first}, tmp_path)


@pytest.mark.parametrize("stack", ("node", "python"))
def test_host_renderers_are_deterministic_specific_clean_and_read_only(
    tmp_path: Path, stack: str
) -> None:
    disposable = create_disposable_root(tmp_path)
    fixture = build_node_express_fixture(disposable) if stack == "node" else build_python_fixture(disposable)
    before = snapshot_paths((fixture.root, fixture.remote))
    manifest = _load(tmp_path, _payload(stack=stack))
    identity = _identity()
    reviewed = {
        "mission.md": manifest.fields["mission"].value.encode("utf-8") + b"\n",
        "tech-stack.md": ("# Stack\n\n" + "\n".join(manifest.fields["stack"].value) + "\n").encode("utf-8"),
    }
    bundle = SimpleNamespace(
        agents=("developer-general", "qa-engineer-general"),
        skills=("project-context", "testing-conventions"),
        prompts=("spec", "implement", "qa"),
    )

    calls = (
        lambda: identity.render_copilot_instructions(manifest),
        lambda: identity.render_constitution(manifest, reviewed),
        lambda: identity.render_rosters(manifest, bundle),
        lambda: identity.render_seeds(manifest),
    )
    all_text = ""
    for call in calls:
        first = _flatten_rendered(call())
        second = _flatten_rendered(call())
        assert first == second
        _assert_clean_bytes(first, tmp_path)
        all_text += "\n".join(data.decode("utf-8") for data in first.values())

    assert manifest.fields["project_name"].value in all_text
    assert manifest.fields["owner"].value in all_text
    assert manifest.fields["mission"].value in all_text
    assert manifest.fields["default_branch"].value in all_text
    assert "README.md" in all_text and "CONTRIBUTING.md" in all_text
    assert all(item in all_text for item in manifest.fields["stack"].value)
    assert "npm test" in all_text if stack == "node" else "python -m pytest" in all_text
    assert snapshot_paths((fixture.root, fixture.remote)) == before


def test_bounded_token_substitution_replaces_only_registered_exact_tokens() -> None:
    identity = _identity()
    template = "Project={{PROJECT_NAME}}\nBranch={{DEFAULT_BRANCH}}\nLiteral=Acme\n"
    values = {"PROJECT_NAME": "Acme Library", "DEFAULT_BRANCH": "trunk"}

    rendered = identity.substitute_bounded_tokens(
        template, values, allowed_tokens=("PROJECT_NAME", "DEFAULT_BRANCH")
    )

    assert rendered == "Project=Acme Library\nBranch=trunk\nLiteral=Acme\n"


@pytest.mark.parametrize(
    ("template", "values", "allowed"),
    (
        ("{{UNKNOWN_REQUIRED}}\n", {}, ("PROJECT_NAME",)),
        ("{{PROJECT_NAME}}\n", {"PROJECT_NAME": "ok", "UNUSED": "x"}, ("PROJECT_NAME",)),
        ("{{PROJECT_NAME}}\n", {"PROJECT_NAME": "ok"}, ("DEFAULT_BRANCH",)),
        ("{{PROJECT_NAME", {"PROJECT_NAME": "ok"}, ("PROJECT_NAME",)),
    ),
)
def test_bounded_token_substitution_rejects_unknown_unused_or_malformed_tokens(
    template: str, values: dict[str, str], allowed: tuple[str, ...]
) -> None:
    identity = _identity()
    with pytest.raises(identity.TemplateSubstitutionError):
        identity.substitute_bounded_tokens(template, values, allowed_tokens=allowed)


def test_renderers_preserve_host_owned_identity_inputs_and_return_no_mutation(
    tmp_path: Path,
) -> None:
    manifest = _load(tmp_path, _payload())
    identity = _identity()
    existing = {
        ".github/copilot-instructions.md": b"HOST_OWNED_INSTRUCTIONS_CANARY\r\n",
        "project.config.json": b'{"host_owned":true}\r\n',
    }
    original = copy.deepcopy(existing)

    ownership = identity.classify_existing_identity_inputs(
        existing,
        managed_hashes={},
    )

    assert existing == original
    assert tuple(ownership) == tuple(existing)
    assert all(item.classification == "host-owned" for item in ownership.values())
    assert all(item.action == "preserve" for item in ownership.values())
    assert all(item.requires_preview_approval for item in ownership.values())
    assert all(item.requires_backup for item in ownership.values())
    assert "HOST_OWNED_INSTRUCTIONS_CANARY" not in repr(ownership)


def test_error_paths_and_rendered_outputs_never_disclose_secrets_framework_or_temp_roots(
    tmp_path: Path,
) -> None:
    payload = _payload()
    payload["fields"]["repo_url"]["value"] = (
        "https://user:IDENTITY_PASSWORD_CANARY@example.invalid/repo.git"
        "?token=IDENTITY_TOKEN_CANARY#fragment"
    )
    payload["fields"]["mission"]["value"] = "${SECRET_REMOTE_TOKEN}"
    identity = _identity()
    path = tmp_path / "secret-input.json"
    path.write_text(json.dumps(payload) + "\n", encoding="utf-8")

    with pytest.raises(identity.IdentityValidationError) as caught:
        identity.load_identity(path)

    message = str(caught.value)
    assert str(tmp_path) not in message
    assert not re.search(r"(?i)(password|token)[=:][^ ]+", message)
    assert all(secret not in message for secret in SECRET_CANARIES)
    assert all(framework not in message for framework in FRAMEWORK_CANARIES)
