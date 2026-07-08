#!/usr/bin/env python3
"""
Bootstrap helper for greenfield and brownfield SDD host projects.

Usage:
    python bootstrap.py greenfield <archetype-name> \
        --project-name MyLib --owner "Your Name" --target ../MyLib

The command copies this framework's portable Markdown/YAML assets into an
empty host repository, applies an archetype constitution, personalizes common
placeholders, and creates the first backlog and ledger placeholders.
"""

from pathlib import Path
import argparse
import datetime
import json
import os
import re
import shutil
import sqlite3
import subprocess
import sys

CONSTITUTION_FILES = (
    "mission.md",
    "tech-stack.md",
    "principles.md",
    "roadmap.md",
    "decision-policy.md",
    "quality-policy.md",
)

BACKLOG_FILES = ("IDEAS.md", "BACKLOG.md")
PLACEHOLDER_PATTERN = re.compile(r"\{\{(PROJECT_NAME|OWNER|DATE)\}\}")
FRONTMATTER_PATTERN = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)


class BootstrapError(Exception):
    """Expected bootstrap failure with a human-readable remediation."""


def framework_root() -> Path:
    """Return the repository root containing this bootstrap script."""
    return Path(__file__).resolve().parents[2]


def today_iso() -> str:
    """Return today's date in the framework's required YYYY-MM-DD format."""
    return datetime.date.today().isoformat()


def load_project_config(root: Path) -> dict:
    """Return the host project's identity config from ``project.config.json``.

    The config surface (A-2) holds ``owner``, ``team``, and ``repo_url`` so the
    framework's generic files never hardcode a personal name -- they trace to
    config or to "the host project's owner". Returns an empty dict when the
    file is absent or unreadable, so callers degrade gracefully on a fresh
    clone. Stdlib-only (Article V).
    """
    config_path = root / "project.config.json"
    if not config_path.is_file():
        return {}
    try:
        data = json.loads(config_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}
    return data if isinstance(data, dict) else {}


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="bootstrap.py",
        description="Bootstrap SDD into greenfield or brownfield host projects.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    greenfield = subparsers.add_parser(
        "greenfield",
        help="Copy framework assets and apply an archetype to an empty project.",
        description=(
            "Scaffold .github/ and spec-driven-development/ into a target "
            "directory, then apply the selected archetype constitution."
        ),
    )
    greenfield.add_argument(
        "archetype_name",
        metavar="archetype-name",
        help="Name of the archetype under spec-driven-development/archetypes/.",
    )
    greenfield.add_argument(
        "--project-name",
        required=True,
        help="Host project name used for {{PROJECT_NAME}} placeholders.",
    )
    greenfield.add_argument(
        "--owner",
        required=True,
        help="Human owner used for {{OWNER}} placeholders.",
    )
    greenfield.add_argument(
        "--target",
        default=".",
        help="Existing target directory. Must be empty or contain only .git/ unless --force is used.",
    )
    greenfield.add_argument(
        "--force",
        action="store_true",
        help="Allow overwriting existing framework files in a non-empty target.",
    )

    brownfield = subparsers.add_parser(
        "brownfield",
        help="Inspect an existing git project and stage an SDD constitution proposal.",
        description=(
            "Run a brownfield archaeology pass against an existing git repository, "
            "write .sdd-archaeology.json, and stage a host-specific constitution "
            "proposal under .sdd-proposal/constitution/. Use --apply only after "
            "human review."
        ),
    )
    brownfield.add_argument(
        "target_path",
        metavar="target-path",
        help="Existing git repository to inspect and prepare for SDD adoption.",
    )
    brownfield.add_argument(
        "--owner",
        default=None,
        help="Optional human owner to include in the staged proposal.",
    )
    brownfield_mode = brownfield.add_mutually_exclusive_group()
    brownfield_mode.add_argument(
        "--draft-only",
        action="store_true",
        help="Refresh archaeology and proposal only. This is the default safe workflow.",
    )
    brownfield_mode.add_argument(
        "--apply",
        action="store_true",
        help="After prompting for approval, copy framework assets and the proposed constitution into the target.",
    )

    host_link = subparsers.add_parser(
        "host-link",
        help="Install the framework's .github/ into a host repo via cross-platform symlink/junction (SDD-016).",
        description=(
            "Create a symlink (Linux/macOS) or junction (Windows) at "
            "<target>/.github pointing at this framework's .github/, so a "
            "host repository can adopt SDD without copying the .github/ tree. "
            "Dry-run is the default; pass --apply to mutate the filesystem."
        ),
    )
    host_link.add_argument(
        "--target",
        required=True,
        help="Existing git repository root to install the .github/ link into.",
    )
    host_link.add_argument(
        "--apply",
        action="store_true",
        help="Actually create the link. Without --apply the command is a dry-run.",
    )
    host_link_conflict = host_link.add_mutually_exclusive_group()
    host_link_conflict.add_argument(
        "--backup",
        action="store_true",
        help="If <target>/.github already exists, move it to .github.bak.<timestamp> before linking.",
    )
    host_link_conflict.add_argument(
        "--force",
        action="store_true",
        help="If <target>/.github already exists, recursively delete it before linking (destructive).",
    )
    host_link.add_argument(
        "--gitignore-mode",
        choices=("strict", "prompt", "warn", "skip"),
        default="prompt",
        dest="gitignore_mode",
        help="How to handle .gitignore conflicts (default: prompt).",
    )
    host_link.add_argument(
        "--no-gitignore-check",
        action="store_true",
        dest="no_gitignore_check",
        help="Disable .gitignore protection check entirely.",
    )

    setup = subparsers.add_parser(
        "setup",
        help="Make a fresh clone of this framework runnable in one idempotent step (SDD-045 A-4).",
        description=(
            "Verify Python >= 3.12, create .venv if absent, initialize a fresh "
            "fleet ledger from schema.sql, install the commit-msg hook, optionally "
            "record an owner, then run schema_lint and the test suite. Idempotent."
        ),
    )
    setup.add_argument(
        "--owner",
        default=None,
        help="Optional owner name to record for this checkout.",
    )
    setup.add_argument(
        "--skip-venv",
        action="store_true",
        dest="skip_venv",
        help="Do not create a .venv (use the current interpreter).",
    )
    setup.add_argument(
        "--skip-checks",
        action="store_true",
        dest="skip_checks",
        help="Skip the schema_lint + pytest verification steps.",
    )

    subparsers.add_parser(
        "doctor",
        help="Report framework health on one screen; non-zero exit on any failure (SDD-045 A-5).",
        description=(
            "Run the same checks CI runs: ledger reachable and untracked, "
            "schema_lint clean, governance coherence, no origin tokens, and the "
            "test suite. Emit a one-screen report and exit non-zero on any failure."
        ),
    ).add_argument(
        "--skip-tests",
        action="store_true",
        dest="skip_tests",
        help="Skip the (slow) test-suite check; run the fast checks only.",
    )

    return parser.parse_args(argv)


