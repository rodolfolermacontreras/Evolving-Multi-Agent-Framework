"""RED-2B proposal preservation, baseline, refresh, and adoption tests for SDD-058."""

from __future__ import annotations

import hashlib
import importlib
import json
import sys
from pathlib import Path
from typing import Any, Callable

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

BASELINE_SCHEMA = "1"
BUNDLE_VERSION = "brownfield-core@1"
SOURCE_REVISION = "a" * 40
EVIDENCE_DIGEST = "b" * 64


def _proposal():
    """Import the intentionally absent proposal production API in test bodies."""

    return importlib.import_module("brownfield_proposal")


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _write_bytes(root: Path, relative: str, data: bytes) -> Path:
    path = root / Path(*relative.split("/"))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return path


def _baseline_file(path: str, data: bytes) -> dict[str, Any]:
    return {
        "path": path,
        "sha256": _sha256(data),
        "byte_length": len(data),
        "baseline_path": f".baseline/{path}",
        "renderer_id": "constitution",
        "renderer_version": "1",
        "evidence_dependencies": ["repository-evidence@1"],
        "text_policy": "preserve-bytes",
    }


def _write_baseline(
    proposal_root: Path,
    files: dict[str, bytes],
    *,
    mutate_manifest: Callable[[dict[str, Any]], None] | None = None,
    write_snapshots: bool = True,
) -> tuple[Path, dict[str, Any]]:
    entries = [_baseline_file(path, data) for path, data in sorted(files.items())]
    manifest: dict[str, Any] = {
        "schema_version": BASELINE_SCHEMA,
        "source_revision": SOURCE_REVISION,
        "evidence_digest": EVIDENCE_DIGEST,
        "bundle_version": BUNDLE_VERSION,
        "generated_at": "2026-07-12",
        "files": entries,
    }
    if mutate_manifest is not None:
        mutate_manifest(manifest)
    if write_snapshots:
        for path, data in files.items():
            _write_bytes(proposal_root, f".baseline/{path}", data)
    manifest_path = proposal_root / "baseline-manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        json.dumps(manifest, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return manifest_path, manifest


def _snapshot_tree(root: Path) -> dict[str, object]:
    return snapshot_paths((root,))


def _outcome_value(outcome: object) -> str:
    value = getattr(outcome, "value", outcome)
    return str(value)


def _plan_items(plan: object) -> tuple[object, ...]:
    return tuple(getattr(plan, "items"))


def _item_by_path(plan: object, path: str) -> object:
    return next(item for item in _plan_items(plan) if getattr(item, "path") == path)


def test_load_and_validate_baseline_accepts_complete_lossless_schema(tmp_path: Path) -> None:
    proposal_root = tmp_path / ".sdd-proposal"
    files = {
        "constitution/mission.md": b"# Mission\r\n\r\nGenerated baseline.\r\n",
        "constitution/principles.md": b"# Principles\n\nGenerated baseline.\n",
    }
    _, raw_manifest = _write_baseline(proposal_root, files)
    proposal = _proposal()

    baseline = proposal.load_and_validate_baseline(proposal_root)

    assert baseline.schema_version == BASELINE_SCHEMA
    assert baseline.source_revision == SOURCE_REVISION
    assert baseline.evidence_digest == EVIDENCE_DIGEST
    assert baseline.bundle_version == BUNDLE_VERSION
    assert tuple(item.path for item in baseline.files) == tuple(sorted(files))
    assert all("\\" not in item.path and not Path(item.path).is_absolute() for item in baseline.files)
    for item in baseline.files:
        expected = files[item.path]
        assert item.sha256 == _sha256(expected)
        assert item.byte_length == len(expected)
        assert item.baseline_path == raw_manifest["files"][tuple(sorted(files)).index(item.path)]["baseline_path"]
        assert tuple(item.evidence_dependencies) == ("repository-evidence@1",)
        assert item.renderer_id == "constitution"
        assert item.renderer_version == "1"
        assert item.text_policy == "preserve-bytes"
        assert (proposal_root / Path(*item.baseline_path.split("/"))).read_bytes() == expected


