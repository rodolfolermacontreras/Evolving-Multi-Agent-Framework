#!/usr/bin/env python3
"""Regression checks for SDD-035 Azure dashboard workflow retirement.

The original SDD-009 tests validated `.github/workflows/deploy-dashboard.yml`.
SDD-035 decommissions that Azure deployment path, so the regression contract now
asserts that no active GitHub Actions workflow can deploy the dashboard to Azure.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure the cli package is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Resolve the workflow file relative to the repo root
_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_WORKFLOW_DIR = _REPO_ROOT / ".github" / "workflows"
_DEPLOY_WORKFLOW_PATH = _WORKFLOW_DIR / "deploy-dashboard.yml"


AZURE_DEPLOY_KEYWORDS = [
    "azure/login",
    "azure-credentials",
    "AZURE_CLIENT_ID",
    "AZURE_TENANT_ID",
    "AZURE_SUBSCRIPTION_ID",
    "containerapp",
    "rg-bridge-dashboard",
    "state-dashboard",
    "ca24921a026cacr",
    "azurecontainerapps",
]


def _workflow_files() -> list[Path]:
    if not _WORKFLOW_DIR.exists():
        return []
    return [path for path in _WORKFLOW_DIR.glob("*.yml") if path.is_file()]


class TestAzureDashboardWorkflowRetired:
    """SDD-035: the Azure dashboard deploy workflow remains retired."""

    def test_deploy_dashboard_workflow_removed(self) -> None:
        assert not _DEPLOY_WORKFLOW_PATH.exists()

    def test_no_workflow_contains_azure_dashboard_deploy_keywords(self) -> None:
        for workflow_path in _workflow_files():
            content = workflow_path.read_text(encoding="utf-8")
            for keyword in AZURE_DEPLOY_KEYWORDS:
                assert keyword not in content, (
                    f"{workflow_path} still contains retired Azure deploy "
                    f"keyword '{keyword}'"
                )

    def test_workflow_directory_has_no_retired_dashboard_deploy_yaml(self) -> None:
        workflow_names = {path.name for path in _workflow_files()}
        assert "deploy-dashboard.yml" not in workflow_names