def fail(message: str, remediation: str) -> None:
    raise BootstrapError(f"{message}\nRemediation: {remediation}")


def validate_target(target: Path, force: bool) -> Path:
    target = target.expanduser().resolve()
    if not target.exists():
        fail(
            f"Target path does not exist: {target}",
            "Create the project directory first, then rerun the bootstrap command.",
        )
    if not target.is_dir():
        fail(
            f"Target path is not a directory: {target}",
            "Pass --target pointing at a directory, not a file.",
        )

    entries = [entry.name for entry in target.iterdir()]
    allowed = {".git"}
    unexpected = [name for name in entries if name not in allowed]
    if unexpected and not force:
        fail(
            f"Target is not empty: {target}",
            "Use an empty repository, a directory containing only .git/, or rerun with --force.",
        )
    return target


def validate_source(root: Path, archetype_name: str) -> Path:
    required_sources = (root / ".github", root / "spec-driven-development")
    for source in required_sources:
        if not source.exists():
            fail(
                f"Framework source directory is missing: {source}",
                "Run this script from an intact checkout of the framework repository.",
            )

    archetype = root / "spec-driven-development" / "archetypes" / archetype_name
    if not archetype.is_dir():
        fail(
            f"Unknown archetype: {archetype_name}",
            "Choose a directory listed under spec-driven-development/archetypes/.",
        )

    constitution = archetype / "constitution"
    missing = [name for name in CONSTITUTION_FILES if not (constitution / name).is_file()]
    if missing:
        fail(
            f"Archetype is missing constitution files: {', '.join(missing)}",
            "Fix the archetype before using it for greenfield bootstrap.",
        )
    return archetype


def copy_directory(source: Path, destination: Path, force: bool) -> None:
    if destination.exists() and not force:
        fail(
            f"Destination already exists: {destination}",
            "Use a clean target or pass --force to overwrite framework-managed files.",
        )
    shutil.copytree(source, destination, dirs_exist_ok=force)


def replace_placeholders(text: str, project_name: str, owner: str, date: str) -> str:
    replacements = {
        "PROJECT_NAME": project_name,
        "OWNER": owner,
        "DATE": date,
    }
    return PLACEHOLDER_PATTERN.sub(lambda match: replacements[match.group(1)], text)


def normalize_frontmatter(text: str, date: str) -> str:
    """Set required constitution frontmatter while preserving the body."""
    body = text
    match = FRONTMATTER_PATTERN.match(text)
    if match:
        body = text[match.end() :]
    frontmatter = (
        "---\n"
        "version: '1.0.0'\n"
        f"ratified: {date}\n"
        f"last_amended: {date}\n"
        "---\n"
    )
    return frontmatter + body.lstrip("\n")


