---
id: SDD-20260607DEDUP-tasks
type: tasks
status: active
owner: principal-software-developer
updated: 2026-06-07
feature: 2026-06-07-cross-feature-dedup
---

# Task List: Cross-Feature Deduplication (SDD-020)

- Feature: SDD-020
- Sprint: PI-5 / Sprint 2 (= overall Sprint 6)
- Author: Principal Software Developer
- Date: 2026-06-07
- Test baseline: >= 213

---

## Task T-020-01: Implement dedup scanner (corpus loader)

**Story**: [R1] Scan scope covers BACKLOG, IDEAS, and open spec dirs
**Type**: [S] sequential
**Execution**: [AFK] autonomous
**Size**: M
**Files**: cli/dedup.py
**Files Blocked**: cli/fleet.py, cli/bootstrap.py, constitution/principles.md
**Depends on**: NONE

### Description

Create `cli/dedup.py` with a corpus loader that:
- Reads `backlog/BACKLOG.md` and `backlog/IDEAS.md` (parse entries with
  titles and optional frontmatter IDs).
- Scans `specs/**/spec.md` where frontmatter `status` is NOT `done` or
  `archived` (open spec dirs only).
- Returns a list of corpus entries, each with: source path, title,
  frontmatter ID (if present), problem-statement text.

### Acceptance Criteria

- [ ] Loads entries from BACKLOG.md and IDEAS.md
- [ ] Loads open spec dirs (status != done/archived)
- [ ] Excludes closed/archived spec dirs
- [ ] Returns structured corpus entries with source, title, ID, text

### Verification

```
python -m pytest cli/test_dedup.py -k "corpus" -v --tb=short
```

---

## Task T-020-02: Implement three-layer match heuristic

**Story**: [R2] HARD/SOFT/ADVISORY heuristic layers
**Type**: [S] sequential
**Execution**: [AFK] autonomous
**Size**: L
**Files**: cli/dedup.py
**Files Blocked**: cli/fleet.py, cli/bootstrap.py, constitution/principles.md
**Depends on**: T-020-01

### Description

Implement three match layers in `cli/dedup.py`:
- **Layer 1 (HARD)**: exact frontmatter `id` collision. Import
  `parse_frontmatter` from `cli/schema_lint.py`. Two entries with the
  same `id` value are a HARD match.
- **Layer 2 (SOFT)**: title fuzzy match via `difflib.SequenceMatcher`.
  Ratio >= 0.8 is a SOFT match.
- **Layer 3 (ADVISORY)**: keyword Jaccard on tokenized problem-statement
  text. Tokenize by whitespace + lowercase, compute Jaccard similarity.
  Threshold TBD in tests (starting point: 0.3).

Each layer returns a list of match pairs with the match tier.

### Acceptance Criteria

- [ ] Layer 1: exact ID collision detected as HARD
- [ ] Layer 1: different IDs not flagged
- [ ] Layer 2: titles with ratio >= 0.8 detected as SOFT
- [ ] Layer 2: dissimilar titles not flagged
- [ ] Layer 3: overlapping keyword sets detected as ADVISORY
- [ ] Layer 3: disjoint keyword sets not flagged
- [ ] Negative controls for each layer pass

### Verification

```
python -m pytest cli/test_dedup.py -k "heuristic or layer" -v --tb=short
```

---

## Task T-020-03: Implement tiered action handler

**Story**: [R4] HARD blocks, SOFT prompts, ADVISORY warns
**Type**: [S] sequential
**Execution**: [AFK] autonomous
**Size**: M
**Files**: cli/dedup.py
**Files Blocked**: cli/fleet.py, cli/bootstrap.py, constitution/principles.md
**Depends on**: T-020-02

### Description

Implement tiered action handling:
- **HARD**: print overlap details, exit code 1. Blocks triage/clarify.
- **SOFT**: print overlap details, prompt owner to decide (merge /
  keep-both / discard / rewrite), exit code 2 if unresolved.
