#!/usr/bin/env python3
"""
Bootstrap helper for greenfield SDD host projects.

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
import re
import shutil
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


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="bootstrap.py",
        description="Bootstrap SDD into a greenfield host project.",
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
    ledger = target / "spec-driven-development" / "ledger" / "fleet.db"
    ledger.parent.mkdir(parents=True, exist_ok=True)
    ledger.touch(exist_ok=True)


def copy_archetype_skills(archetype: Path, target: Path, force: bool) -> None:
    skills = archetype / "skills"
    if not skills.is_dir():
        return
    destination = target / ".github" / "skills" / "domain"
    destination.mkdir(parents=True, exist_ok=True)
    for skill_dir in skills.iterdir():
        if skill_dir.is_dir():
            copy_directory(skill_dir, destination / skill_dir.name, force)


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


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])
    try:
        if args.command == "greenfield":
            run_greenfield(args)
            return 0
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
