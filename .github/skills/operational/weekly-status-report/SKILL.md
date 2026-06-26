---
name: weekly-status-report
description: "Generate or update the weekly 1:1 status report for the Evolving Multi-Agent Framework. Scans git commits, code changes, test results, specs, sessions, sprints, and documents to auto-populate a structured report with progress summary, blockers, meetings, and scorecard. Appends a new week section to the existing report file."
argument-hint: "Optionally specify the week date range, e.g. 'May 22-28, 2026'. Defaults to the current week."
license: MIT
metadata:
  author: emf-framework
  version: '1.0'
  origin: PI-2 operational need (2026-05-21)
---

# Weekly Status Report

Generate the weekly 1:1 status report for the Evolving Multi-Agent Framework project. Appends a new week section at the top of the report file, preserving all previous weeks.

## When to Use

- End of each work week (or start of the following week) to prepare for the manager 1:1.
- When the user says: "weekly report", "status report", "weekly update", "1:1 report", "update the report", "get me this week's report".
- When invoking `/weekly-status-report` or loading this skill by name.

## Report File

```
spec-driven-development/docs/1_1_STATUS_REPORT_SDD.md
```

New sections are prepended after the top-level heading so the most recent week is always first.

## Data Collection Protocol

Gather ALL of the following before writing. Run these steps in order:

### Step 1 -- Determine the reporting week

- If the user specifies a date range, use it.
- Otherwise, compute the Monday-to-Sunday window that contains today's date.
- Identify the prior week's end date for the "Progress since last week (DATE)" header.

### Step 2 -- Git history

```powershell
cd <your-repo-root>
git log --oneline --after="YYYY-MM-DD" --before="YYYY-MM-DD" --format="%h %ad %s" --date=short
```

- Count total commits in the window.
- Group commits by theme (sprint, feature, fix, docs, chore).
- Note any new ADRs, specs, or session files created.

### Step 3 -- Code changes

```powershell
git diff --stat <first_commit_before_window>..HEAD | Select-Object -Last 3
```

- Capture files changed, insertions, deletions.
- Note any new CLI tools, agents, skills, or prompts added.

### Step 4 -- Test results

```powershell
python -m pytest spec-driven-development/ -v --tb=short 2>&1 | Select-Object -Last 5
```

- Record total tests passing, duration, and any failures.
- Compare to the previous week's count from the prior report section.

### Step 5 -- Asset counts

```powershell
(Get-ChildItem -Path ".github/agents" -Filter "*.agent.md").Count
(Get-ChildItem -Path ".github/skills" -Recurse -Filter "SKILL.md").Count
(Get-ChildItem -Path ".github/prompts" -Filter "*.prompt.md").Count
(Get-ChildItem -Path "spec-driven-development/docs/ADR" -Filter "*.md" | Where-Object { $_.Name -ne "TEMPLATE.md" }).Count
```

### Step 6 -- CLI code metrics

```powershell
Get-ChildItem -Path "spec-driven-development/cli" -Filter "*.py" -Recurse |
  Where-Object { $_.Name -notlike "test_*" -and $_.Name -ne "__init__.py" } |
  ForEach-Object { (Get-Content $_.FullName | Measure-Object -Line).Lines } |
  Measure-Object -Sum
```

### Step 7 -- Spec and sprint status

- Read `spec-driven-development/constitution/roadmap.md` for current PI status.
- Scan `spec-driven-development/specs/` directories for feature stage (check for RETRO.md = DONE, tasks.md = TASKS, spec.md = SPEC, etc.).
- Read `spec-driven-development/sessions/SESSION-MEMORY.md` for in-flight work and blockers.
- Read any sprint retro files created this week.

### Step 8 -- Lessons and retrospectives

- Check `spec-driven-development/sprints/PI-*/lessons.md` for new lessons added this week.
- Note any lessons shipped vs still open.

### Step 9 -- Previous week's scorecard

- Read the most recent existing section in the report file.
- Extract the "This Week" column values -- these become "Last Week" in the new section.

