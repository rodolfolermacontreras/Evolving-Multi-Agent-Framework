#!/usr/bin/env python3
"""QA validation runner -- two-stage review automation (SDD-004).

Subcommands:
    check    Run spec-compliance and code-quality checks against a feature.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


# -- Exception -------------------------------------------------------------- #


class QAError(Exception):
    """Expected QA validation failure."""


# -- Stage 1: Spec Compliance ----------------------------------------------- #


def check_validation(validation_path: Path) -> dict:
    """Parse validation.md checkboxes. Return checked/unchecked counts."""
    if not validation_path.is_file():
        raise QAError(f"validation.md not found: {validation_path}")

    text = validation_path.read_text(encoding="utf-8")
    checked = 0
    unchecked = 0
    unchecked_items: list[str] = []

    for line in text.splitlines():
        stripped = line.strip()
        if re.match(r"^-\s+\[x\]", stripped, re.IGNORECASE):
            checked += 1
        elif re.match(r"^-\s+\[\s\]", stripped):
            unchecked += 1
            unchecked_items.append(stripped)

    return {
        "checked": checked,
        "unchecked": unchecked,
        "unchecked_items": unchecked_items,
    }


def check_ac_crossref(spec_path: Path, validation_path: Path) -> dict:
    """Cross-reference AC identifiers from spec against validation proves."""
    if not spec_path.is_file():
        raise QAError(f"spec.md not found: {spec_path}")
    if not validation_path.is_file():
        raise QAError(f"validation.md not found: {validation_path}")

    # Extract AC numbers from spec.md acceptance criteria section
    spec_text = spec_path.read_text(encoding="utf-8")
    spec_acs: set[str] = set()
    in_ac_section = False
    for line in spec_text.splitlines():
        if re.match(r"^##\s+Acceptance Criteria", line, re.IGNORECASE):
            in_ac_section = True
            continue
        if in_ac_section and re.match(r"^##\s+", line):
            break
        if in_ac_section:
            m = re.match(r"^\s*(\d+)\.\s+", line)
            if m:
                spec_acs.add(f"AC{m.group(1)}")

    # Parse validation.md "proves ACn" references
    val_text = validation_path.read_text(encoding="utf-8")
    covered_acs: set[str] = set()
    test_to_acs: dict[str, list[str]] = {}

    for line in val_text.splitlines():
        # Match lines like: - [x] `test_foo`: proves AC1, AC2.
        m = re.match(r"^-\s+\[.\]\s+`([^`]+)`.*?proves\s+(.*)", line, re.IGNORECASE)
        if m:
            test_name = m.group(1)
            ac_refs = re.findall(r"AC(\d+)", m.group(2), re.IGNORECASE)
            ac_ids = [f"AC{n}" for n in ac_refs]
            test_to_acs[test_name] = ac_ids
            covered_acs.update(ac_ids)

    missing = sorted(spec_acs - covered_acs,
                     key=lambda x: int(re.search(r"\d+", x).group()))
    # EXTRA: tests that reference ACs not in the spec
    all_referenced = set()
    for acs in test_to_acs.values():
        all_referenced.update(acs)
    extra_acs = sorted(all_referenced - spec_acs,
                       key=lambda x: int(re.search(r"\d+", x).group()))

    return {
        "spec_acs": sorted(spec_acs,
                           key=lambda x: int(re.search(r"\d+", x).group())),
        "covered_acs": sorted(covered_acs,
                              key=lambda x: int(re.search(r"\d+", x).group())),
        "missing": missing,
        "extra": extra_acs,
    }


def check_task_status(tasks_path: Path) -> dict:
    """Parse tasks.md table rows. Flag tasks not marked done."""
    if not tasks_path.is_file():
        raise QAError(f"tasks.md not found: {tasks_path}")

    text = tasks_path.read_text(encoding="utf-8")
    lines = text.strip().splitlines()

    # Find header row
    header_idx = None
    for i, line in enumerate(lines):
        if line.strip().startswith("|") and re.search(r"task\s*id", line, re.IGNORECASE):
            header_idx = i
            break
    if header_idx is None:
        raise QAError(f"No task table header in {tasks_path}")

    headers = [h.strip().lower() for h in lines[header_idx].strip().strip("|").split("|")]

    # Find relevant column indices
    id_col = None
    status_col = None
    desc_col = None
    for i, h in enumerate(headers):
        if "task" in h and "id" in h:
            id_col = i
        elif "status" in h:
            status_col = i
        elif "desc" in h:
            desc_col = i

    if id_col is None or status_col is None:
        raise QAError(f"Cannot find Task ID or Status column in {tasks_path}")

    not_done: list[dict] = []
    # Skip header and separator rows
    for line in lines[header_idx + 2:]:
        if not line.strip().startswith("|"):
            continue
        cols = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cols) <= max(id_col, status_col):
            continue
        task_id = cols[id_col].strip()
        status = cols[status_col].strip().lower()
        if not task_id or task_id.startswith("-"):
            continue
        if status != "done":
            desc = cols[desc_col].strip() if desc_col is not None and desc_col < len(cols) else ""
            not_done.append({"task_id": task_id, "status": status, "description": desc})

    return {"not_done": not_done}


# -- Stage 2: Code Quality ------------------------------------------------- #


def scan_bare_except(impl_paths: list[Path]) -> list[dict]:
    """Scan Python files for bare ``except:`` statements."""
    findings: list[dict] = []
    pattern = re.compile(r"^\s*except\s*:")
    for p in impl_paths:
        if not p.is_file():
            continue
        for i, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
            if pattern.match(line):
                findings.append({
                    "file": str(p),
                    "line_no": i,
                    "line": line.strip(),
                    "severity": "CRITICAL",
                })
    return findings


def scan_debug_prints(impl_paths: list[Path]) -> list[dict]:
    """Scan Python files for print() calls not writing to stderr."""
    findings: list[dict] = []
    pattern = re.compile(r"\bprint\s*\(")
    stderr_pattern = re.compile(r"file\s*=\s*(sys\.)?stderr")
    for p in impl_paths:
        if not p.is_file():
            continue
        for i, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
            if pattern.search(line) and not stderr_pattern.search(line):
                findings.append({
                    "file": str(p),
                    "line_no": i,
                    "line": line.strip(),
                    "severity": "WARNING",
                })
    return findings


# -- Report renderer -------------------------------------------------------- #


def render_report(validation: dict, crossref: dict, task_status: dict,
                  bare_except: list[dict], debug_prints: list[dict]) -> str:
    """Render the two-stage review report as Markdown."""
    lines: list[str] = []

    # ---- Stage 1 ----
    lines.append("## Stage 1: Spec Compliance")
    lines.append("")

    # Validation checkboxes
    lines.append("### Validation Checkboxes")
    lines.append(f"- Checked: {validation['checked']}")
    lines.append(f"- Unchecked: {validation['unchecked']}")
    if validation["unchecked_items"]:
        lines.append("- Unchecked items:")
        for item in validation["unchecked_items"]:
            lines.append(f"  - {item}")
    lines.append("")

    # AC cross-reference
    lines.append("### AC Cross-Reference")
    lines.append(f"- Spec ACs: {', '.join(crossref['spec_acs']) or 'none'}")
    lines.append(f"- Covered ACs: {', '.join(crossref['covered_acs']) or 'none'}")
    if crossref["missing"]:
        lines.append(f"- MISSING: {', '.join(crossref['missing'])}")
    if crossref["extra"]:
        lines.append(f"- EXTRA: {', '.join(crossref['extra'])}")
    if not crossref["missing"] and not crossref["extra"]:
        lines.append("- All ACs covered. No extra references.")
    lines.append("")

    # Task status
    lines.append("### Task Status")
    if task_status["not_done"]:
        lines.append("- Tasks not done:")
        for t in task_status["not_done"]:
            lines.append(f"  - {t['task_id']}: {t['description']} (status: {t['status']})")
    else:
        lines.append("- All tasks done.")
    lines.append("")

    # ---- Stage 2 ----
    lines.append("## Stage 2: Code Quality")
    lines.append("")

    # Bare except
    lines.append("### Bare Except Scan")
    if bare_except:
        for f in bare_except:
            lines.append(f"- [{f['severity']}] {f['file']}:{f['line_no']} -- {f['line']}")
    else:
        lines.append("- No bare except statements found.")
    lines.append("")

    # Debug prints
    lines.append("### Debug Print Scan")
    if debug_prints:
        for f in debug_prints:
            lines.append(f"- [{f['severity']}] {f['file']}:{f['line_no']} -- {f['line']}")
    else:
        lines.append("- No debug print statements found.")
    lines.append("")

    return "\n".join(lines)


# -- CLI wiring ------------------------------------------------------------- #


def parse_args(argv: list[str]) -> argparse.Namespace:
    """Build and parse CLI arguments."""
    parser = argparse.ArgumentParser(
        prog="qa.py",
        description="QA validation runner -- two-stage review automation.",
    )
    sub = parser.add_subparsers(dest="command")

    check_p = sub.add_parser("check", help="Run spec-compliance and code-quality checks.")
    check_p.add_argument(
        "--feature", required=True, type=Path,
        help="Path to the feature spec directory (must contain spec.md, validation.md, tasks.md).",
    )
    check_p.add_argument(
        "--impl", type=Path, default=None,
        help="Path to the implementation file or directory to scan.",
    )
    check_p.add_argument(
        "--test", type=Path, default=None,
        help="Path to the test file (currently unused; reserved for future expansion).",
    )

    return parser.parse_args(argv)


def _resolve_impl_files(impl_arg: Path | None, feature_dir: Path) -> list[Path]:
    """Resolve implementation file paths from --impl or default."""
    if impl_arg is None:
        return []
    if impl_arg.is_file():
        return [impl_arg]
    if impl_arg.is_dir():
        return sorted(impl_arg.glob("*.py"))
    return []


def main(argv: list[str] | None = None) -> int:
    """Entry point for the QA validation runner."""
    if argv is None:
        argv = sys.argv[1:]

    args = parse_args(argv)

    if args.command is None:
        print("ERROR: no subcommand given. Use 'check'.", file=sys.stderr)
        return 2

    feature = Path(args.feature)
    if not feature.is_dir():
        print(f"ERROR: feature directory not found: {feature}", file=sys.stderr)
        return 2

    impl_files = _resolve_impl_files(args.impl, feature)

    # ---- Stage 1 ----
    stage1_fail = False
    try:
        validation = check_validation(feature / "validation.md")
    except QAError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        validation = {"checked": 0, "unchecked": 0, "unchecked_items": []}
        stage1_fail = True

    try:
        crossref = check_ac_crossref(feature / "spec.md", feature / "validation.md")
    except QAError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        crossref = {"spec_acs": [], "covered_acs": [], "missing": [], "extra": []}
        stage1_fail = True

    try:
        task_status = check_task_status(feature / "tasks.md")
    except QAError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        task_status = {"not_done": []}
        stage1_fail = True

    if validation["unchecked"] > 0:
        stage1_fail = True
    if crossref["missing"]:
        stage1_fail = True
    if task_status["not_done"]:
        stage1_fail = True

    # ---- Stage 2 ----
    bare_except = scan_bare_except(impl_files)
    debug_prints = scan_debug_prints(impl_files)

    # ---- Report ----
    report = render_report(validation, crossref, task_status, bare_except, debug_prints)
    print(report)

    if stage1_fail:
        print("NOT COMPLIANT")
        return 1

    print("COMPLIANT")
    return 0


if __name__ == "__main__":
    sys.exit(main())
