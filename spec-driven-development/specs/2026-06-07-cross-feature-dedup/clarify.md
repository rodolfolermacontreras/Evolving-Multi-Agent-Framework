---
id: SDD-20260607DEDUP-clarification
type: clarification
status: draft
owner: principal-architect
updated: 2026-06-07
feature: 2026-06-07-cross-feature-dedup
---

# CLARIFY: Cross-Feature Deduplication at /triage and /clarify (SDD-020)

- Date: 2026-06-07
- Drafted by: Principal Architect (scaffold session, EM context)
- Status: AWAITING OWNER ANSWERS -- to be answered in fresh Sprint 6 implementation session per Article VII
- Spec ID: SDD-020
- Gating: /spec finalization is blocked until these answers are recorded.

---

## Ground Rules

- One question at a time. Owner answers in this file; Architect records the
  answer + rationale immediately below each question.
- Recommended answers (where stated) are the Architect's starting position,
  NOT decisions.
- Q5 (SDD-019 integration order) is the hardest dependency to resolve and
  may need to be answered jointly with the SDD-019 CLARIFY session.

---

## Scope

### Q1: Dedup scope -- what gets scanned?

When the dedup pass runs, what corpus does it scan against?
- (a) `backlog/BACKLOG.md` only.
- (b) `backlog/BACKLOG.md` + `backlog/IDEAS.md`.
- (c) `backlog/**` + open spec dirs (`specs/**/spec.md` where status != done/archived).
- (d) Everything in (c) + closed/done spec dirs (full history).

Recommended answer: (c) backlog + open spec dirs. Closed specs are
historical; flagging overlap with a done spec is interesting but rarely
actionable. PI-wide is implicit because BACKLOG is PI-scoped.

Answer: TBD

---

## Constraints

### Q2: Match heuristic -- how is overlap detected?

How does the detector decide two items overlap?
- (a) **Exact ID** only (frontmatter `id` collision).
- (b) **Title fuzzy match** (e.g., difflib SequenceMatcher ratio >= 0.8).
- (c) **Title + problem-statement keyword overlap** (top-N TF-IDF or
  Jaccard on tokenized problem statements).
- (d) **Semantic similarity via LLM embeddings**.
- (e) Layered: (a) hard match, (b) soft match, (c) advisory match.

Recommended answer: (e) layered, but **NO LLM in v1**. Layer 1: exact ID.
Layer 2: title fuzzy match (stdlib difflib). Layer 3: keyword Jaccard on
problem-statement tokens. Each layer reports separately with a clear
confidence label (HARD / SOFT / ADVISORY). Keeps the tool stdlib-only,
deterministic, fast, and inspectable. Semantic-LLM is a future
enhancement (out-of-scope candidate).

Answer: TBD

### Q3: Tooling form -- CLI subcommand, skill, or both?

Where does the dedup logic live?
- (a) New `cli/dedup.py` module with a CLI entry point.
- (b) New `fleet.py dedup` subcommand (extends existing CLI).
- (c) New skill `.github/skills/workflow/cross-feature-dedup/SKILL.md`
  that the /triage and /clarify prompts invoke.
- (d) Both: skill calls CLI; CLI is also independently runnable.

Recommended answer: (d) both. CLI provides the deterministic, testable
core; skill provides the orchestration around it (read BACKLOG, present
overlap to owner, write decision to dedup log). This matches the SDD
pattern -- CLI for mechanics, skill for workflow.

Answer: TBD

---

## Behavior

### Q4: Action on overlap detected -- auto-merge, prompt, or block?

When the detector flags an overlap, what happens?
- (a) **Auto-merge**: detector picks the canonical entry and discards
  the candidate; owner reviews after the fact.
- (b) **Prompt**: owner sees the overlap candidates and decides
  (merge / keep-both / discard candidate / rewrite candidate).
- (c) **Block**: /triage or /clarify refuses to proceed until the owner
  explicitly resolves the overlap.
- (d) Tiered: HARD match blocks, SOFT match prompts, ADVISORY match
  warns.

Recommended answer: (d) tiered, mapping to the layered heuristic from Q2.
HARD (exact ID collision) blocks. SOFT (fuzzy title match) prompts.
ADVISORY (keyword overlap) warns and proceeds. Auto-merge is never used
in v1 -- too risky without owner judgment.

Answer: TBD

### Q5: Integration with SDD-019 -- ordering and dependency

How do SDD-019 (serial CLARIFY/SPEC gate) and SDD-020 (this feature)
interact? Three viable orderings:
- (a) **Dedup first, gate second.** Dedup output is a precondition for
  SDD-019 lock acquisition (overlap-clean candidates can acquire the
  lock; flagged candidates cannot until resolved).
- (b) **Gate first, dedup second.** Dedup runs *inside* the locked
  CLARIFY phase as a quality gate.
- (c) **Independent and composable.** Neither blocks the other; they
  ship in either order.

Recommended answer: (c) independent and composable, with a soft
preference for landing SDD-020 first (lower-risk, no constitutional
amendment). If both ship in Sprint 6, the order is irrelevant to the
final composed behavior. **This question MUST be answered jointly with
the SDD-019 CLARIFY session.**

Answer: TBD

### Q6: Dedup log artifact -- where does the audit trail live?

Where does the detector write its findings + the owner's decision?
- (a) Per-spec-dir `dedup-scan.md` (similar to clarification-log.md).
- (b) Rolling `backlog/DEDUP-LOG.md` (one log for all triage rounds).
- (c) Ledger event rows (`dedup_scan_run`, `dedup_overlap_flagged`,
  `dedup_decision_recorded`).
- (d) Combination: ledger row + per-spec-dir log (for spec-bound dedups)
  + rolling log (for pure-BACKLOG triage rounds).

Recommended answer: (d) combination. Ledger gives the dashboard a
queryable surface; per-spec-dir log gives reviewers context inside the
spec dir; rolling log gives PM a single place to audit triage hygiene
over time. All three reuse existing infra.

Answer: TBD

---

## Edge Cases

### Q7: Empty corpus -- first triage round of a new project

What happens when the dedup pass runs against an empty or near-empty
BACKLOG (e.g., first triage round of a brand-new project)?
- (a) Skip silently; emit clean report.
- (b) Emit explicit "no corpus to dedup against" notice; proceed.

Recommended answer: (b) explicit notice. Silent skips obscure the fact
that the pass ran; an explicit notice makes the run auditable even when
trivially clean.

Answer: TBD

---

## Out of Scope (proposed -- confirm at /spec)

- LLM-based semantic similarity (deferred to a future feature once layered
  heuristics prove insufficient).
- Auto-merge of detected duplicates.
- Cross-repo / multi-project dedup.
- Retroactive dedup of historical (done/archived) spec dirs.
- Dedup of post-SPEC artifacts (plans, tasks, validations, retros).

---

## Question count: 7
