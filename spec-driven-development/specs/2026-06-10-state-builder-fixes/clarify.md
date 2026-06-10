---
id: SDD-20260610STATEBUILDERFIX-clarification
type: clarification
status: active
owner: principal-product-manager
updated: 2026-06-10
feature: 2026-06-10-state-builder-fixes
---

# CLARIFY: SDD-040 -- state_builder.py parser fix + auto-refresh

- Date: 2026-06-10 (SKELETON)
- Authors: Principal Product Manager + Principal Architect (jointly, at F-21)
- Status: **OPEN** -- 5 questions; closes at F-21 in a fresh Sprint 10 session
- Spec ID: SDD-040
- Sprint: PI-6 / Sprint 1 (= overall Sprint 10), F-21 (pass 1 of 1; CLARIFY+SPEC+PLAN+TASKS fused per [`SPRINT-10-KICKOFF.prompt.md`](../../feature-prompts/SPRINT-10-KICKOFF.prompt.md) section 2)
- Gating: lock of [`validation.md`](./validation.md), finalization of [`spec.md`](./spec.md) Acceptance Criteria + Out-of-Scope, finalization of [`plan.md`](./plan.md) Risk Assessment, and finalization of [`tasks.md`](./tasks.md) per-task scope, all unblocked once Q-A through Q-E are answered.

---

## Ground Rules

- **One question at a time is the author discipline.** The five
  questions below are pre-staged at scaffold so the owner can answer
  them in a single round, but the owner may answer them one at a time
  across multiple turns within F-21 if preferred. PM and Architect
  each give a recommendation per question. Where they agree, a
  **Joint recommendation** is recorded.
- This file is the **only** source of truth for SDD-040 design
  decisions. Anything decided in chat or hallway must be back-filled
  here before [`spec.md`](./spec.md) finalizes at F-21.
- All five questions inherit the Article V (stdlib-only) constraint
  per Q-D and the Article VII (one feature, one session) constraint
  per [`SPRINT-10-KICKOFF.prompt.md`](../../feature-prompts/SPRINT-10-KICKOFF.prompt.md)
  section 0.

---

## Scope

### Q-A: Active-focus signal source

**Context.** The current `derive_next_action` heuristic in
`cli/state_builder.py` (line 562) picks the active focus by walking
features by stage in fixed order: IMPLEMENT > REVIEW > PI commitments
> backlog fallback. Source of truth is **frontmatter only** -- no
runtime signal. Owner verbatim 2026-06-10 via EM proves this fails
empirically: "Still says Active focus: azure-decommission (stale --
that wrapped up)." azure-decommission shipped at PI-5 close
(`8417818`, 2026-06-09); the dashboard still picks it because the
heuristic does not know what shipped most recently.

Four candidate signal sources, alone or in combination:

- **(a) Commit recency.** Read `git log --since=N` (or a similar
  bounded window) and pick the spec dir whose files were most
  recently touched. Reflects "what is being worked on right now"
  even if the spec dir is still in active status.
- **(b) Validation-completeness.** Pick the spec dir with REQUIRED
  items still unchecked in its `validation.md`. Reflects "what is
  still owed contractually." If multiple, tie-break by sprint
  frontmatter or commit recency.
- **(c) Sprint frontmatter.** Pick by the currently-open sprint
  per `sprints/PI-N/CURRENT_PI.md`. Reflects "what is planned for
  this sprint" -- but this is essentially what the current heuristic
  already does, and it is the source of the staleness.
- **(d) Combination.** A composite rule -- for example, "most recent
  commit among spec dirs with REQUIRED items unchecked, falling back
  to the current sprint's anchor feature if none qualify."

**PM recommendation:** TBD at F-21.

**Architect recommendation:** TBD at F-21.

**Joint recommendation:** TBD at F-21.

**Status:** OPEN.
**Answer:** TBD at F-21.

---

### Q-B: Auto-refresh mechanism

**Context.** Article V (stdlib-only CLI) rules out `watchdog`,
`flask`, `fastapi`, `requests`. The existing serve subcommand
(`cli/state_builder.py serve`, line 2385) already rebuilds state on
every HTTP GET via `DashboardHandler.do_GET` (line 2358) using
`build(... write=False, live_html=True ...)`. The defect is that
the **page itself does not refresh** -- the owner has to F5 the
browser, or the existing "Page auto-refreshes every 20s" print
claim on line 2402 is not wired through to the served HTML.

Four candidate mechanisms (all stdlib-compatible):

