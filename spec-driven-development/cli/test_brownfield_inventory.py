"""RED-2A inventory, evidence, path, link, and redaction matrix for SDD-058."""

from __future__ import annotations

import importlib
import subprocess
import sys
from pathlib import Path

import pytest

CLI_DIR = Path(__file__).resolve().parent
if str(CLI_DIR) not in sys.path:
    sys.path.insert(0, str(CLI_DIR))

from brownfield_test_fixtures import (  # noqa: E402
    build_node_express_fixture,
    build_python_fixture,
    create_disposable_root,
    make_link,
    snapshot_paths,
)


def _inventory():
    """Import the intentionally absent read-only production API in test bodies."""

    return importlib.import_module("brownfield_inventory")


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), *args], check=True, capture_output=True,
        text=True, encoding="utf-8",
    ).stdout.strip()


@pytest.mark.parametrize(
    ("raw", "reason"),
    (
        ("../escape", "traversal"),
        ("safe/../../escape", "traversal"),
        (r"safe\..\..\escape", "traversal"),
        (r"safe/..\../escape", "traversal"),
        ("/absolute/path", "absolute"),
        (r"C:\absolute\path", "absolute"),
        (r"C:drive-relative", "drive"),
        (r"\\server\share\path", "absolute"),
        (".git/config", ".git"),
        ("safe/.GIT/objects", ".git"),
        ("CON", "reserved"),
        ("safe/aux.txt", "reserved"),
        ("safe/NUL.json", "reserved"),
        ("safe/trailing-dot.", "reserved"),
        ("safe/trailing-space ", "reserved"),
        ("safe/control" + chr(1) + "name", "control"),
        ("safe/nul" + chr(0) + "name", "control"),
        ("", "empty"),
        (".", "empty"),
    ),
)
def test_safe_relative_path_rejects_lexically_unsafe_matrix(
    tmp_path: Path, raw: str, reason: str
) -> None:
    root = tmp_path / "root"
    root.mkdir()
    inventory = _inventory()
    before = snapshot_paths((root,))

    with pytest.raises(inventory.PathSafetyError) as caught:
        inventory.safe_relative_path(raw, root, "managed destination", allow_missing=True)

    message = str(caught.value).lower()
    assert reason in message
    assert "managed destination" in message
    assert "traceback" not in message
    assert snapshot_paths((root,)) == before


@pytest.mark.parametrize(
    "raw",
    ("src/package/file.py", "README.md", "docs/name with spaces.md", "unicode/café.txt"),
)
def test_safe_relative_path_accepts_contained_portable_paths(
    tmp_path: Path, raw: str
) -> None:
    root = tmp_path / "root"
    root.mkdir()
    inventory = _inventory()

    result = inventory.safe_relative_path(raw, root, "managed destination", allow_missing=True)

    assert result == root / Path(*raw.split("/"))
    assert result.is_relative_to(root)


@pytest.mark.parametrize(
    "paths",
    (
        ("Readme.md", "README.md"),
        ("docs/guide.md", "DOCS/GUIDE.md"),
        ("alpha", "alpha/beta"),
        ("alpha/beta", "alpha"),
        ("same/path", "same/path"),
    ),
)
def test_validate_path_set_rejects_casefold_duplicates_and_overlap(paths: tuple[str, str]) -> None:
    inventory = _inventory()
    with pytest.raises(inventory.PathSafetyError):
        inventory.validate_path_set(paths)


def test_validate_path_set_returns_sorted_posix_paths() -> None:
    inventory = _inventory()
    assert inventory.validate_path_set(("zeta/file", r"alpha\file", "middle")) == (
        "alpha/file", "middle", "zeta/file"
    )


@pytest.mark.parametrize("stack", ("node", "python"))
def test_validate_repository_root_requires_exact_committed_root(
    tmp_path: Path, stack: str
) -> None:
    disposable = create_disposable_root(tmp_path)
    fixture = build_node_express_fixture(disposable) if stack == "node" else build_python_fixture(disposable)
    inventory = _inventory()

    assert inventory.validate_repository_root(fixture.root) == fixture.root.resolve()
    for invalid in (fixture.root / "src", fixture.root / ".git", disposable.root, fixture.remote):
        with pytest.raises(inventory.RepositoryValidationError):
            inventory.validate_repository_root(invalid)


def test_validate_repository_root_rejects_missing_head(tmp_path: Path) -> None:
    empty = tmp_path / "empty-repository"
    subprocess.run(
        ["git", "init", "--quiet", "--initial-branch=main", str(empty)],
        check=True, capture_output=True,
    )
    inventory = _inventory()
    with pytest.raises(inventory.RepositoryValidationError, match="HEAD"):
        inventory.validate_repository_root(empty)


def test_validate_repository_root_rejects_link_or_named_equivalent(tmp_path: Path) -> None:
    disposable = create_disposable_root(tmp_path)
    fixture = build_node_express_fixture(disposable)
    linked = tmp_path / "linked-host"
    link_created = make_link(linked, fixture.root)
    inventory = _inventory()

    if link_created:
        with pytest.raises(inventory.PathSafetyError, match="link|reparse|junction"):
            inventory.validate_repository_root(linked)
    else:
        linked.mkdir()
        (linked / "link-equivalent.marker").write_text(str(fixture.root), encoding="utf-8")
        with pytest.raises(inventory.RepositoryValidationError):
            inventory.validate_repository_root(linked)


