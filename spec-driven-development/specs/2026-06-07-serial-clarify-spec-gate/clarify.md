---
id: SDD-20260607SERIAL-clarification
type: clarification
status: done
owner: principal-architect
updated: 2026-06-07
feature: 2026-06-07-serial-clarify-spec-gate
---

# CLARIFY: Serial Gate on CLARIFY/SPEC (SDD-019)

- Date: 2026-06-07
- Drafted by: Principal Architect (scaffold session, EM context)
- Status: CLOSED 2026-06-07
- Spec ID: SDD-019
- Gating: /spec finalization, ADR drafting, and any `constitution/` edit are
  ALL blocked until these answers are recorded and reviewed.

---

## Ground Rules

- One question at a time. Owner answers in this file; Architect records the
  answer + rationale immediately below each question.
- Recommended answers (where stated) are the Architect's starting position,
  NOT decisions. The owner may accept, reject, or amend.
- Constitutional amendment scope is itself a CLARIFY question (Q5); do not
  presume Article VII without owner confirmation.

---

## Scope

### Q1: Gate granularity -- per-phase, per-repo, or per-PI?

Should the serial gate be:
- (a) **Per-phase**: at most one feature in CLARIFY at a time AND at most
  one feature in SPEC at a time (two independent locks);
- (b) **Per-repo combined**: at most one feature across BOTH CLARIFY and
  SPEC (single lock spanning both phases);
- (c) **Per-PI**: serial within a PI but parallel across PIs (likely a
  non-starter for a single-repo framework, listed for completeness)?

CURRENT_PI.md Sprint 2 risk row says "gate is serial per-phase, not
per-repo" but the BACKLOG entry says "Serial gate on CLARIFY/SPEC
(repo-wide)" -- these are in tension. CLARIFY must resolve.

Recommended answer: (a) per-phase. Two independent locks (one for CLARIFY,
one for SPEC), each holding exactly one feature.

Answer: (a) per-phase. Two independent locks (one for CLARIFY, one for SPEC), each holding exactly one feature. Per-phase preserves throughput (a feature finishing CLARIFY frees the slot before its SPEC starts).

### Q2: Scope of "CLARIFY" and "SPEC" phases

What counts as "being in CLARIFY" and "being in SPEC" for lock purposes?
- (a) Existence of `clarify.md` or `clarification-log.md` in a spec dir
  with status != `done`;
- (b) An explicit lock-acquire event in the ledger;
- (c) A spec dir whose `spec.md` frontmatter `status` is `draft`;
- (d) Some combination.

Recommended answer: (a) frontmatter status of the relevant artifact is the
source of truth. Lock = (any clarification file with status != done) OR
(any spec.md with status == draft). This makes the existing filesystem
data contract (SDD-FDC-001) the lock substrate; no new state to maintain.

Answer: (a) frontmatter status. Lock holder derived from artifact frontmatter. Lock = (any clarification file with status != done) for CLARIFY lock, OR (any spec.md with status == draft) for SPEC lock. Reuses SDD-FDC-001 as the lock substrate; no new state to maintain.

---

## Constraints

### Q3: Enforcement mechanism -- advisory lint vs hard fleet.py refusal?

When a second feature tries to enter CLARIFY (or SPEC) while another holds
the lock, what should happen?
- (a) **Hard refusal** in `fleet.py`: dispatch exits non-zero with a
  message naming the lock holder. Owner must manually override.
- (b) **Advisory warning**: dispatch prints a warning but proceeds.
  Schema_lint can flag the violation post-hoc.
- (c) **Hybrid**: hard refusal in `fleet.py`, advisory only in interactive
  /clarify and /spec slash commands (since those are owner-initiated and
  the owner is the human-in-the-loop).

Recommended answer: (c) hybrid. Hard refusal in automated dispatch (no
human in the loop to override safely); advisory in slash commands (owner
is present and can make the override call).

Answer: (c) hybrid. Hard refusal in `fleet.py` (automated dispatch exits non-zero naming the lock holder); advisory warning in interactive slash commands (owner is present and can override). Matches existing pattern: automated paths fail closed, interactive paths inform.

### Q4: Override path -- who, how, with what audit trail?

If the gate must be bypassed (e.g., emergency hotfix CLARIFY while another
feature holds the SPEC lock), what is the path?
- (a) `fleet.py lock force-release <feature> --reason "..."` writes a
  ledger row; subsequent dispatch proceeds.
- (b) Manual edit of a lock-state file with a commit message that
  schema_lint recognizes.
- (c) No override; the second feature waits.

Recommended answer: (a) explicit force-release subcommand with mandatory
`--reason`, ledger-audited. Avoids silent bypass and gives the dashboard
something to show.