def test_load_and_validate_baseline_preserves_reviewed_and_snapshot_bytes_and_skips_generation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    proposal = _proposal()
    disposable = create_disposable_root(tmp_path)
    fixture = build_node_express_fixture(disposable)
    proposal_root = fixture.root / ".sdd-proposal"
    reviewed = proposal_root / "constitution/mission.md"
    reviewed_preimage = reviewed.read_bytes()
    baseline_preimage = b"# Mission\n\nOriginal generated baseline.\n"
    _write_baseline(proposal_root, {"constitution/mission.md": baseline_preimage})
    before = _snapshot_tree(proposal_root)
    def forbidden(*_args: object, **_kwargs: object) -> object:
        pytest.fail("normal validation/apply must not generate or refresh a proposal")

    monkeypatch.setattr(proposal, "generate_proposal", forbidden)
    monkeypatch.setattr(proposal, "plan_refresh", forbidden)
    baseline = proposal.load_and_validate_baseline(proposal_root)

    assert baseline.files[0].sha256 == _sha256(baseline_preimage)
    assert reviewed.read_bytes() == reviewed_preimage
    assert _snapshot_tree(proposal_root) == before
    assert not hasattr(proposal, "apply")
    assert not hasattr(proposal, "apply_proposal")


@pytest.mark.parametrize(
    ("baseline", "reviewed", "candidate", "expected"),
    (
        (b"base", b"base", b"base", "unchanged"),
        (b"base", b"base", b"upstream", "upstream-only"),
        (b"base", b"human", b"base", "user-only"),
        (b"base", b"same-new", b"same-new", "convergent"),
        (b"base", b"human", b"upstream", "conflict"),
    ),
)
def test_classify_refresh_returns_exact_five_outcomes(
    baseline: bytes, reviewed: bytes, candidate: bytes, expected: str
) -> None:
    proposal = _proposal()
    outcome = proposal.classify_refresh(baseline, reviewed, candidate)
    assert _outcome_value(outcome) == expected


def test_classify_refresh_is_byte_exact_not_todo_or_text_heuristic() -> None:
    proposal = _proposal()
    baseline = b"TODO: human answer required\r\n"

    assert _outcome_value(proposal.classify_refresh(baseline, baseline, b"answered\n")) == "upstream-only"
    assert _outcome_value(proposal.classify_refresh(baseline, b"TODO: changed by human\r\n", baseline)) == "user-only"
    assert _outcome_value(proposal.classify_refresh(b"same text\n", b"same text\r\n", b"same text\n")) == "user-only"


def test_plan_refresh_classifies_multiple_files_in_deterministic_path_order(tmp_path: Path) -> None:
    proposal_root = tmp_path / ".sdd-proposal"
    baselines = {
        "constitution/mission.md": b"mission-base\n",
        "constitution/principles.md": b"principles-base\n",
        "constitution/roadmap.md": b"roadmap-base\n",
    }
    _write_baseline(proposal_root, baselines)
    reviewed = {
        "constitution/roadmap.md": b"roadmap-human\n",
        "constitution/mission.md": b"mission-base\n",
        "constitution/principles.md": b"principles-same-new\n",
    }
    candidates = {
        "constitution/principles.md": b"principles-same-new\n",
        "constitution/mission.md": b"mission-upstream\n",
        "constitution/roadmap.md": b"roadmap-base\n",
    }
    for path, data in reviewed.items():
        _write_bytes(proposal_root, path, data)
    proposal = _proposal()

    first = proposal.plan_refresh(proposal_root, candidates)
    second = proposal.plan_refresh(proposal_root, dict(reversed(tuple(candidates.items()))))

    assert tuple(item.path for item in _plan_items(first)) == tuple(sorted(baselines))
    assert first == second
    assert _outcome_value(_item_by_path(first, "constitution/mission.md").outcome) == "upstream-only"
    assert _outcome_value(_item_by_path(first, "constitution/principles.md").outcome) == "convergent"
    assert _outcome_value(_item_by_path(first, "constitution/roadmap.md").outcome) == "user-only"


def test_plan_refresh_preserves_user_and_convergent_values_without_mutation(tmp_path: Path) -> None:
    proposal_root = tmp_path / ".sdd-proposal"
    baselines = {
        "constitution/mission.md": b"mission-base\r\n",
        "constitution/principles.md": b"principles-base\n",
    }
    reviewed = {
        "constitution/mission.md": b"mission-human\r\n",
        "constitution/principles.md": b"principles-shared\n",
    }
    candidates = {
        "constitution/mission.md": baselines["constitution/mission.md"],
        "constitution/principles.md": reviewed["constitution/principles.md"],
    }
    _write_baseline(proposal_root, baselines)
    for path, data in reviewed.items():
        _write_bytes(proposal_root, path, data)
    before = _snapshot_tree(proposal_root)
    proposal = _proposal()

    plan = proposal.plan_refresh(proposal_root, candidates)

    assert _snapshot_tree(proposal_root) == before
    assert tuple(getattr(plan, "conflicts")) == ()
    assert _item_by_path(plan, "constitution/mission.md").result_bytes == reviewed["constitution/mission.md"]
    assert _item_by_path(plan, "constitution/principles.md").result_bytes == reviewed["constitution/principles.md"]


