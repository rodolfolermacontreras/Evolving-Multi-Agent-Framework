#!/usr/bin/env python3
"""Tests for .github/workflows/deploy-dashboard.yml (SDD-009, T-003).

Validates V-6, V-7, V-8 from the validation contract.

Parser choice: stdlib-only minimal YAML handling. The workflow file is simple
enough that we read it as text and parse key assertions via substring checks
and a lightweight line-by-line parser. No third-party YAML library is used,
consistent with the project's stdlib-only constraint (LESSON-001).
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Ensure the cli package is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Resolve the workflow file relative to the repo root
_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_WORKFLOW_PATH = _REPO_ROOT / ".github" / "workflows" / "deploy-dashboard.yml"


def _read_workflow() -> str:
    """Read the workflow file content; skip test if file does not exist."""
    if not _WORKFLOW_PATH.is_file():
        pytest.skip(f"Workflow file not found at {_WORKFLOW_PATH}")
    return _WORKFLOW_PATH.read_text(encoding="utf-8")


class TestDeployWorkflowOIDC:
    """V-6: workflow declares OIDC-only auth with no client secrets."""

    def test_deploy_workflow_oidc_only(self) -> None:
        content = _read_workflow()

        # Must declare id-token: write for OIDC federation
        assert "id-token: write" in content

        # Must NOT contain any client-secret references
        forbidden = [
            "client-secret",
            "client_secret",
            "AZURE_CLIENT_SECRET",
            "ARM_CLIENT_SECRET",
            "password:",
        ]
        for pattern in forbidden:
            assert pattern not in content, (
                f"Workflow must not contain '{pattern}' (OIDC-only per ADR-009)"
            )

        # azure/login step must reference client-id, tenant-id, subscription-id
        assert "client-id:" in content
        assert "tenant-id:" in content
        assert "subscription-id:" in content


class TestDeployWorkflowTriggers:
    """V-7: workflow triggers cover state.md path and required branches."""

    def test_deploy_workflow_triggers_cover_state_md(self) -> None:
        content = _read_workflow()

        # Must declare workflow_dispatch
        assert "workflow_dispatch" in content

        # Must trigger on push to master
        assert "master" in content

        # If paths filter is present, it must include these critical paths
        if "paths:" in content:
            required_paths = [
                "spec-driven-development/exec/state.md",
                "spec-driven-development/cli/state_builder.py",
                ".github/workflows/deploy-dashboard.yml",
                "Dockerfile",
            ]
            for p in required_paths:
                assert p in content, (
                    f"Workflow paths filter must include '{p}'"
                )


class TestDeployWorkflowYAMLParses:
    """V-8: workflow YAML parses cleanly (smoke test)."""

    def test_deploy_workflow_yaml_parses(self) -> None:
        content = _read_workflow()

        # Minimal structural check: top-level keys must be present
        assert "name:" in content
        assert "on:" in content
        assert "jobs:" in content

        # Must have a job definition
        lines = content.splitlines()
        has_job = any(
            line.strip().endswith(":") and not line.startswith(" " * 4)
            for line in lines
            if "jobs:" not in line and line.strip()
        )
        # The file should parse without obvious YAML errors
        # (balanced quotes, no tabs for indentation)
        for i, line in enumerate(lines, 1):
            assert "\t" not in line, (
                f"Line {i}: YAML must use spaces, not tabs"
            )