- **(a) Handler-side meta-refresh.** Inject `<meta http-equiv="refresh"
  content="N">` into the served HTML head. Simplest possible
  mechanism. Cadence is fixed per page render (so changing cadence
  requires a server-side flag). No JS required.
- **(b) Client-side polling via `<script>`.** Inject a small inline
  `<script>` that polls a JSON endpoint (e.g. `GET /state.json`) or
  re-fetches the page on a timer. More flexible than (a), but
  introduces JS to a previously script-free page (CSP currently
  blocks scripts; would need a CSP relaxation).
- **(c) Server-side file-mtime sweep.** Background thread that
  walks `specs/**`, `sprints/**`, `exec/**`, `ledger/fleet.db` and
  checks `os.stat` mtimes against a cached snapshot. On change,
  invalidates the rebuild cache so the next GET picks up new state.
  Pairs naturally with (a) to drive client refresh.
- **(d) Server-Sent Events (SSE).** New `text/event-stream` route
  pushes a "refresh" event when the mtime sweep detects a change.
  Stdlib-only (use `BaseHTTPRequestHandler` raw `wfile.write` with
  `Content-Type: text/event-stream`). Most responsive UX. Highest
  implementation cost.

**PM recommendation:** TBD at F-21.

**Architect recommendation:** TBD at F-21.

**Joint recommendation:** TBD at F-21.

**Status:** OPEN.
**Answer:** TBD at F-21.

---

### Q-C: Refresh cadence

**Context.** Cadence balances dashboard freshness against laptop
CPU cost. Too aggressive (e.g. 1 second) burns CPU on every file
walk; too lazy (e.g. 60 seconds) defeats the point.

Candidate defaults:

- **(a) 1 second.** Effectively instant. Highest CPU cost. Only
  defensible if Q-B answer is (c) or (d) with a cheap mtime sweep.
- **(b) 5 seconds.** Conservative default for polling. Reasonable
  developer-laptop CPU profile.
- **(c) 10 seconds.** Matches the existing "20s" print claim at
  half. Owner-friendly for casual monitoring.
- **(d) 20 seconds.** Matches the existing print claim verbatim;
  least change relative to the implicit current contract.
- **(e) On-demand only.** No timer; refresh triggered by manual
  POST/GET to a refresh endpoint. Lowest CPU; needs owner action
  per refresh.

CLI flag for override is required by validation R5 regardless of
default choice.

**PM recommendation:** TBD at F-21.

**Architect recommendation:** TBD at F-21.

**Joint recommendation:** TBD at F-21.

**Status:** OPEN.
**Answer:** TBD at F-21.

---

### Q-D: Stdlib-only constraint (Article V) confirmation

**Context.** Article V (Stdlib-Only CLI Pattern, see
[`docs/CLI-PATTERN.md`](../../docs/CLI-PATTERN.md)) binds all
`cli/*.py` modules. SDD-040 must confirm and re-affirm the
constraint explicitly, because Q-B candidate (d) SSE and Q-A
candidate (a) commit-recency both flirt with edge cases that could
tempt a third-party import (`watchdog`, `pygit2`, etc.).

Concrete confirmation:

- Implementation MUST use only stdlib modules. Modules already
  imported by `cli/state_builder.py` are `http.server`, `urllib`,
  `pathlib`, `json`, `os`, `sqlite3`, `socket`, `sys`, `html`,
  `webbrowser`, `re`, `datetime`. New stdlib modules are
  permitted (e.g. `threading` for Q-B (c)/(d); `subprocess` for
  Q-A (a) `git log` invocation; `dataclasses` if helpful).
- Implementation MUST NOT add `watchdog`, `flask`, `fastapi`,
  `requests`, `pygit2`, or any other PyPI dependency.
- If commit-recency (Q-A (a)) is chosen, the implementation reads
  `git log` via `subprocess.run` -- not via a Python git library.

**PM recommendation:** **CONFIRM Article V binding.** No exceptions
for SDD-040. If F-21 needs to question Article V's stdlib reach,
that is a separate constitutional question and requires an ADR per
[`SPRINT-10-KICKOFF.prompt.md`](../../feature-prompts/SPRINT-10-KICKOFF.prompt.md)
Hard Constraints item 4.

**Architect recommendation:** **CONFIRM Article V binding** for the
reasons PM gives. The set of permitted stdlib modules above is the
working list; F-21 may extend it with any additional stdlib import
without ceremony.

**Joint recommendation:** **CONFIRM Article V binding.** No new
third-party dependency. Implementation uses only stdlib modules.