def test_plan_refresh_conflict_requires_explicit_per_file_resolution_and_keeps_preimages(
    tmp_path: Path,
) -> None:
    proposal_root = tmp_path / ".sdd-proposal"
    path = "constitution/mission.md"
    baseline = b"baseline\n"
    reviewed = b"human-reviewed\r\n"
    candidate = b"new-upstream\n"
    _write_baseline(proposal_root, {path: baseline})
    reviewed_path = _write_bytes(proposal_root, path, reviewed)
    baseline_path = proposal_root / ".baseline/constitution/mission.md"
    before = _snapshot_tree(proposal_root)
    proposal = _proposal()

    unresolved = proposal.plan_refresh(proposal_root, {path: candidate})

    assert tuple(getattr(unresolved, "conflicts")) == (path,)
    assert bool(getattr(unresolved, "requires_resolution"))
    assert _outcome_value(_item_by_path(unresolved, path).outcome) == "conflict"
    assert reviewed_path.read_bytes() == reviewed
    assert baseline_path.read_bytes() == baseline
    assert _snapshot_tree(proposal_root) == before

    with pytest.raises(proposal.ProposalConflictError, match="resolution|conflict"):
        proposal.plan_refresh(proposal_root, {path: candidate}, resolutions={})
    with pytest.raises(proposal.ProposalConflictError, match="resolution|choice"):
        proposal.plan_refresh(proposal_root, {path: candidate}, resolutions={path: "overwrite"})

    preserve = proposal.plan_refresh(
        proposal_root, {path: candidate}, resolutions={path: "reviewed"}
    )
    adopt = proposal.plan_refresh(
        proposal_root, {path: candidate}, resolutions={path: "candidate"}
    )
    assert _item_by_path(preserve, path).result_bytes == reviewed
    assert _item_by_path(adopt, path).result_bytes == candidate
    assert not bool(getattr(preserve, "requires_resolution"))
    assert not bool(getattr(adopt, "requires_resolution"))
    assert _snapshot_tree(proposal_root) == before


@pytest.mark.parametrize(
    ("case", "mutate", "snapshot_mode", "guidance"),
    (
        ("malformed-json", None, "malformed", "baseline"),
        ("unsupported-schema", lambda data: data.update(schema_version="999"), "normal", "version"),
        ("missing-source", lambda data: data.pop("source_revision"), "normal", "source"),
        ("missing-evidence", lambda data: data.pop("evidence_digest"), "normal", "evidence"),
        ("wrong-bundle", lambda data: data.update(bundle_version="unknown@9"), "normal", "bundle"),
        ("escaping-reviewed-path", lambda data: data["files"][0].update(path="../escape.md"), "normal", "path"),
        ("absolute-reviewed-path", lambda data: data["files"][0].update(path="C:/escape.md"), "normal", "path"),
        ("escaping-snapshot-path", lambda data: data["files"][0].update(baseline_path="../../escape.md"), "normal", "path"),
        ("hash-mismatch", lambda data: data["files"][0].update(sha256="0" * 64), "normal", "hash"),
        ("length-mismatch", lambda data: data["files"][0].update(byte_length=999), "normal", "length"),
        ("missing-renderer", lambda data: data["files"][0].update(renderer_id=""), "normal", "renderer"),
        ("missing-snapshot", None, "missing", "snapshot"),
        ("duplicate-path", lambda data: data["files"].append(dict(data["files"][0])), "normal", "duplicate"),
        ("unsorted-paths", lambda data: data["files"].reverse(), "two-files", "sort"),
    ),
)
def test_load_and_validate_baseline_rejects_invalid_matrix_without_mutation(
    tmp_path: Path,
    case: str,
    mutate: Callable[[dict[str, Any]], None] | None,
    snapshot_mode: str,
    guidance: str,
) -> None:
    proposal_root = tmp_path / case / ".sdd-proposal"
    files = {"constitution/mission.md": b"baseline mission\n"}
    if snapshot_mode == "two-files":
        files["constitution/principles.md"] = b"baseline principles\n"
    manifest_path, _ = _write_baseline(
        proposal_root,
        files,
        mutate_manifest=mutate,
        write_snapshots=snapshot_mode != "missing",
    )
    if snapshot_mode == "malformed":
        manifest_path.write_bytes(b"{not-json\n")
    before = _snapshot_tree(proposal_root)
    proposal = _proposal()

    with pytest.raises(proposal.BaselineValidationError) as caught:
        proposal.load_and_validate_baseline(proposal_root)

    message = str(caught.value).lower()
    assert guidance in message
    assert "adopt" in message or "regenerate" in message or "baseline" in message
    assert "traceback" not in message
    assert str(tmp_path).lower() not in message
    assert _snapshot_tree(proposal_root) == before


