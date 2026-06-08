#!/usr/bin/env python3
"""Mirror SDD tasks into issue tracker payloads."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib import error, parse, request


GENERATED_START = "<!-- sdd-task:start -->"
GENERATED_END = "<!-- sdd-task:end -->"
FORBIDDEN_STATUS_CONFLICTS = {
    ("pending", "closed"),
    ("in-progress", "closed"),
    ("blocked", "closed"),
    ("done", "open"),
    ("done", "reopened"),
}


class TaskSyncError(Exception):
    """Expected task sync failure with a human-readable message."""


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def stable_fingerprint(text: str) -> str:
    total = sum((index + 1) * ord(char) for index, char in enumerate(text))
    return f"sdd-v1:{len(text)}:{total}"


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        raise TaskSyncError(f"cannot read {path}: {exc}") from exc


def write_text(path: Path, text: str) -> None:
    try:
        path.write_text(text, encoding="utf-8")
    except OSError as exc:
        raise TaskSyncError(f"cannot write {path}: {exc}") from exc


def ensure_spec_dir(spec_dir: Path) -> Path:
    resolved = spec_dir.resolve()
    if not (resolved / "tasks.md").is_file():
        raise TaskSyncError(f"missing tasks.md in spec dir: {resolved}")
    if "spec-driven-development" not in resolved.parts or "specs" not in resolved.parts:
        raise TaskSyncError("generated sync state must live under spec-driven-development/specs/")
    return resolved


def parse_frontmatter_value(text: str, key: str, default: str) -> str:
    match = re.search(rf"^\s*{re.escape(key)}\s*:\s*['\"]?([^'\"\n]+)", text, re.MULTILINE)
    return match.group(1).strip() if match else default


def parse_spec_id(spec_dir: Path) -> str:
    spec_path = spec_dir / "spec.md"
    if not spec_path.is_file():
        return spec_dir.name
    text = read_text(spec_path)
    explicit = re.search(r"Spec ID:\s*(SDD-\d+)", text)
    if explicit:
        return explicit.group(1)
    return parse_frontmatter_value(text, "id", spec_dir.name)


def parse_list_block(block: str) -> list[str]:
    values: list[str] = []
    for line in block.splitlines():
        stripped = line.strip()
        if stripped.startswith("- ["):
            values.append(stripped)
        elif stripped.startswith("- "):
            values.append(stripped[2:].strip())
    return values


def parse_task_fields(block: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    for line in block.splitlines():
        match = re.match(r"^\*\*(?P<key>[^*]+)\*\*:\s*(?P<value>.*)$", line.strip())
        if match:
            fields[match.group("key").strip().lower()] = match.group("value").strip()
    return fields


def section_between(block: str, heading: str, next_heading: str | None = None) -> str:
    pattern = rf"^### {re.escape(heading)}\s*$"
    match = re.search(pattern, block, re.MULTILINE)
    if not match:
        return ""
    start = match.end()
    if next_heading:
        next_match = re.search(rf"^### {re.escape(next_heading)}\s*$", block[start:], re.MULTILINE)
        if next_match:
            return block[start:start + next_match.start()].strip()
    generic_next = re.search(r"^###\s+", block[start:], re.MULTILINE)
    if generic_next:
        return block[start:start + generic_next.start()].strip()
    return block[start:].strip()


def parse_tasks(spec_dir: Path) -> list[dict[str, Any]]:
    spec_dir = ensure_spec_dir(spec_dir)
    text = read_text(spec_dir / "tasks.md")
    matches = list(re.finditer(r"^## Task (?P<id>T-[\w-]+):\s*(?P<title>.+)$", text, re.MULTILINE))
    if not matches:
        raise TaskSyncError("no task headings found in tasks.md")

    tasks: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, match in enumerate(matches):
        task_id = match.group("id").strip()
        if task_id in seen:
            raise TaskSyncError(f"duplicate task ID: {task_id}")
        seen.add(task_id)
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        block = text[match.end():end]
        fields = parse_task_fields(block)
        description = section_between(block, "Description", "Acceptance Criteria")
        acceptance = parse_list_block(section_between(block, "Acceptance Criteria", "Verification"))
        verification = section_between(block, "Verification")
        tasks.append({
            "id": task_id,
            "title": match.group("title").strip(),
            "status": fields.get("status", "pending"),
            "story": fields.get("story", ""),
            "files": fields.get("files", ""),
            "blocked_files": fields.get("files blocked", ""),
            "description": description,
            "acceptance_criteria": acceptance,
            "verification": verification,
        })
    return tasks


def issue_state_for_task(task: dict[str, Any]) -> str:
    return "closed" if task.get("status") == "done" else "open"


def render_issue_body(task: dict[str, Any], spec_dir: Path, spec_id: str) -> str:
    lines = [
        GENERATED_START,
        f"Source spec: `{spec_dir.as_posix()}`",
        f"Spec ID: `{spec_id}`",
        f"Task ID: `{task['id']}`",
        f"Local status: `{task.get('status', 'pending')}`",
        "",
        "## Description",
        task.get("description") or "No description provided.",
        "",
        "## File Scope",
        task.get("files") or "Not specified.",
        "",
        "## Acceptance Criteria",
    ]
    criteria = task.get("acceptance_criteria") or []
    lines.extend(criteria if criteria else ["- Not specified."])
    lines.extend([
        "",
        "## Verification",
        task.get("verification") or "Not specified.",
        GENERATED_END,
    ])
    return "\n".join(lines).strip() + "\n"


def render_payload(task: dict[str, Any], spec_dir: Path, spec_id: str, provider: str) -> dict[str, Any]:
    body = render_issue_body(task, spec_dir, spec_id)
    labels = ["sdd", spec_id.lower(), provider, f"task:{task['id'].lower()}", f"status:{task.get('status', 'pending')}"]
    return {
        "title": f"[{task['id']}] {task['title']}",
        "body": body,
        "labels": labels,
        "state": issue_state_for_task(task),
        "task_id": task["id"],
    }


def replace_generated_region(existing: str, generated: str) -> str:
    if GENERATED_START not in existing or GENERATED_END not in existing:
        return generated
    start = existing.index(GENERATED_START)
    end = existing.index(GENERATED_END) + len(GENERATED_END)
    return existing[:start] + generated.strip() + existing[end:]


def load_issue_map(spec_dir: Path, spec_id: str, provider: str, repo: str) -> dict[str, Any]:
    path = spec_dir / "issue-map.json"
    if not path.exists():
        return {"schema_version": 1, "spec_id": spec_id, "provider": provider, "repository": repo, "tasks": {}}
    try:
        data = json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        raise TaskSyncError(f"invalid issue-map.json: {exc}") from exc
    data.setdefault("schema_version", 1)
    data.setdefault("spec_id", spec_id)
    data.setdefault("provider", provider)
    data.setdefault("repository", repo)
    data.setdefault("tasks", {})
    return data


def write_issue_map(spec_dir: Path, data: dict[str, Any]) -> None:
    write_text(spec_dir / "issue-map.json", json.dumps(data, indent=2, sort_keys=True) + "\n")


def resolve_github_token(environ: dict[str, str] | None = None) -> str:
    env = environ if environ is not None else os.environ
    token = env.get("GITHUB_TOKEN") or env.get("GH_TOKEN")
    if not token:
        raise TaskSyncError("GitHub apply mode requires GITHUB_TOKEN or GH_TOKEN")
    return token


class GitHubProvider:
    """GitHub Issues provider using urllib transport."""

    def __init__(self, repo: str, token: str, transport: Any | None = None) -> None:
        self.repo = repo
        self.token = token
        self.transport = transport or request.urlopen

    def _request(self, method: str, path: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        url = f"https://api.github.com/repos/{self.repo}{path}"
        data = None if payload is None else json.dumps(payload, sort_keys=True).encode("utf-8")
        req = request.Request(
            url,
            data=data,
            method=method,
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
                "User-Agent": "sdd-taskstoissues",
            },
        )
        try:
            with self.transport(req) as response:
                raw = response.read().decode("utf-8")
        except error.URLError as exc:
            raise TaskSyncError(f"GitHub request failed: {exc.reason}") from exc
        return json.loads(raw or "{}")

    def create_issue(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self._request("POST", "/issues", {
            "title": payload["title"],
            "body": payload["body"],
            "labels": payload["labels"],
        })

    def update_issue(self, remote_id: str, payload: dict[str, Any], existing_body: str = "") -> dict[str, Any]:
        body = replace_generated_region(existing_body, payload["body"]) if existing_body else payload["body"]
        return self._request("PATCH", f"/issues/{parse.quote(str(remote_id))}", {
            "title": payload["title"],
            "body": body,
            "labels": payload["labels"],
            "state": payload["state"],
        })

    def get_issue(self, remote_id: str) -> dict[str, Any]:
        return self._request("GET", f"/issues/{parse.quote(str(remote_id))}")


class AdoDryRunProvider:
    """ADO-compatible no-network provider boundary for fast-follow tests."""

    required_env = ("ADO_PAT", "ADO_ORG_URL", "ADO_PROJECT")

    def __init__(self) -> None:
        self.created: list[dict[str, Any]] = []

    def create_issue(self, payload: dict[str, Any]) -> dict[str, Any]:
        self.created.append(payload)
        return {"id": len(self.created), "html_url": f"ado://work-item/{len(self.created)}", "state": payload["state"]}

    def update_issue(self, remote_id: str, payload: dict[str, Any], existing_body: str = "") -> dict[str, Any]:
        return {"id": remote_id, "html_url": f"ado://work-item/{remote_id}", "state": payload["state"]}

    def get_issue(self, remote_id: str) -> dict[str, Any]:
        return {"id": remote_id, "html_url": f"ado://work-item/{remote_id}", "state": "open"}


def make_provider(provider: str, repo: str, apply: bool) -> Any:
    if provider == "github":
        if not apply:
            return None
        return GitHubProvider(repo, resolve_github_token())
    if provider == "ado":
        return AdoDryRunProvider()
    raise TaskSyncError(f"unsupported provider: {provider}")


def normalize_remote_id(response: dict[str, Any]) -> str:
    return str(response.get("number") or response.get("id") or "")


def normalize_remote_url(response: dict[str, Any]) -> str:
    return str(response.get("html_url") or response.get("url") or "")


def push_tasks(spec_dir: Path, provider_name: str, repo: str, apply: bool = False,
               provider: Any | None = None, now: str | None = None) -> dict[str, Any]:
    spec_dir = ensure_spec_dir(spec_dir)
    spec_id = parse_spec_id(spec_dir)
    tasks = parse_tasks(spec_dir)
    payloads = [render_payload(task, spec_dir, spec_id, provider_name) for task in tasks]
    if not apply:
        return {"mode": "dry-run", "provider": provider_name, "repository": repo, "issues": payloads}

    provider = provider or make_provider(provider_name, repo, apply=True)
    mapping = load_issue_map(spec_dir, spec_id, provider_name, repo)
    timestamp = now or utc_now()
    summary = {"created": [], "updated": [], "unchanged": []}
    for task, payload in zip(tasks, payloads):
        fingerprint = stable_fingerprint(payload["body"])
        existing = mapping["tasks"].get(task["id"])
        if existing and existing.get("sync_fingerprint") == fingerprint:
            summary["unchanged"].append(task["id"])
            continue
        if existing:
            remote = provider.get_issue(existing["remote_id"])
            response = provider.update_issue(existing["remote_id"], payload, remote.get("body", ""))
            summary["updated"].append(task["id"])
        else:
            response = provider.create_issue(payload)
            summary["created"].append(task["id"])
        mapping["tasks"][task["id"]] = {
            "provider": provider_name,
            "remote_id": normalize_remote_id(response),
            "url": normalize_remote_url(response),
            "last_synced_at": timestamp,
            "last_seen_remote_status": str(response.get("state", payload["state"])),
            "sync_fingerprint": fingerprint,
        }
    write_issue_map(spec_dir, mapping)
    summary["mode"] = "apply"
    return summary


def detect_conflicts(spec_dir: Path, provider_name: str, repo: str, provider: Any | None = None) -> list[dict[str, str]]:
    spec_dir = ensure_spec_dir(spec_dir)
    spec_id = parse_spec_id(spec_dir)
    tasks = {task["id"]: task for task in parse_tasks(spec_dir)}
    mapping = load_issue_map(spec_dir, spec_id, provider_name, repo)
    provider = provider or make_provider(provider_name, repo, apply=True)
    conflicts: list[dict[str, str]] = []
    for task_id, entry in mapping.get("tasks", {}).items():
        if task_id not in tasks:
            continue
        remote = provider.get_issue(entry["remote_id"])
        local_status = str(tasks[task_id].get("status", "pending"))
        remote_status = str(remote.get("state", entry.get("last_seen_remote_status", "open")))
        if (local_status, remote_status) in FORBIDDEN_STATUS_CONFLICTS:
            conflicts.append({
                "task_id": task_id,
                "local_status": local_status,
                "remote_status": remote_status,
                "remote_url": str(entry.get("url", "")),
                "conflict_type": "status-drift",
                "recommended_action": "Update tasks.md through the SDD lifecycle or reopen/close the remote issue to match local authority.",
            })
    if conflicts:
        write_conflict_report(spec_dir, conflicts)
    return conflicts


def write_conflict_report(spec_dir: Path, conflicts: list[dict[str, str]]) -> None:
    lines = ["# Issue Sync Conflicts", "", "| Task | Local | Remote | URL | Type | Recommended Action |", "|------|-------|--------|-----|------|--------------------|"]
    for conflict in conflicts:
        lines.append(
            f"| {conflict['task_id']} | {conflict['local_status']} | {conflict['remote_status']} | "
            f"{conflict['remote_url']} | {conflict['conflict_type']} | {conflict['recommended_action']} |"
        )
    write_text(spec_dir / "issue-conflicts.md", "\n".join(lines) + "\n")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="taskstoissues.py", description="Mirror SDD tasks into issue tracker payloads.")
    sub = parser.add_subparsers(dest="command", required=True)
    push = sub.add_parser("push", help="Render or apply task-to-issue sync.")
    push.add_argument("--spec-dir", required=True)
    push.add_argument("--provider", choices=["github", "ado"], default="github")
    push.add_argument("--repo", required=True)
    push.add_argument("--apply", action="store_true", help="Perform provider writes. Default is dry-run.")
    push.add_argument("--dry-run", action="store_true", help="Render planned writes without network calls.")

    conflicts = sub.add_parser("conflicts", help="Check mapped remote issue status for conflicts.")
    conflicts.add_argument("--spec-dir", required=True)
    conflicts.add_argument("--provider", choices=["github", "ado"], default="github")
    conflicts.add_argument("--repo", required=True)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])
    try:
        if args.command == "push":
            result = push_tasks(Path(args.spec_dir), args.provider, args.repo, apply=bool(args.apply))
            print(json.dumps(result, indent=2, sort_keys=True))
            return 0
        if args.command == "conflicts":
            conflicts = detect_conflicts(Path(args.spec_dir), args.provider, args.repo)
            if conflicts:
                print(f"conflicts: {len(conflicts)}")
                return 2
            print("conflicts: 0")
            return 0
    except TaskSyncError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 1


if __name__ == "__main__":
    sys.exit(main())#!/usr/bin/env python3
"""Mirror locked SDD tasks into issue trackers through stdlib providers."""