def write_text(path: Path, text: str, force: bool) -> None:
    if path.exists() and not force:
        fail(
            f"Refusing to overwrite existing file: {path}",
            "Use --force only if you intend to replace existing framework-managed content.",
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def apply_constitution(
    archetype: Path,
    target: Path,
    project_name: str,
    owner: str,
    date: str,
    force: bool,
) -> None:
    destination = target / "spec-driven-development" / "constitution"
    for name in CONSTITUTION_FILES:
        source = archetype / "constitution" / name
        text = source.read_text(encoding="utf-8")
        text = replace_placeholders(text, project_name, owner, date)
        text = normalize_frontmatter(text, date)
        write_text(destination / name, text, force=True)


def initialize_backlog(archetype: Path, target: Path, project_name: str, owner: str, date: str, force: bool) -> None:
    backlog_dir = target / "spec-driven-development" / "backlog"
    template_dir = archetype / "backlog"
    fallback = {
        "IDEAS.md": f"# Ideas\n\n<!-- Capture raw ideas for {project_name} here. -->\n",
        "BACKLOG.md": f"# Backlog\n\n<!-- Triage accepted ideas for {project_name} here. -->\n",
    }

    for name in BACKLOG_FILES:
        template = template_dir / name
        if template.is_file():
            text = template.read_text(encoding="utf-8")
            text = replace_placeholders(text, project_name, owner, date)
        else:
            text = fallback[name]
        path = backlog_dir / name
        write_text(path, text, force=True)


def initialize_ledger(target: Path) -> None:
    """Create a fresh fleet ledger from the framework's schema.sql.

    Idempotent: if fleet.db already exists and is non-empty, the existing
    database is left untouched (a teammate's local dispatch state is
    preserved). A fresh or empty file is initialized by executing
    spec-driven-development/ledger/schema.sql, producing the correct tables
    with zero dispatch rows -- replacing the prior empty-file touch().
    """
    ledger = target / "spec-driven-development" / "ledger" / "fleet.db"
    ledger.parent.mkdir(parents=True, exist_ok=True)
    if ledger.exists() and ledger.stat().st_size > 0:
        return
    schema_path = framework_root() / "spec-driven-development" / "ledger" / "schema.sql"
    if not schema_path.is_file():
        fail(
            f"Ledger schema not found: {schema_path}",
            "Restore spec-driven-development/ledger/schema.sql from the framework checkout.",
        )
    schema_sql = schema_path.read_text(encoding="utf-8")
    connection = sqlite3.connect(str(ledger))
    try:
        connection.executescript(schema_sql)
        connection.commit()
    finally:
        connection.close()


def copy_archetype_skills(archetype: Path, target: Path, force: bool) -> None:
    skills = archetype / "skills"
    if not skills.is_dir():
        return
    destination = target / ".github" / "skills" / "domain"
    destination.mkdir(parents=True, exist_ok=True)
    for skill_dir in skills.iterdir():
        if skill_dir.is_dir():
            copy_directory(skill_dir, destination / skill_dir.name, force)



def run_git(target: Path, *args: str, check: bool = True) -> str:
    try:
        result = subprocess.run(["git", "-C", str(target), *args], check=False, capture_output=True, text=True)
    except OSError as exc:
        fail("Unable to run git for brownfield archaeology.", f"Install git and ensure it is on PATH. Details: {exc}")
    if check and result.returncode != 0:
        detail = (result.stderr or result.stdout).strip()
        fail(f"Git command failed in {target}: git {' '.join(args)}", detail or "Verify the target is a valid git repository.")
    return result.stdout.strip()


def validate_brownfield_target(target: Path) -> Path:
    target = target.expanduser().resolve()
    if not target.exists():
        fail(f"Target path does not exist: {target}", "Pass the path to an existing host repository.")
    if not target.is_dir():
        fail(f"Target path is not a directory: {target}", "Pass a directory that is the root of an existing git repository.")
    if run_git(target, "rev-parse", "--is-inside-work-tree", check=False).lower() != "true":
        fail(f"Target is not a git repository: {target}", "Initialize git and create at least one commit before running brownfield bootstrap.")
    repo_root = Path(run_git(target, "rev-parse", "--show-toplevel")).resolve()
    if repo_root != target:
        fail(f"Target must be the git repository root: {target}", f"Rerun against the repository root: {repo_root}")
    run_git(target, "rev-parse", "--verify", "HEAD")
    return target


LANGUAGE_EXTENSIONS = {
    ".py": "Python", ".pyw": "Python", ".ts": "TypeScript", ".tsx": "TypeScript",
    ".js": "JavaScript", ".jsx": "JavaScript", ".mjs": "JavaScript", ".cjs": "JavaScript",
    ".go": "Go", ".java": "Java", ".cs": "C#", ".rb": "Ruby", ".rs": "Rust",
    ".php": "PHP", ".swift": "Swift", ".kt": "Kotlin", ".kts": "Kotlin",
    ".cpp": "C++", ".cc": "C++", ".cxx": "C++", ".c": "C", ".h": "C/C++ Header",
    ".hpp": "C/C++ Header", ".fs": "F#", ".fsx": "F#", ".scala": "Scala",
    ".sh": "Shell", ".ps1": "PowerShell",
}
SKIP_DIRS = {".git", ".hg", ".svn", ".sdd-proposal", ".tox", ".venv", "venv", "node_modules", "dist", "build", "target", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}


def rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def read_if_exists(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore") if path.is_file() else ""
    except OSError:
        return ""


def repo_files(target: Path) -> list[Path]:
    return [p for p in target.rglob("*") if p.is_file() and not any(part in SKIP_DIRS for part in p.relative_to(target).parts)]


def detect_languages(files: list[Path]) -> list[dict[str, object]]:
    counts: dict[str, int] = {}
    for path in files:
        if language := LANGUAGE_EXTENSIONS.get(path.suffix.lower()):
            counts[language] = counts.get(language, 0) + 1
    return [{"language": lang, "file_count": count} for lang, count in sorted(counts.items(), key=lambda item: (-item[1], item[0]))[:5]]


def detect_package_managers(target: Path, files: list[Path]) -> list[dict[str, object]]:
    rels = {rel(path, target) for path in files}
    checks = {
        "Python pyproject": {"pyproject.toml"}, "Python requirements": {"requirements.txt"}, "Python setup": {"setup.py", "setup.cfg"},
        "npm": {"package.json", "package-lock.json"}, "pnpm": {"pnpm-lock.yaml"}, "Yarn": {"yarn.lock"},
        "Go modules": {"go.mod"}, "Cargo": {"Cargo.toml"}, "Bundler": {"Gemfile"}, "Maven": {"pom.xml"}, "Gradle": {"build.gradle", "build.gradle.kts"},
    }
    detected = [{"name": name, "evidence": sorted(r for r in rels if Path(r).name in names)[:10]} for name, names in checks.items() if any(Path(r).name in names for r in rels)]
    dotnet = sorted(r for r in rels if r.endswith(".csproj") or r.endswith(".sln"))
    return detected + ([{"name": ".NET", "evidence": dotnet[:10]}] if dotnet else [])


def add_evidence(bucket: dict[str, set[str]], framework: str, evidence: str) -> None:
    bucket.setdefault(framework, set()).add(evidence)


def detect_test_frameworks(target: Path, files: list[Path]) -> list[dict[str, object]]:
    rels = {rel(path, target) for path in files}
    found: dict[str, set[str]] = {}
    package_json = read_if_exists(target / "package.json").lower()
    pyproject = read_if_exists(target / "pyproject.toml").lower()
    requirements = "\n".join(read_if_exists(path).lower() for path in [target / "requirements.txt", *target.glob("requirements*.txt")])
    java_configs = "\n".join(read_if_exists(target / name).lower() for name in ("pom.xml", "build.gradle", "build.gradle.kts"))
    cs_configs = "\n".join(read_if_exists(path).lower() for path in target.rglob("*.csproj"))
    if "pytest" in pyproject or "pytest" in requirements:
        add_evidence(found, "pytest", "pyproject.toml/requirements.txt")
    if "unittest" in pyproject or any(r.startswith("tests/") and r.endswith(".py") for r in rels):
        add_evidence(found, "pytest", "tests/ directory with Python tests")
    for framework in ("vitest", "jest", "mocha"):
        if framework in package_json:
            add_evidence(found, framework, "package.json")
    config_map = {"vitest": {"vitest.config.ts", "vitest.config.js"}, "jest": {"jest.config.js", "jest.config.ts", "jest.config.cjs"}}
    for framework, names in config_map.items():
        if any(Path(r).name in names for r in rels):
            add_evidence(found, framework, f"{framework} config")
    if read_if_exists(target / "go.mod") or any(r.endswith("_test.go") for r in rels):
        add_evidence(found, "go test", "go.mod or *_test.go")
    if "junit" in java_configs or any(r.startswith("src/test/") and r.endswith(".java") for r in rels):
        add_evidence(found, "junit", "Java test configuration or src/test")
    for framework in ("xunit", "nunit"):
        if framework in cs_configs:
            add_evidence(found, framework, "*.csproj")
    if "rspec" in read_if_exists(target / "Gemfile").lower() or any("spec/" in r and r.endswith("_spec.rb") for r in rels):
        add_evidence(found, "rspec", "Gemfile or spec/ directory")
    if read_if_exists(target / "Cargo.toml") or any(r.endswith(".rs") for r in rels):
        add_evidence(found, "cargo test", "Cargo.toml or Rust sources")
    return [{"name": name, "evidence": sorted(evidence)} for name, evidence in sorted(found.items())]


def detect_ci_systems(target: Path) -> list[dict[str, object]]:
    checks = {"GitHub Actions": target / ".github" / "workflows", "Azure Pipelines": target / "azure-pipelines.yml", "GitLab CI": target / ".gitlab-ci.yml", "Jenkins": target / "Jenkinsfile", "CircleCI": target / ".circleci"}
    return [{"name": name, "evidence": rel(path, target)} for name, path in checks.items() if path.exists()]


def detect_convention_files(target: Path, files: list[Path]) -> list[dict[str, object]]:
    names = {".editorconfig", ".flake8", ".pylintrc", ".ruff.toml", "ruff.toml", "tsconfig.json", "eslint.config.js", "eslint.config.mjs", ".eslintrc", ".eslintrc.json", ".eslintrc.js", "prettier.config.js", "prettier.config.cjs", ".rubocop.yml", "rustfmt.toml", ".gitattributes"}
    detected = [{"name": p.name, "path": rel(p, target)} for p in files if p.name in names or p.name.startswith(".prettierrc")]
    tools = sorted(set(re.findall(r"^\[tool\.([^\]]+)\]", read_if_exists(target / "pyproject.toml"), flags=re.MULTILINE)))
    detected.extend({"name": f"pyproject.toml [tool.{tool}]", "path": "pyproject.toml"} for tool in tools)
    return sorted(detected, key=lambda item: (str(item["path"]), str(item["name"])))


def infer_branching(branch_names: list[str]) -> str:
    normalized = {name.removeprefix("origin/") for name in branch_names if name and name != "HEAD" and not name.endswith("/HEAD")}
    if "develop" in normalized:
        return "git-flow"
    return "trunk-based" if normalized and normalized.issubset({"main", "master"}) else "unknown"


def collect_git_archaeology(target: Path) -> dict[str, object]:
    branches = run_git(target, "branch", "--format=%(refname:short)").splitlines()
    branches += [line for line in run_git(target, "branch", "-r", "--format=%(refname:short)", check=False).splitlines() if line and "->" not in line]
    head = run_git(target, "symbolic-ref", "--short", "HEAD", check=False) or run_git(target, "rev-parse", "--short", "HEAD")
    return {"branch_count": len(set(branches)), "commit_count": int(run_git(target, "rev-list", "--count", "HEAD")), "default_branch": head, "last_commit_date": run_git(target, "log", "-1", "--format=%cs"), "inferred_branching": infer_branching(branches)}


def create_archaeology_report(target: Path) -> dict[str, object]:
    files = repo_files(target)
    git = collect_git_archaeology(target)
    docs = [path.name for path in target.glob("*.md") if path.is_file()]
    priority = {"readme.md": 0, "contributing.md": 1, "architecture.md": 2, "changelog.md": 3}
    report = {
        "target_path": str(target),
        "git": {key: git[key] for key in ("branch_count", "commit_count", "default_branch", "last_commit_date")},
        "languages": detect_languages(files),
        "package_managers": detect_package_managers(target, files),
        "test_frameworks": detect_test_frameworks(target, files),
        "ci_systems": detect_ci_systems(target),
        "convention_files": detect_convention_files(target, files),
        "existing_docs": sorted(docs, key=lambda name: (priority.get(name.lower(), 50), name.lower())),
        "inferred_branching": git["inferred_branching"],
    }
    (target / ".sdd-archaeology.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


def markdown_list(items: list[str], empty: str) -> str:
    return "".join(f"- {item}\n" for item in items) if items else f"- {empty}\n"


def evidence_summary(items: list[dict[str, object]]) -> list[str]:
    lines = []
    for item in items:
        evidence = item.get("evidence")
        evidence_text = ", ".join(str(value) for value in evidence) if isinstance(evidence, list) else str(evidence)
        lines.append(f"{item.get('name')}: {evidence_text}")
    return lines


def proposal_frontmatter(date: str) -> str:
    return "---\nversion: '1.0.0'\n" + f"ratified: {date}\nlast_amended: {date}\nproposal: true\n---\n\n"


def write_proposal_file(proposal_dir: Path, name: str, body: str, date: str) -> None:
    write_text(proposal_dir / name, proposal_frontmatter(date) + body.lstrip("\n"), force=True)


def draft_constitution_proposal(target: Path, report: dict[str, object], owner: str | None, date: str) -> Path:
    """Stage brownfield constitution drafts derived from observed repository evidence."""
    proposal_dir = target / ".sdd-proposal" / "constitution"
    proposal_dir.mkdir(parents=True, exist_ok=True)
    project_name = target.name
    owner_text = owner or "<!-- TODO(human): name the accountable owner for this host project. -->"
    language_lines = [f"{item['language']} ({item['file_count']} files)" for item in report["languages"]]
    package_lines = evidence_summary(report["package_managers"])
    test_lines = evidence_summary(report["test_frameworks"])
    ci_lines = evidence_summary(report["ci_systems"])
    convention_lines = [f"{item['name']} ({item['path']})" for item in report["convention_files"]]
    docs = [f"Top-level doc: {doc}" for doc in report["existing_docs"]]
    principles = [
        "H1: Brownfield changes must preserve existing conventions unless an approved spec explicitly changes them.",
        "H2: Worker agents must use the respect-existing skill before modifying host code.",
    ]
    if any("tests/ directory" in ", ".join(item.get("evidence", [])) for item in report["test_frameworks"]):
        principles.append("H3: Tests belong under the existing tests/ directory pattern unless the host already uses a more specific convention.")
    branch_note = {"trunk-based": "stay trunk-based around the observed main/master long-lived branch model", "git-flow": "respect the observed git-flow model with develop as a long-lived branch"}.get(report["inferred_branching"])
    principles.append(f"H4: Branching should {branch_note}." if branch_note else "H4: <!-- TODO(human): Confirm branching policy; archaeology could not infer it confidently. -->")
    files = {
        "mission.md": f"""# Mission\n\nOwner: {owner_text}\n\nThis proposal was extracted from repository archaeology for `{project_name}` at `{report['target_path']}`.\n\n<!-- TODO(human): Replace this section with the actual mission the existing project already serves. Use README, product docs, and stakeholder language. -->\n\n## Observed Evidence\n\n{markdown_list(docs, 'No top-level Markdown docs detected. Add mission evidence manually.')}## Adoption Note\n\nSDD is being wrapped around the existing project. This constitution should describe current reality before it prescribes changes.\n""",
        "tech-stack.md": f"""# Tech Stack\n\n## Detected Languages\n\n{markdown_list(language_lines, '<!-- TODO(human): Confirm primary implementation language(s). -->')}## Package and Build Inputs\n\n{markdown_list(package_lines, '<!-- TODO(human): Add package manager or build system details. -->')}## Test Frameworks\n\n{markdown_list(test_lines, '<!-- TODO(human): Confirm test runner and baseline test command. -->')}## CI Systems\n\n{markdown_list(ci_lines, '<!-- TODO(human): Document deployment and release automation. -->')}## Convention Files\n\n{markdown_list(convention_lines, '<!-- TODO(human): Add linting, formatting, and style conventions. -->')}""",
        "principles.md": f"""# Principles\n\nFramework Articles I-X are inherited from SDD. The host-specific articles below are proposed from observed repository evidence.\n\n{markdown_list(principles, '<!-- TODO(human): Add host-specific principles. -->')}## Human Review Required\n\n<!-- TODO(human): Confirm each host article, delete anything that does not match current practice, and add missing conventions from team knowledge. -->\n""",
        "roadmap.md": f"""# Roadmap\n\n## Adoption Roadmap\n\n- Review `.sdd-archaeology.json` and this staged proposal with the project owner.\n- Run one small feature or refactor through SDD before broad rollout.\n- Measure friction and capture missing skills or conventions as lesson-capture candidates.\n\n## Current Repository Signals\n\n- Commit count: {report['git']['commit_count']}\n- Current branch: {report['git']['default_branch']}\n- Last commit date: {report['git']['last_commit_date']}\n\n<!-- TODO(human): Add product roadmap items from existing planning artifacts. -->\n""",
        "decision-policy.md": f"""# Decision Policy\n\n## Proposed Policy\n\n- Use existing project decision records if present; otherwise introduce ADRs only for new SDD-era decisions.\n- Do not rewrite previous decisions during adoption. Document observed practice first.\n- Escalate out-of-scope architectural changes to the Architect before implementation.\n\n## Branching Evidence\n\nDetected branching model: `{report['inferred_branching']}`.\n\n<!-- TODO(human): Confirm commit, branch, review, and release policies from team practice. -->\n""",
        "quality-policy.md": f"""# Quality Policy\n\n## Existing Quality Signals\n\n### Test Frameworks\n\n{markdown_list(test_lines, '<!-- TODO(human): Add the test framework and baseline test command. -->')}### CI Systems\n\n{markdown_list(ci_lines, '<!-- TODO(human): Add CI quality gates. -->')}### Convention Files\n\n{markdown_list(convention_lines, '<!-- TODO(human): Add linting and formatting commands. -->')}## Proposed Brownfield Quality Rule\n\nAll SDD work must preserve the existing quality baseline. Workers may add focused tests for their scope, but they must not reorganize unrelated tests, linting, or formatting.\n\n<!-- TODO(human): Record exact commands for test, lint, typecheck, build, and release verification. -->\n""",
    }
    for name, body in files.items():
        write_proposal_file(proposal_dir, name, body, date)
    return proposal_dir.parent


def apply_brownfield_framework(target: Path, proposal_root: Path) -> None:
    root = framework_root()
    for source in (root / ".github", root / "spec-driven-development"):
        if not source.exists():
            fail(f"Framework source directory is missing: {source}", "Run this script from an intact checkout of the framework repository.")
    copy_directory(root / ".github", target / ".github", force=True)
    copy_directory(root / "spec-driven-development", target / "spec-driven-development", force=True)
    destination = target / "spec-driven-development" / "constitution"
    for name in CONSTITUTION_FILES:
        source = proposal_root / "constitution" / name
        if not source.is_file():
            fail(f"Staged proposal is missing {name}: {source}", "Rerun brownfield bootstrap without --apply to refresh the proposal, review it, then apply again.")
        write_text(destination / name, source.read_text(encoding="utf-8"), force=True)
    initialize_ledger(target)


def print_brownfield_next_steps() -> None:
    print()
    print("Next steps:")
    print("(1) Open the Principal Executive Manager.")
    print("(2) Capture your first idea.")
    print("(3) Run /triage. The Executive Manager will route to the PM for grilling.")


def run_brownfield(args: argparse.Namespace) -> None:
    """Run brownfield archaeology, stage a host-derived constitution proposal, and optionally adopt SDD."""
    date = today_iso()
    target = validate_brownfield_target(Path(args.target_path))
    report = create_archaeology_report(target)
    proposal_root = draft_constitution_proposal(target, report, args.owner, date)
    if not args.apply:
        print(f"Archaeology report saved at {target / '.sdd-archaeology.json'}")
        print(f"Proposal staged at {proposal_root}. Review, edit, then run `python bootstrap.py brownfield {target} --apply` to adopt.")
        print_brownfield_next_steps()
        return
    answer = input(f"Apply SDD framework files and staged constitution into {target}? Type 'yes' to continue: ").strip().lower()
    if answer != "yes":
        fail("Brownfield apply was not approved.", f"Review the staged proposal at {proposal_root}, then rerun with --apply when ready.")
    apply_brownfield_framework(target, proposal_root)
    print(f"SDD brownfield bootstrap applied to {target}.")
    print(f"Archaeology report: {target / '.sdd-archaeology.json'}")
    print(f"Constitution source proposal: {proposal_root / 'constitution'}")
    print_brownfield_next_steps()


def run_greenfield(args: argparse.Namespace) -> None:
    root = framework_root()
    date = today_iso()
    target = validate_target(Path(args.target), args.force)
    archetype = validate_source(root, args.archetype_name)

    copy_directory(root / ".github", target / ".github", args.force)
    copy_directory(root / "spec-driven-development", target / "spec-driven-development", args.force)
    apply_constitution(archetype, target, args.project_name, args.owner, date, args.force)
    copy_archetype_skills(archetype, target, args.force)
    initialize_backlog(archetype, target, args.project_name, args.owner, date, args.force)
    initialize_ledger(target)

    print(f"SDD greenfield bootstrap complete for {args.project_name}.")
    print(f"Target: {target}")
    print(f"Archetype: {args.archetype_name}")
    print("\nNext 3 steps:")
    print("1. Open VS Code and select the Principal Executive Manager agent.")
    print("2. Capture your first product idea in plain language.")
    print("3. Ask the Product Manager to run /triage on that idea.")


# --------------------------------------------------------------------------- #
# host-link (SDD-016 + SDD-017) -- install framework's .github/ into a host
# repo via cross-platform symlink/junction. Dry-run by default.
# --------------------------------------------------------------------------- #


def resolve_framework_github() -> Path:
    """Return absolute path to the framework's .github/ directory."""
    return (framework_root() / ".github").resolve()


def validate_host_link_target(target: Path) -> Path:
    """Resolve and confirm the target is a real git repository.

    Reuses the brownfield repo-root guard. Returns the resolved absolute path.
    """
    return validate_brownfield_target(target)


def _windows_junction(link_path: Path, source: Path) -> None:
    """Create a Windows junction at link_path -> source via cmd /c mklink /J."""
    result = subprocess.run(
        ["cmd", "/c", "mklink", "/J", str(link_path), str(source)],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        detail = (result.stderr or result.stdout or "").strip()
        fail(
            f"mklink /J fallback failed for {link_path} -> {source}",
            f"Run with developer mode enabled or use a Windows account with the privilege. Details: {detail}",
        )


def install_link(framework_github: Path, link_path: Path) -> str:
    """Create a symlink at link_path -> framework_github.

    Prefer os.symlink. On OSError (typically Windows without developer mode
    or symlink privilege), fall back to a Windows junction via mklink /J.

    Returns "symlink" or "junction" depending on which path succeeded.
    """
    if link_path.exists() or link_path.is_symlink():
        fail(
            f"Link path already exists: {link_path}",
            "Pre-install conflict handling is the caller's job; resolve and retry.",
        )
    try:
        os.symlink(str(framework_github), str(link_path), target_is_directory=True)
        return "symlink"
    except OSError:
        # Windows fallback: junction. Junctions require absolute paths.
        _windows_junction(link_path, framework_github.resolve())
        return "junction"


def _timestamp() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%d-%H%M%S")


def handle_existing_github(link_path: Path, mode: str) -> str | None:
    """Resolve an existing <target>/.github per the conflict mode.

    mode in {"abort", "backup", "force"}.

    - "abort": raise BootstrapError naming --backup and --force.
      Distinguishes stale symlinks from real directories (SDD-029).
    - "backup": move link_path to .github.bak.<timestamp>; return the backup path.
    - "force": recursively remove link_path; return None.
    """
    if mode == "abort":
        if link_path.is_symlink() and not link_path.exists():
            fail(
                f"Stale symlink at {link_path} (target no longer exists).",
                "Remove the broken symlink and re-run: del or rm the link, then retry.",
            )
        elif link_path.is_dir() and not link_path.is_symlink():
            fail(
                f"Directory already exists at {link_path}.",
                "Re-run with --backup to move it aside, or --force to overwrite (destructive).",
            )
        else:
            fail(
                f"Host .github/ already exists at {link_path}",
                "Re-run with --backup to move it aside, or --force to overwrite (destructive).",
            )
    if mode == "backup":
        backup = link_path.parent / f".github.bak.{_timestamp()}"
        shutil.move(str(link_path), str(backup))
        return str(backup)
    if mode == "force":
        if link_path.is_symlink() or link_path.is_file():
            link_path.unlink()
        else:
            shutil.rmtree(link_path)
        return None
    fail(
        f"Unknown conflict mode: {mode}",
        "Internal error; expected one of abort/backup/force.",
    )
    return None  # unreachable


def format_dry_run_report(target: Path, link_path: Path,
                          framework_github: Path, existing: bool,
                          mode: str) -> str:
    """Build the human-readable dry-run summary."""
    lines = [
        "host-link dry-run (no filesystem changes will occur):",
        f"  target host repo : {target}",
        f"  link path        : {link_path}",
        f"  framework source : {framework_github}",
    ]
    if existing:
        if mode == "abort":
            lines.append("  existing .github: present -- would ABORT (no flag)")
        elif mode == "backup":
            lines.append("  existing .github: present -- would MOVE to .github.bak.<timestamp>")
        elif mode == "force":
            lines.append("  existing .github: present -- would RECURSIVELY DELETE")
    else:
        lines.append("  existing .github: absent -- would create link directly")
    lines.append("Re-run with --apply to perform the action.")
    return "\n".join(lines)


# --------------------------------------------------------------------------- #
# SDD-027: Host .gitignore protection
# --------------------------------------------------------------------------- #

_MANIFEST_PATH = Path(__file__).resolve().with_name("host_gitignore_manifest.json")


def _load_gitignore_manifest(path: Path | None = None) -> dict:
    """Load the host gitignore manifest JSON."""
    manifest_path = path or _MANIFEST_PATH
    if not manifest_path.is_file():
        fail(
            f"Gitignore manifest not found: {manifest_path}",
            "Ensure host_gitignore_manifest.json exists alongside bootstrap.py.",
        )
    return json.loads(manifest_path.read_text(encoding="utf-8"))


def _parse_host_gitignore(gitignore_path: Path) -> set[str]:
    """Read host .gitignore, return set of non-comment, non-empty patterns."""
    if not gitignore_path.is_file():
        return set()
    patterns: set[str] = set()
    for line in gitignore_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            patterns.add(stripped)
    return patterns


def _check_gitignore_coverage(
    host_root: Path,
    manifest: dict,
) -> tuple[list[str], list[str]]:
    """Compare manifest against host's ignore rules.

    Returns (missing_ignores, over_ignores).
    - missing_ignores: must_be_ignored patterns not in host .gitignore
    - over_ignores: must_be_tracked paths that git says are ignored
    """
    gitignore_patterns = _parse_host_gitignore(host_root / ".gitignore")

    missing_ignores: list[str] = []
    for pattern in manifest.get("must_be_ignored", []):
        if pattern not in gitignore_patterns:
            missing_ignores.append(pattern)

    over_ignores: list[str] = []
    for path in manifest.get("must_be_tracked", []):
        try:
            result = subprocess.run(
                ["git", "-C", str(host_root), "check-ignore", "-q", path],
                capture_output=True, text=True,
            )
            if result.returncode == 0:
                # git says this path IS ignored -- that's a problem
                over_ignores.append(path)
        except OSError:
            pass  # git not available; skip live check

    return missing_ignores, over_ignores


def _check_host_gitignore(
    host_root: Path,
    mode: str = "prompt",
    manifest: dict | None = None,
) -> bool:
    """Check host .gitignore for SDD compatibility.

    Returns True if OK to proceed, False if should abort.
    """
    if mode == "skip":
        return True

    gitignore_path = host_root / ".gitignore"
    if not gitignore_path.is_file():
        print("WARNING: No .gitignore found in host repository.", file=sys.stderr)
        print("Recommended content:", file=sys.stderr)
        if manifest is None:
            manifest = _load_gitignore_manifest()
        for pattern in manifest.get("must_be_ignored", []):
            print(f"  {pattern}", file=sys.stderr)
        if mode == "strict":
            return False
        return True

    if manifest is None:
        manifest = _load_gitignore_manifest()

    missing, over = _check_gitignore_coverage(host_root, manifest)

    if not missing and not over:
        return True

    if missing:
        print("Missing .gitignore rules (must_be_ignored):", file=sys.stderr)
        for pattern in missing:
            print(f"  - {pattern}", file=sys.stderr)
    if over:
        print("Over-aggressive .gitignore rules (must_be_tracked paths are ignored):", file=sys.stderr)
        for path in over:
            print(f"  - {path}", file=sys.stderr)

    if mode == "strict":
        return False
    # prompt and warn modes: report but proceed
    return True


def run_host_link(args: argparse.Namespace) -> None:
    """Dispatcher for `bootstrap.py host-link --target <host> [...]`."""
    target = validate_host_link_target(Path(args.target))
    framework_github = resolve_framework_github()
    if not framework_github.is_dir():
        fail(
            f"Framework .github/ not found at {framework_github}",
            "Run this script from an intact checkout of the framework repository.",
        )

    # SDD-027: gitignore protection check
    gitignore_mode = getattr(args, "gitignore_mode", "prompt")
    no_gitignore_check = getattr(args, "no_gitignore_check", False)
    if not no_gitignore_check and args.apply:
        ok = _check_host_gitignore(target, mode=gitignore_mode)
        if not ok:
            print("ERROR: .gitignore check failed. Aborting host-link.", file=sys.stderr)
            fail(
                "Host .gitignore protection check failed.",
                f"Fix the reported issues and re-run, or use --gitignore-mode skip to bypass.",
            )

    link_path = target / ".github"

    existing = link_path.exists() or link_path.is_symlink()
    if args.backup:
        mode = "backup"
    elif args.force:
        mode = "force"
    else:
        mode = "abort"

    if not args.apply:
        print(format_dry_run_report(target, link_path, framework_github,
                                    existing, mode))
        return

    if existing:
        backup_path = handle_existing_github(link_path, mode)
    else:
        backup_path = None

    kind = install_link(framework_github, link_path)

    print(f"host-link complete: {kind} created at {link_path} -> {framework_github}")
    if backup_path:
        print(f"  previous .github/ preserved at: {backup_path}")
    print("\nNext steps for the host operator:")
    print("  - Inspect .github/ from the host root; framework agents/skills are now visible.")
    print("  - Review docs/HOST-INTEGRATION.md for the CI/Actions trade-off and rollback procedure.")


# --------------------------------------------------------------------------- #
# SDD-045 A-4 / A-5: setup (one-command clone-and-run) and doctor (health check)
# --------------------------------------------------------------------------- #


def install_commit_msg_hook(root: Path) -> str:
    """Install the commit-msg hook into root/.git/hooks. Idempotent.

    Returns a short status string. A no-op (with a note) when there is no
    .git directory (e.g. running setup before `git init`).
    """
    source = root / "spec-driven-development" / "cli" / "hooks" / "commit-msg"
    git_hooks = root / ".git" / "hooks"
    if not source.is_file():
        return f"commit-msg hook source missing ({source}); skipped"
    if not (root / ".git").is_dir():
        return "no .git directory; commit-msg hook skipped"
    git_hooks.mkdir(parents=True, exist_ok=True)
    destination = git_hooks / "commit-msg"
    shutil.copyfile(str(source), str(destination))
    try:
        destination.chmod(0o755)
    except OSError:
        pass
    return f"commit-msg hook installed at {destination}"


def write_owner_config(root: Path, owner: str | None) -> str:
    """Record the owner name when provided. Idempotent.

    When owner is None the step is skipped (this framework checkout is already
    personalized via its constitution). When provided, the name is written to
    spec-driven-development/exec/.owner.
    """
    if owner is None:
        return "owner config skipped (constitution already personalizes ownership)"
    owner_file = root / "spec-driven-development" / "exec" / ".owner"
    owner_file.parent.mkdir(parents=True, exist_ok=True)
    owner_file.write_text(f"{owner}\n", encoding="utf-8")
    return f"owner recorded at {owner_file}"


def _run_check(root: Path, args: list[str]) -> tuple[int, str]:
    """Run a checker subprocess from root; return (exit_code, combined_output)."""
    result = subprocess.run(
        [sys.executable, *args],
        cwd=str(root), capture_output=True, text=True, check=False,
    )
    return result.returncode, (result.stdout + result.stderr).strip()


def run_setup(root: Path, owner: str | None = None, *,
              make_venv: bool = True, run_checks: bool = True) -> int:
    """Idempotently make a fresh clone of the framework runnable (A-4).

    Returns 0 on success, 1 on any failed step.
    """
    print("SDD setup -- making this clone runnable")

    if sys.version_info < (3, 12):
        print(
            f"ERROR: Python 3.12+ required; found {sys.version_info.major}."
            f"{sys.version_info.minor}.",
            file=sys.stderr,
        )
        print("Remediation: install Python 3.12 or newer and re-run setup.", file=sys.stderr)
        return 1
    print(f"  [1/6] Python {sys.version_info.major}.{sys.version_info.minor} OK")

    venv_dir = root / ".venv"
    if not make_venv or venv_dir.exists():
        reason = "already present" if venv_dir.exists() else "skipped (--skip-venv)"
        print(f"  [2/6] .venv {reason}")
    else:
        code, output = _run_check(root, ["-m", "venv", str(venv_dir)])
        if code != 0:
            print(f"ERROR: failed to create .venv: {output}", file=sys.stderr)
            return 1
        print(f"  [3/6] .venv created at {venv_dir}")

    try:
        initialize_ledger(root)
    except BootstrapError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print("  [3/6] fleet ledger initialized from schema.sql")

    print(f"  [4/6] {install_commit_msg_hook(root)}")
    print(f"  [5/6] {write_owner_config(root, owner)}")

    if not run_checks:
        print("  [6/6] schema_lint + tests skipped (--skip-checks)")
        print("\nSetup complete (checks skipped). Talk to the Executive Manager to begin.")
        return 0

    schema_lint = root / "spec-driven-development" / "cli" / "schema_lint.py"
    code, output = _run_check(root, [str(schema_lint)])
    if code != 0:
        print(f"ERROR: schema_lint failed:\n{output}", file=sys.stderr)
        return 1
    print("  [6/6] schema_lint clean; running test suite...")

    code, output = _run_check(
        root, ["-m", "pytest", "spec-driven-development", "--tb=no", "-q"]
    )
    if code != 0:
        print(f"ERROR: test suite failed:\n{output}", file=sys.stderr)
        return 1
    summary = output.splitlines()[-1] if output else ""
    print(f"        tests passed: {summary}")
    print("\nSetup complete. Open VS Code, select the Executive Manager agent, and begin.")
    return 0


def current_pi_name(root: Path) -> str | None:
    """Return the highest-numbered active PI name, or None (SDD-046 / R-B1-5).

    Read-only: globs ``sprints/PI-*/CURRENT_PI.md`` and selects markers whose
    status is active. Touches no Article X function.
    """
    sprints = root / "spec-driven-development" / "sprints"
    if not sprints.is_dir():
        return None
    candidates: list[Path] = []
    for marker in sprints.glob("PI-*/CURRENT_PI.md"):
        text = marker.read_text(encoding="utf-8", errors="replace")
        if re.search(r"status:\s*active", text, re.IGNORECASE) or "Status: **ACTIVE**" in text:
            candidates.append(marker)
    if not candidates:
        return None

    def _pi_number(marker: Path) -> int:
        name = marker.parent.name  # "PI-7"
        try:
            return int(name.split("-", 1)[1])
        except (IndexError, ValueError):
            return -1

    return sorted(candidates, key=_pi_number, reverse=True)[0].parent.name


def check_current_pi_dispatch_rows(root: Path) -> tuple[str, bool, str] | None:
    """Return a (label, ok, detail) check tuple, or None to skip (SDD-046 / B-1).

    None when there is no active PI marker (doctor stays green). Otherwise the
    check passes only when the ledger has >=1 dispatch row for the active PI.
    """
    pi = current_pi_name(root)
    if pi is None:
        return None
    label = "current-PI dispatch rows"
    ledger = root / "spec-driven-development" / "ledger" / "fleet.db"
    if not ledger.is_file():
        return (label, False, f"{pi}: fleet.db missing")
    try:
        connection = sqlite3.connect(str(ledger))
        try:
            cursor = connection.execute(
                "SELECT COUNT(*) FROM dispatches WHERE pi = ?", (pi,)
            )
            count = cursor.fetchone()[0]
        finally:
            connection.close()
    except sqlite3.Error as exc:
        return (label, False, f"{pi}: cannot query dispatches: {exc}")
    if count > 0:
        return (label, True, f"{pi}: {count} row(s)")
    return (label, False, f"{pi}: 0 dispatch rows logged (dogfood the ledger)")


def run_doctor(root: Path, *, run_tests: bool = True) -> int:
    """Report framework health on one screen; non-zero exit on any failure (A-5).

    The set of checks is the single source of truth for what CI runs.
    """
    import origin_lint
    import governance_check

    is_framework = root == framework_root()
    checks: list[tuple[str, bool, str]] = []

    # (a) ledger reachable AND untracked.
    ledger = root / "spec-driven-development" / "ledger" / "fleet.db"
    tracked = origin_lint.find_tracked_dbs(root)
    if tracked:
        checks.append(("ledger untracked", False,
                       f"tracked db(s): {', '.join(tracked)} (run git rm --cached)"))
    elif not ledger.is_file():
        checks.append(("ledger reachable", False, "fleet.db missing (run setup)"))
    else:
        try:
            connection = sqlite3.connect(str(ledger))
            try:
                connection.execute("SELECT COUNT(*) FROM dispatches")
            finally:
                connection.close()
            checks.append(("ledger reachable + untracked", True, "ok"))
        except sqlite3.Error as exc:
            checks.append(("ledger reachable", False, f"cannot query fleet.db: {exc}"))

    # (b) schema_lint clean (framework checkout only). --check-orphans enforces
    #     the SDD-047 D-1 lock: every non-domain skill must be wired to an
    #     agent, prompt, or instruction.
    if is_framework:
        code, output = _run_check(
            root,
            [str(root / "spec-driven-development" / "cli" / "schema_lint.py"),
             "--check-orphans"],
        )
        checks.append(("schema_lint clean", code == 0,
                       "ok" if code == 0 else output.splitlines()[-1] if output else "failed"))

    # (c) governance coherence + article-range match.
    gov_ok, gov_findings = governance_check.check_governance(root)
    checks.append(("governance coherent", gov_ok,
                   "ok" if gov_ok else "; ".join(gov_findings)))

    # (d) no origin tokens (config-aware tightened denylist: owner name + origin tokens).
    findings = origin_lint.scan_origin_tokens(root, origin_lint.load_config_denylist(root))
    checks.append(("origin tokens absent", not findings,
                   "ok" if not findings else f"{len(findings)} token(s) found"))

    # (d2) session-start docs fresh: no stale hardcoded article/current-PI count
    #      in the four onboarding docs (SDD-051B). Framework checkout only.
    if is_framework:
        import staledoc_lint
        stale = staledoc_lint.scan(root)
        checks.append(("session-start docs fresh", not stale,
                       "ok" if not stale else f"{len(stale)} stale count(s)"))

    # (e) tests pass.
    if run_tests and is_framework:
        code, output = _run_check(
            root, ["-m", "pytest", "spec-driven-development", "--tb=no", "-q"]
        )
        checks.append(("tests pass", code == 0,
                       output.splitlines()[-1] if output else ("ok" if code == 0 else "failed")))

    # (f) current-PI dispatch rows: promises must become real ledger entries.
    if is_framework:
        pi_check = check_current_pi_dispatch_rows(root)
        if pi_check is not None:
            checks.append(pi_check)

    # (g) tdd gate: production changes must be test-paired (SDD-046 B-2 rule 1).
    if is_framework:
        import tdd_gate_check
        changed = tdd_gate_check.changed_files(root)
        gate_ok, offenders = tdd_gate_check.evaluate(changed)
        checks.append((
            "tdd gate",
            gate_ok,
            "ok" if gate_ok else f"untested production change(s): {', '.join(offenders)}",
        ))

    # (h) DONE completeness: closed features of the active PI must be complete.
    if is_framework:
        import done_check
        pi = current_pi_name(root)
        if pi is not None:
            problems = done_check.audit_pi(
                root / "spec-driven-development" / "specs", pi
            )
            checks.append((
                "DONE completeness",
                not problems,
                "ok" if not problems else "; ".join(problems),
            ))
        else:
            checks.append(("DONE completeness", True, "no active PI to audit"))

    print("SDD doctor -- framework health")
    all_ok = True
    for label, ok, detail in checks:
        marker = "PASS" if ok else "FAIL"
        print(f"  [{marker}] {label}: {detail}")
        all_ok = all_ok and ok
    print("\nAll checks passed." if all_ok else "\nOne or more checks FAILED.")
    return 0 if all_ok else 1


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])
    try:
        if args.command == "greenfield":
            run_greenfield(args)
            return 0
        if args.command == "brownfield":
            run_brownfield(args)
            return 0
        if args.command == "host-link":
            run_host_link(args)
            return 0
        if args.command == "setup":
            return run_setup(
                framework_root(),
                owner=args.owner,
                make_venv=not args.skip_venv,
                run_checks=not args.skip_checks,
            )
        if args.command == "doctor":
            return run_doctor(framework_root(), run_tests=not args.skip_tests)
        fail(f"Unsupported command: {args.command}", "Run python bootstrap.py --help for valid commands.")
    except BootstrapError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    except OSError as exc:
        print(f"ERROR: File operation failed: {exc}", file=sys.stderr)
        print("Remediation: Check permissions, paths, and whether files are open in another process.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