def test_missing_legacy_baseline_blocks_normal_validation_without_creating_files(tmp_path: Path) -> None:
    proposal = _proposal()
    disposable = create_disposable_root(tmp_path)
    fixture = build_node_express_fixture(disposable)
    proposal_root = fixture.root / ".sdd-proposal"
    reviewed = proposal_root / "constitution/mission.md"
    reviewed_preimage = reviewed.read_bytes()
    before = _snapshot_tree(proposal_root)
    with pytest.raises(proposal.LegacyBaselineRequiredError, match="adopt|legacy|baseline"):
        proposal.load_and_validate_baseline(proposal_root)

    assert reviewed.read_bytes() == reviewed_preimage
    assert not (proposal_root / "baseline-manifest.json").exists()
    assert not (proposal_root / ".baseline").exists()
    assert _snapshot_tree(proposal_root) == before


@pytest.mark.parametrize("stack", ("node", "python"))
def test_plan_baseline_adoption_previews_side_by_side_without_touching_legacy_proposal(
    tmp_path: Path, stack: str
) -> None:
    proposal = _proposal()
    disposable = create_disposable_root(tmp_path)
    fixture = build_node_express_fixture(disposable) if stack == "node" else build_python_fixture(disposable)
    proposal_root = fixture.root / ".sdd-proposal"
    reviewed_path = proposal_root / "constitution/mission.md"
    if not reviewed_path.exists():
        _write_bytes(proposal_root, "constitution/mission.md", b"# Mission\n\nPython human review.\n")
    reviewed_preimage = reviewed_path.read_bytes()
    candidate = b"# Mission\n\nNew generated candidate.\n"
    before = _snapshot_tree(proposal_root)
    plan = proposal.plan_baseline_adoption(
        proposal_root, {"constitution/mission.md": candidate}
    )

    assert bool(getattr(plan, "legacy_baseline_adoption"))
    assert bool(getattr(plan, "requires_exact_approval"))
    assert tuple(item.path for item in _plan_items(plan)) == ("constitution/mission.md",)
    item = _item_by_path(plan, "constitution/mission.md")
    assert item.reviewed_bytes == reviewed_preimage
    assert item.candidate_bytes == candidate
    assert item.baseline_bytes == candidate
    assert item.reviewed_destination == "constitution/mission.md"
    assert item.candidate_destination != item.reviewed_destination
    assert item.baseline_destination != item.reviewed_destination
    assert reviewed_path.read_bytes() == reviewed_preimage
    assert not (proposal_root / "baseline-manifest.json").exists()
    assert not (proposal_root / ".baseline").exists()
    assert _snapshot_tree(proposal_root) == before


def test_plan_baseline_adoption_requires_exact_resolution_for_existing_difference(
    tmp_path: Path,
) -> None:
    proposal_root = tmp_path / ".sdd-proposal"
    path = "constitution/mission.md"
    reviewed = b"human legacy decision\r\n"
    candidate = b"generated candidate\n"
    _write_bytes(proposal_root, path, reviewed)
    before = _snapshot_tree(proposal_root)
    proposal = _proposal()

    preview = proposal.plan_baseline_adoption(proposal_root, {path: candidate})

    assert tuple(getattr(preview, "conflicts")) == (path,)
    assert bool(getattr(preview, "requires_resolution"))
    with pytest.raises(proposal.ProposalConflictError, match="resolution|conflict"):
        proposal.plan_baseline_adoption(
            proposal_root, {path: candidate}, resolutions={path: "overwrite"}
        )
    resolved = proposal.plan_baseline_adoption(
        proposal_root, {path: candidate}, resolutions={path: "reviewed"}
    )
    assert not bool(getattr(resolved, "requires_resolution"))
    assert _item_by_path(resolved, path).result_bytes == reviewed
    assert _snapshot_tree(proposal_root) == before
