#!/usr/bin/env python3
"""No-network A/B harness for model-upgrade proposals."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


REQUIRED_KINDS = {"clarify", "spec", "plan-tasks", "implement-report", "review-report"}


class ModelUpgradeError(Exception):
    """Expected model-upgrade harness failure."""


def slug(value: str) -> str:
    lowered = value.strip().lower()
    safe = re.sub(r"[^a-z0-9]+", "-", lowered).strip("-")
    safe = re.sub(r"-+", "-", safe)
    if not safe:
        raise ModelUpgradeError("model identifier must contain at least one ASCII letter or digit")
    return safe


def branch_name(old: str, new: str) -> str:
    return f"model-upgrade/{slug(old)}-to-{slug(new)}"


def load_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ModelUpgradeError(f"missing file: {path}") from exc


def validate_workload(data: dict[str, Any]) -> list[dict[str, Any]]:
    scenarios = data.get("scenarios")
    if not isinstance(scenarios, list):
        raise ModelUpgradeError("workload must contain scenarios list")
    kinds = {str(item.get("kind")) for item in scenarios if isinstance(item, dict)}
    missing = REQUIRED_KINDS - kinds
    if missing:
        raise ModelUpgradeError(f"workload missing scenario kinds: {', '.join(sorted(missing))}")
    return scenarios


def calculate_cost(pricing: dict[str, Any], output_data: dict[str, Any], model_key: str) -> dict[str, float]:
    model = pricing["models"][model_key]
    usage = output_data.get("usage", {})
    input_tokens = float(usage.get("input_tokens", 0))
    output_tokens = float(usage.get("output_tokens", 0))
    per_run = (input_tokens / 1_000_000.0 * float(model["input_per_1m"])) + (output_tokens / 1_000_000.0 * float(model["output_per_1m"]))
    fixed = pricing.get("fixed_costs", {})
    return {
        "per_run": round(per_run, 6),
        "one_time": round(float(fixed.get("one_time", 0.0)), 6),
        "recurring_monthly": round(float(fixed.get("monthly", 0.0)), 6),
    }


def quality_summary(outputs: dict[str, Any]) -> dict[str, Any]:
    rows = outputs.get("outputs", [])
    if not isinstance(rows, list) or not rows:
        raise ModelUpgradeError("output file must contain non-empty outputs list")
    validation_pass = all(bool(row.get("validation_pass")) for row in rows)
    spec_quality = sum(float(row.get("spec_quality", 0)) for row in rows) / len(rows)
    commit_quality = sum(float(row.get("commit_quality", 0)) for row in rows) / len(rows)
    report_quality = sum(float(row.get("report_quality", 0)) for row in rows) / len(rows)
    ambiguous = any(bool(row.get("ambiguous_win")) for row in rows)
    return {
        "validation_pass": validation_pass,
        "spec_quality": round(spec_quality, 3),
        "commit_quality": round(commit_quality, 3),
        "report_quality": round(report_quality, 3),
        "ambiguous_owner_approval_required": ambiguous,
    }


def recommendation(old_quality: dict[str, Any], new_quality: dict[str, Any], cost_delta: float) -> str:
    if not new_quality["validation_pass"]:
        return "reject"
    old_score = old_quality["spec_quality"] + old_quality["commit_quality"] + old_quality["report_quality"]
    new_score = new_quality["spec_quality"] + new_quality["commit_quality"] + new_quality["report_quality"]
    if new_quality["ambiguous_owner_approval_required"] or cost_delta > 0.01:
        return "owner-review"
    if new_score >= old_score:
        return "approve"
    return "reject"


def compare(fixture: Path, pricing_path: Path, old_output: Path, new_output: Path, out_dir: Path) -> dict[str, Any]:
    workload = load_json(fixture)
    scenarios = validate_workload(workload)
    pricing = load_json(pricing_path)
    old_data = load_json(old_output)
    new_data = load_json(new_output)
    old_cost = calculate_cost(pricing, old_data, "old")
    new_cost = calculate_cost(pricing, new_data, "new")
    old_quality = quality_summary(old_data)
    new_quality = quality_summary(new_data)
    cost_delta = round(new_cost["per_run"] - old_cost["per_run"], 6)
    result = {
        "schema_version": 1,
        "scenario_count": len(scenarios),
        "currency": pricing.get("currency", "USD"),
        "costs": {
            "old_model": old_cost,
            "new_model": new_cost,
            "delta_per_run": cost_delta,
            "one_time": new_cost["one_time"],
            "recurring_monthly": new_cost["recurring_monthly"],
        },
        "quality": {
            "old_model": old_quality,
            "new_model": new_quality,
        },
    }
    result["recommendation"] = recommendation(old_quality, new_quality, cost_delta)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "comparison.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out_dir / "comparison.md").write_text(render_markdown(result), encoding="utf-8")
    return result


def render_markdown(result: dict[str, Any]) -> str:
    lines = [
        "# Model Upgrade Comparison",
        "",
        f"- Recommendation: {result['recommendation']}",
        f"- Currency: {result['currency']}",
        f"- Scenario count: {result['scenario_count']}",
        "",
        "## Costs",
        f"- Old model per-run: {result['costs']['old_model']['per_run']}",
        f"- New model per-run: {result['costs']['new_model']['per_run']}",
        f"- Delta per-run: {result['costs']['delta_per_run']}",
        f"- One-time: {result['costs']['one_time']}",
        f"- Recurring monthly: {result['costs']['recurring_monthly']}",
        "",
        "## Quality",
        f"- Old validation pass: {result['quality']['old_model']['validation_pass']}",
        f"- New validation pass: {result['quality']['new_model']['validation_pass']}",
        f"- New spec-quality checklist score: {result['quality']['new_model']['spec_quality']}",
        f"- New commit/report quality delta marker: {result['quality']['new_model']['commit_quality']} / {result['quality']['new_model']['report_quality']}",
        f"- Ambiguous owner approval required: {result['quality']['new_model']['ambiguous_owner_approval_required']}",
        "",
    ]
    return "\n".join(lines)


def cmd_branch_name(args: argparse.Namespace) -> int:
    print(branch_name(args.old, args.new))
    return 0


def cmd_compare(args: argparse.Namespace) -> int:
    result = compare(Path(args.fixture), Path(args.pricing), Path(args.old_output), Path(args.new_output), Path(args.out_dir))
    print(json.dumps({"recommendation": result["recommendation"], "report": str(Path(args.out_dir) / "comparison.json")}, sort_keys=True))
    return 1 if result["recommendation"] == "owner-review" else 0


def cmd_summarize(args: argparse.Namespace) -> int:
    report = load_json(Path(args.report))
    print(render_markdown(report))
    return 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="model_upgrade.py", description="Compare captured model-upgrade outputs without network calls.")
    sub = parser.add_subparsers(dest="command", required=True)
    branch = sub.add_parser("branch-name", help="Render safe model-upgrade branch name")
    branch.add_argument("--old", required=True)
    branch.add_argument("--new", required=True)
    branch.set_defaults(func=cmd_branch_name)
    compare_parser = sub.add_parser("compare", help="Compare captured old/new model outputs")
    compare_parser.add_argument("--fixture", required=True)
    compare_parser.add_argument("--pricing", required=True)
    compare_parser.add_argument("--old-output", required=True)
    compare_parser.add_argument("--new-output", required=True)
    compare_parser.add_argument("--out-dir", required=True)
    compare_parser.set_defaults(func=cmd_compare)
    summarize = sub.add_parser("summarize", help="Render Markdown summary from comparison.json")
    summarize.add_argument("--report", required=True)
    summarize.set_defaults(func=cmd_summarize)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    try:
        args = parse_args(argv if argv is not None else sys.argv[1:])
        return int(args.func(args))
    except (ModelUpgradeError, OSError, json.JSONDecodeError, KeyError, TypeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())