- **ADVISORY**: print overlap details as warning, exit code 0.

In non-interactive mode (`--no-prompt`), SOFT acts like HARD (exit 1).

### Acceptance Criteria

- [ ] HARD match -> exit 1 with overlap details
- [ ] SOFT match -> prompt owner; unresolved -> exit 2
- [ ] ADVISORY match -> exit 0 with warning
- [ ] `--no-prompt` mode: SOFT acts like HARD (exit 1)

### Verification

```
python -m pytest cli/test_dedup.py -k "action or tier" -v --tb=short
```

---

## Task T-020-04: Implement CLI entry point with argparse

**Story**: [R3, O2] Standalone CLI with main(argv)
**Type**: [S] sequential
**Execution**: [AFK] autonomous
**Size**: M
**Files**: cli/dedup.py
**Files Blocked**: cli/fleet.py, cli/bootstrap.py, constitution/principles.md
**Depends on**: T-020-03

### Description

Add argparse-based CLI entry point to `cli/dedup.py`:
- `dedup.py scan [--scope backlog|specs|all] [--format table|json]`
- `dedup.py scan --candidate "<title or path>"` -- check a single
  candidate against the corpus.
- `--no-prompt` flag for CI/automation (SOFT -> HARD behavior).
- `main(argv)` signature per CLI-PATTERN.md.
- Exit codes: 0 = clean, 1 = HARD overlap, 2 = SOFT overlap.

### Acceptance Criteria

- [ ] `main(argv)` signature; callable from subprocess
- [ ] `--scope` filters corpus correctly
- [ ] `--format json` produces valid JSON output
- [ ] `--format table` produces human-readable table
- [ ] `--candidate` checks single item against corpus
- [ ] `--no-prompt` flag works
- [ ] `--help` produces clean output

### Verification

```
python -m pytest cli/test_dedup.py -k "cli or argparse" -v --tb=short
```

---

## Task T-020-05: Implement dedup log writers

**Story**: [R6] Triple-destination logging
**Type**: [S] sequential
**Execution**: [AFK] autonomous
**Size**: M
**Files**: cli/dedup.py
**Files Blocked**: cli/fleet.py, cli/bootstrap.py, constitution/principles.md
**Depends on**: T-020-04

### Description

Write dedup findings to three destinations:
1. **Ledger**: event rows with types `dedup_scan_run`,
   `dedup_overlap_flagged`, `dedup_decision_recorded`.
2. **Per-spec-dir**: `dedup-scan.md` written to the candidate's spec dir
   when the overlap is spec-bound.
3. **Rolling log**: append to `backlog/DEDUP-LOG.md` on every scan.

### Acceptance Criteria

- [ ] Ledger rows written with correct event types
- [ ] Per-spec-dir `dedup-scan.md` created for spec-bound overlaps
- [ ] `backlog/DEDUP-LOG.md` appended on every scan
- [ ] All three destinations populated after a single scan run
- [ ] Existing dedup log content preserved (append, not overwrite)

### Verification

```
python -m pytest cli/test_dedup.py -k "log" -v --tb=short
```

---

## Task T-020-06: Create cross-feature-dedup skill

**Story**: [R3] Skill invokes CLI for agent consumption
**Type**: [P] parallelizable
**Execution**: [AFK] autonomous
**Size**: S
**Files**: .github/skills/workflow/cross-feature-dedup/SKILL.md
**Files Blocked**: cli/dedup.py, cli/fleet.py, cli/bootstrap.py
**Depends on**: T-020-05

### Description

Create `.github/skills/workflow/cross-feature-dedup/SKILL.md` with YAML
frontmatter and skill body. The skill:
- Describes when to invoke dedup (at /triage and /clarify).
- Documents the CLI interface (`dedup.py scan` with flags).
- Provides examples of interpreting HARD/SOFT/ADVISORY results.
- References the triple-destination log for audit trail.