**Status:** OPEN (pre-staged at scaffold; expected to be a quick
ratification at F-21).
**Answer:** TBD at F-21 (pre-staged "CONFIRM").

---

### Q-E: Backwards compatibility for non-serve invocation

**Context.** `python state_builder.py` (without `serve`) writes
static `state.md`, `state.html`, and `work-index.md` to `exec/` for
git/diff use. Many existing tests in `cli/test_state_builder.py`
exercise this path. Sprint 10's parser fix MUST NOT regress this
path; the new active-focus signal source must be deterministic when
fed deterministic inputs.

Concrete confirmation:

- Non-serve invocation MUST produce byte-identical static `state.md`
  and `state.html` to the pre-SDD-040 baseline (commit `8417818`)
  in cases where the new active-focus helper has nothing to
  contribute (e.g. no recent commits in the configured window, no
  REQUIRED-unchecked spec dirs -- per Q-A answer).
- Non-serve invocation MAY produce a different `Active focus:` line
  in cases where the new helper does contribute -- and SHOULD (that
  is the entire point of the parser fix).
- Auto-refresh behavior MUST be serve-mode-only. The CLI form
  `python state_builder.py` (without `serve`) MUST NOT gain a
  background thread, a watcher, or any new side effect.
- All existing tests in `cli/test_state_builder.py` MUST stay green
  without modification.

**PM recommendation:** **CONFIRM backwards compatibility.** Pre-stage
the answer at scaffold; F-21 ratifies.

**Architect recommendation:** **CONFIRM** with one clarification:
"byte-identical" applies to **static output for unchanged inputs**.
If a CLARIFY answer to Q-A changes the active-focus line for the
current input set (which is the whole point), that is not a
regression -- it is the fix. The regression test (R2/R6) measures
the byte-identical property against a **controlled baseline input
set** (e.g. specs/sprints/exec frozen at a known commit), not
against live inputs that have shifted.

**Joint recommendation:** **CONFIRM backwards compatibility** per
the Architect's clarification. R2 in [`validation.md`](./validation.md)
will reference a controlled baseline input set at F-21.

**Status:** OPEN (pre-staged at scaffold; expected to be a quick
ratification at F-21).
**Answer:** TBD at F-21 (pre-staged "CONFIRM with clarification").

---

## OWNER-ATTENTION items (at F-21 close)

- **None at scaffold.** F-21 may surface OWNER-ATTENTION items as
  Q-A through Q-C are answered -- e.g. if Q-A (d) "combination" is
  chosen, the precise composition rule may need owner sign-off; if
  Q-B (b) client-side script is chosen, the CSP relaxation may
  need owner sign-off. Any surfaced item is recorded here and
  flagged in the F-21 close report.

## ADR decision

- **Default at scaffold: no ADR needed.** Per
  [`SPRINT-10-KICKOFF.prompt.md`](../../feature-prompts/SPRINT-10-KICKOFF.prompt.md)
  section 3, the active-focus heuristic and refresh mechanism are
  implementation choices inside an existing CLI surface, not new
  constitutional ground.
- **Escalate to ADR if:** F-21 surfaces a refresh mechanism that
  challenges Article V's stdlib reach (Q-D), OR Q-B (b) requires
  a CSP relaxation that constitutes a security-policy change, OR
  any other answer rises to a Level-2 decision per
  [`docs/RULES.md`](../../docs/RULES.md).

## F-21 close checklist

When the owner finishes answering Q-A through Q-E, the F-21 owner:

1. Updates each Q-N "Answer" line above with the owner's verbatim
   response (or EM-synthesized decision with attribution).
2. Sets this file's frontmatter `status: done` and updates `updated:`.
3. Finalizes [`spec.md`](./spec.md) Acceptance Criteria (AC-1..AC-5)
   with concrete Given/When/Then wording bound to the answers.
4. Finalizes [`validation.md`](./validation.md) R1-R9 with concrete
   test names, file paths, and verification commands, then **LOCKS**
   the contract (records lock timestamp at the top of the file).
5. Finalizes [`plan.md`](./plan.md) Risk Assessment with mitigations
   updated against the chosen Q-B mechanism.
6. Finalizes [`tasks.md`](./tasks.md) per-task file scope and
   acceptance test columns.
7. Decides ADR yes/no per the rule above; if yes, drafts ADR-NNN
   and routes to owner for Level-2 approval before F-22 starts.
8. Commits the F-21 finalization with subject
   `clarify: SDD-040 CLARIFY closed; validation contract LOCKED`
   and routes to owner for ratification per Sprint 10 pre-push gate.