Answer: (a) `fleet.py lock force-release <feature> --reason "..."` -- writes a ledger row (event_type `lock_force_released`); subsequent dispatch proceeds. Explicit, audited, scriptable; avoids silent bypass.

---

## Behavior

### Q5: Constitutional amendment -- which Article?

The gate is a behavioral rule. Where does it live in the constitution?
- (a) **Article VII** ("One Feature, One Session"): extend it to include
  a *repo-wide* clause (today it is session-scoped, not repo-scoped).
- (b) **Article VIII** (new) -- "Cross-Feature Serial Gate" -- as a
  first-class peer to Article VII.
- (c) **decision-policy.md**: amend Level-1 decision rules so that
  dispatching CLARIFY/SPEC while another feature holds the lock is a
  Level-2 (human-approval) decision.
- (d) Combination of the above.

Recommended answer: (b) new Article VIII. Article VII is about
*intra-session* discipline (one human focus per session). The serial gate
is about *inter-feature* discipline at the repo level. Conflating them
muddies both. New Article keeps each rule focused and independently
amendable.

Answer: New Article XI -- "Cross-Feature Serial Gate at CLARIFY and SPEC". The scaffold's option (b) text said "Article VIII (new)" but Article VIII already exists (Constitution Immutability). The framework has 10 articles (I-X). A new article is Article XI. MINOR version bump 1.1.0 -> 1.2.0 on principles.md. ADR drafted in F-07, constitution edit in F-08 after owner approval.

### Q6: Batch semantics under multi-worker dispatch

Under multi-worker dispatch (fleet of N parallel workers), what is the
batch unit that the lock guards?
- (a) **One dispatch packet at a time** for the locked feature (workers
  may still parallelize *within* a single feature's CLARIFY/SPEC tasks);
- (b) **One worker at a time** for the locked feature (true serial even
  within a feature);
- (c) **Unlimited workers within the lock holder**, zero workers for any
  other feature in the same phase.

Recommended answer: (c). The lock is about cross-feature contamination,
not intra-feature parallelism. Within the lock holder, parallel workers
are fine because they share the same feature context.

Answer: (c) unlimited workers within the lock holder; zero workers for any other feature in the same phase. The lock prevents cross-feature contamination, not intra-feature parallelism.

### Q7: Queue policy -- FIFO, priority-weighted, or manual?

When feature B requests CLARIFY while feature A holds the lock, what
ordering rule decides who gets the lock next when A releases?
- (a) FIFO on request timestamp.
- (b) Priority-weighted (P1 jumps P2 in the queue).
- (c) Manual: owner picks the next holder explicitly.

Recommended answer: (b) priority-weighted with FIFO as tiebreak. Aligns
with how the PM already prioritizes the backlog; no new ordering concept.

Answer: (b) priority-weighted, FIFO tiebreak. Aligns with PM's existing RICE-based backlog ordering. No new ordering concept.

---

## Edge Cases

### Q8: Backwards compatibility -- what happens to in-flight specs?

At enforcement turn-on, multiple spec dirs may already be in CLARIFY or
SPEC. What is the migration story?
- (a) Grandfather everything currently open; lock applies only to
  *new* CLARIFY/SPEC starts after a cutover commit.
- (b) Force-converge: owner picks one current holder; all others move to
  `status: blocked` until the holder releases.
- (c) Convert-then-lock: each open spec dir gets explicitly locked
  (back-dated lock-acquire ledger rows) in a single migration commit.

Recommended answer: (a) grandfather. Simplest, lowest-risk, and the
serial gate's value is forward-looking, not retroactive.

Answer: (a) grandfather. Everything currently open at enforcement turn-on is grandfathered. Lock applies only to new CLARIFY/SPEC starts after the cutover commit.

### Q9: What is NOT serialized?

Phases explicitly OUTSIDE the gate:
- /triage (pre-CLARIFY)
- /plan, /tasks, /implement, /qa, /retro (post-SPEC)
- Bug fixes < 3 files (no spec required per existing rule)

Confirm these stay parallelizable. Confirm any other carve-outs.

Recommended answer: All of the above stay parallel. No carve-outs beyond
this list.

Answer: Confirmed as listed. /triage, /plan, /tasks, /implement, /qa, /retro, and <3-file bug fixes all stay parallelizable. No additional carve-outs.

---

## Out of Scope (proposed -- confirm at /spec)

- Multi-repo / cross-repo serial gates.
- Serializing PLAN, TASKS, IMPLEMENT, QA, or RETRO phases.
- Auto-detection of "stuck" lock holders (lock-holder liveness probe);
  v1 relies on owner discipline + force-release override.
- Integration with SDD-020 cross-feature dedup (covered separately; see
  spec.md "Cross-Feature Notes").

---

## Question count: 9