## Report Section Format

Use this exact structure for the new week section. Match the style of the existing sections in the file.

```markdown
---

## Week of {Month} {start_day}-{end_day}, {year}

Date: {Month} {end_day}, {year} | Owner: {owner} | Branch: master at {short_sha} ({total_commits} commits)

### Progress since last week ({Month} {prior_week_end_day})

{Group commits into logical sprint/feature blocks. Each block:}

**{Sprint/Feature Name} ({STATUS}, {date range or date})**
- {file}: {what changed and why}. {test count if relevant}.
- {next bullet}...

{Repeat for each logical block of work.}

### Blockers / Next Steps

| Item | Status | Blocker |
|------|--------|---------|
| {item} | {status} | {blocker or "None"} |

### Key Meetings This Week

| Meeting | Date | Key Outcome |
|---------|------|-------------|
| {meeting or "_(No external meetings -- framework internal work)_"} | {date} | {outcome} |

### Scorecard

| Metric | Last Week ({date}) | This Week ({date}) | Delta |
|--------|-------------------|-------------------|-------|
| Total commits | {N} | {N} | {+/-N} |
| Tests passing | {N} | {N} | {+/-N} |
| PI status | {text} | {text} | {text} |
| CLI tools operational | {N} | {N} | {+/-N} |
| CLI code lines | {N} | {N} | {+/-N} |
| Agent definitions | {N} | {N} | {+/-N} |
| Skills | {N} | {N} | {+/-N} |
| Slash commands | {N} | {N} | {+/-N} |
| ADRs | {N} | {N} | {+/-N} |
| Features DONE through SDD | {N} | {N} | {+/-N} |
| Fleet dispatch success rate | {%} | {%} | {text} |
| Lessons captured | {N} | {N} | {+/-N} |
| Specs in flight | {N} | {N} | {+/-N} |
| {any new metric relevant this week} | {N/A} | {value} | {New} |
```

## Scorecard Metrics Reference

These are the standard metrics. Include all of them every week. Add new rows when a new category of asset appears (e.g. "Specialists promoted", "Azure deployments").

| Metric | How to Compute |
|--------|---------------|
| Total commits | `git log --oneline \| Measure-Object -Line` |
| Tests passing | pytest output last line |
| PI status | roadmap.md current PI label |
| CLI tools operational | Count of non-test, non-init .py files in cli/ |
| CLI code lines | Sum of lines in CLI source files |
| Agent definitions | .agent.md count in .github/agents/ |
| Skills | SKILL.md count in .github/skills/ |
| Slash commands | .prompt.md count in .github/prompts/ |
| ADRs | .md count in docs/ADR/ minus TEMPLATE.md |
| Features DONE through SDD | Spec dirs with RETRO.md present |
| Fleet dispatch success rate | From ledger or retro |
| Lessons captured | Count of LESSON-NNN entries across all PI lessons files |
| Specs in flight | Spec dirs without RETRO.md |

## Writing Rules

1. All data must come from actual git log, test output, file system, and artifacts -- never from memory or docs that may be stale.
2. Delta column shows `+N`, `-N`, `Unchanged`, or `New` (for first-time metrics).
3. Do not invent meetings. If there were none, use the placeholder row.
4. Group commits into logical blocks (sprints, features, fixes). Do not list every commit individually.
5. Keep sprint/feature descriptions concise: file name, what changed, why, test count.
6. Blockers table must include every known blocker, even if carried over from prior week.
7. Preserve all prior week sections in the file -- only prepend the new section.

## Process

1. Run Steps 1-9 above to collect all data.
2. Read the existing report file to get the prior week's scorecard values.
3. Compose the new section using the format above.
4. Insert the new section after the top-level `# Weekly Status Report` heading and the `---` separator, before the first existing `## Week of` section.
5. Save the file.
6. Report: "Weekly status report updated for {week range}. {N} commits, {N} tests passing, {summary of key deliverables}."