### Acceptance Criteria

- [ ] Skill file exists with valid YAML frontmatter
- [ ] Skill references `cli/dedup.py scan` command
- [ ] Skill explains HARD/SOFT/ADVISORY tiers
- [ ] `schema_lint` accepts the skill file

### Verification

```
python cli/schema_lint.py
```

---

## Task T-020-07: Hook dedup into /triage and /clarify prompts

**Story**: [R8] Prompts invoke dedup automatically
**Type**: [P] parallelizable
**Execution**: [AFK] autonomous
**Size**: S
**Files**: .github/prompts/triage.prompt.md, .github/prompts/clarify.prompt.md
**Files Blocked**: cli/dedup.py, cli/fleet.py, cli/bootstrap.py
**Depends on**: T-020-05

### Description

Update `/triage` and `/clarify` prompt files to include a step that
invokes the dedup pass. The step instructs the agent to run
`cli/dedup.py scan --scope all` before proceeding and to act on any
HARD or SOFT results.

### Acceptance Criteria

- [ ] `triage.prompt.md` references dedup scan step
- [ ] `clarify.prompt.md` references dedup scan step
- [ ] Instructions match the CLI interface from T-020-04

### Verification

```
grep -l "dedup" .github/prompts/triage.prompt.md .github/prompts/clarify.prompt.md
```

---

## Task T-020-08: Empty corpus handling

**Story**: [R7] Explicit notice on empty corpus
**Type**: [S] sequential
**Execution**: [AFK] autonomous
**Size**: S
**Files**: cli/dedup.py
**Files Blocked**: cli/fleet.py, cli/bootstrap.py, constitution/principles.md
**Depends on**: T-020-01

### Description

When BACKLOG.md is empty (or missing) and no open spec dirs exist, the
scanner emits an explicit notice: "no corpus to dedup against; 0
candidates scanned" and exits 0. It does NOT silently skip.

### Acceptance Criteria

- [ ] Empty BACKLOG + no specs -> explicit "0 candidates scanned" notice
- [ ] Missing BACKLOG.md -> same notice (not crash)
- [ ] Exit code 0 (no overlap is not an error)

### Verification

```
python -m pytest cli/test_dedup.py -k "empty" -v --tb=short
```

---

## Task T-020-09: Full test suite + schema_lint regression check

**Story**: [R9, R10] No regression
**Type**: [S] sequential
**Execution**: [AFK] autonomous
**Size**: S
**Files**: (none -- verification only)
**Files Blocked**: (none)
**Depends on**: T-020-08

### Description

Run the full test suite and `schema_lint` to confirm no regressions.
Test count must be >= 213 baseline. All existing tests pass. All new
dedup-related tests pass.

### Acceptance Criteria

- [ ] `pytest` exits 0 with >= 213 tests passed
- [ ] `schema_lint` exits 0
- [ ] No warnings or deprecations introduced

### Verification

```
python -m pytest spec-driven-development/cli/ -v --tb=short
python spec-driven-development/cli/schema_lint.py
```

---

## Dependency Graph

```
T-020-01 -> T-020-02 -> T-020-03 -> T-020-04 -> T-020-05 -> T-020-06 [P]
                                                             -> T-020-07 [P]
T-020-01 -> T-020-08
T-020-08 -> T-020-09
T-020-07 -> T-020-09
T-020-06 -> T-020-09
```

## Batch Plan

- **Batch 1** (F-08): T-020-01, T-020-02 (sequential, build core scanner)
- **Batch 2** (F-08): T-020-03, T-020-04, T-020-05 (sequential, build CLI + logging)
- **CHECKPOINT**: Run test suite after Batch 2
- **Batch 3** (F-08, parallel): T-020-06 + T-020-07 + T-020-08 (different files)
- **Batch 4** (F-08): T-020-09 (final regression check)