def test_collect_repository_evidence_is_sorted_deterministic_and_stack_specific(
    tmp_path: Path,
) -> None:
    disposable = create_disposable_root(tmp_path)
    node = build_node_express_fixture(disposable)
    python = build_python_fixture(disposable)
    inventory = _inventory()

    node_first = inventory.collect_repository_evidence(node.root)
    node_second = inventory.collect_repository_evidence(node.root)
    python_evidence = inventory.collect_repository_evidence(python.root)

    assert node_first == node_second
    assert (node_first.target_head, node_first.default_branch, node_first.project_name) == (
        node.head, "main", "fixture-express-service"
    )
    assert "node" in node_first.stack
    assert (python_evidence.target_head, python_evidence.default_branch, python_evidence.project_name) == (
        python.head, "trunk", "fixture-python-library"
    )
    assert "python" in python_evidence.stack
    assert node_first.source_documents == tuple(sorted(node_first.source_documents))
    assert all("\\" not in path and not Path(path).is_absolute() for path in node_first.source_documents)
    assert node_first.evidence_digest != python_evidence.evidence_digest


@pytest.mark.parametrize(
    "remote",
    (
        "https://secret-user:token-value@example.invalid/org/repo.git?sig=secret#fragment",
        "https://token-value@example.invalid/org/repo.git",
        "ssh://secret-user:token-value@example.invalid/org/repo.git",
        "${SECRET_REMOTE_TOKEN}@example.invalid/org/repo.git",
    ),
)
def test_collect_repository_evidence_redacts_or_blocks_secret_remote_canaries(
    tmp_path: Path, remote: str
) -> None:
    disposable = create_disposable_root(tmp_path)
    fixture = build_python_fixture(disposable)
    _git(fixture.root, "remote", "set-url", "origin", remote)
    inventory = _inventory()
    canaries = ("secret-user", "token-value", "sig=secret", "SECRET_REMOTE_TOKEN")

    try:
        evidence = inventory.collect_repository_evidence(fixture.root)
    except inventory.RepositoryEvidenceError as error:
        serialized = str(error)
    else:
        serialized = repr(evidence)
        assert evidence.remotes
        assert all("?" not in item and "#" not in item for item in evidence.remotes)

    for canary in canaries:
        assert canary not in serialized
    assert str(tmp_path) not in serialized


def test_collect_repository_evidence_keeps_conventional_nonsecret_git_ssh_user(
    tmp_path: Path,
) -> None:
    disposable = create_disposable_root(tmp_path)
    fixture = build_node_express_fixture(disposable)
    _git(fixture.root, "remote", "set-url", "origin", "git@example.invalid:org/repo.git")
    inventory = _inventory()
    evidence = inventory.collect_repository_evidence(fixture.root)
    assert evidence.remotes == ("git@example.invalid:org/repo.git",)


def test_inventory_target_rejects_link_without_reading_external_or_unrelated_bytes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    disposable = create_disposable_root(tmp_path)
    fixture = build_python_fixture(disposable)
    outside = tmp_path / "outside"
    outside.mkdir()
    secret = outside / "secret.txt"
    secret.write_text("INVENTORY_SECRET_CANARY\n", encoding="utf-8")
    linked = fixture.root / "linked-outside"
    link_created = make_link(linked, outside)
    unrelated = fixture.root / "unrelated-host-owned.txt"
    unrelated.write_text(
        "UNRELATED_CONTENT_CANARY\n", encoding="utf-8"
    )
    inventory = _inventory()
    original_read_bytes = Path.read_bytes
    read_paths: list[Path] = []

    def record_read_bytes(path: Path) -> bytes:
        read_paths.append(path)
        return original_read_bytes(path)

    monkeypatch.setattr(Path, "read_bytes", record_read_bytes)

    if not link_created:
        pytest.skip("directory links are unavailable")

    with pytest.raises(inventory.PathSafetyError, match="link|junction|reparse"):
        inventory.inventory_target(
            fixture.root,
            managed_paths=("README.md", "linked-outside"),
            forbidden_fingerprints=("FRAMEWORK_FORBIDDEN_CANARY",),
        )

    assert read_paths == [fixture.root / "README.md"]


def test_inventory_target_hashes_only_managed_files_without_fingerprint_scan(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    disposable = create_disposable_root(tmp_path)
    fixture = build_python_fixture(disposable)
    unrelated = fixture.root / "unrelated-host-owned.txt"
    unrelated.write_text("UNRELATED_CONTENT_CANARY\n", encoding="utf-8")
    inventory = _inventory()
    original_read_bytes = Path.read_bytes
    read_paths: list[Path] = []

    def record_read_bytes(path: Path) -> bytes:
        read_paths.append(path)
        return original_read_bytes(path)

    monkeypatch.setattr(Path, "read_bytes", record_read_bytes)

    snapshot = inventory.inventory_target(
        fixture.root,
        managed_paths=("README.md",),
        forbidden_fingerprints=(),
    )

    assert read_paths == [fixture.root / "README.md"]
    assert snapshot.observations[0].sha256 is not None
    assert all("\\" not in observation.path for observation in snapshot.observations)


def test_expected_inventory_failures_are_actionable_and_do_not_disclose_content(
    tmp_path: Path,
) -> None:
    root = tmp_path / "root"
    root.mkdir()
    secret = "SENSITIVE_FILE_CONTENT_CANARY"
    (root / "secret.txt").write_text(secret, encoding="utf-8")
    inventory = _inventory()

    with pytest.raises(inventory.PathSafetyError) as caught:
        inventory.safe_relative_path("../secret.txt", root, "proposal", allow_missing=False)

    message = str(caught.value)
    assert "proposal" in message.lower()
    assert "outside" in message.lower() or "traversal" in message.lower()
    assert secret not in message
    assert str(tmp_path) not in message
    assert "Traceback" not in message
