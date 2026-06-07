---
id: SDD-20260607GITIGN-clarification
type: clarification
status: draft
owner: principal-architect
updated: 2026-06-07
feature: 2026-06-07-host-gitignore-protection
---

# CLARIFY: Host `.gitignore` Protection (SDD-027)

- Date: 2026-06-07
- Drafted by: Principal Architect (scaffold session, EM context)
- Status: AWAITING OWNER ANSWERS -- to be answered in fresh Sprint 6 implementation session per Article VII
- Spec ID: SDD-027
- Gating: /spec finalization is blocked until these answers are recorded.
- Article X amendment posture: owner direction 2026-06-07 is "normal spec
  first; only escalate if the spec proves the article must change."

---

## Ground Rules

- One question at a time. Owner answers in this file; Architect records the
  answer + rationale immediately below each question.
- Recommended answers (where stated) are the Architect's starting position,
  NOT decisions.
- Q1 (Article X fit) is itself the amendment-vs-no-amendment trigger; do
  not skip it.

---

## Scope

### Q1: Article X fit -- amendment needed or not?

Does the host-`.gitignore` rule fit inside Article X (Host Integration) as
currently written, or does Article X need a clause added?

Read Article X first. Then choose:
- (a) **Fits as-is.** Article X already mandates "no framework-internal
  state leaks into host commits"; this spec is implementation, not
  amendment.
- (b) **Needs a clause.** Article X is silent on host-side ignore
  contracts; an amendment is required (Friction Analysis still NOT
  required up front per owner direction 2026-06-07; spec proves the
  need first).
- (c) **Article X needs splitting** -- the install-time contract is a
  big enough concept to deserve its own Article.

Recommended answer: defer until Article X has been re-read in the fresh
Sprint 6 session. Initial reading suggests (a) -- the gitignore check is
the *implementation* of a rule Article X already implies -- but the
final call belongs to the owner after re-reading.

Answer: TBD

### Q2: Detection strategy -- depth and form

How deep does the detector inspect the host's state?
- (a) **Static parse of host `.gitignore`** -- read the file, compare
  patterns against the framework-defined sets, report.
- (b) **Live git check** -- run `git check-ignore` (or equivalent) on
  each framework path in the host repo and report what git actually
  ignores. Catches `.gitignore`s in parent dirs, global excludes,
  `core.excludesFile`, etc.
- (c) **Both** -- static parse for the diff display; live git check for
  the authoritative answer.

Recommended answer: (c). Static parse alone misses global excludes and
parent-dir `.gitignore` files; live git check alone gives no readable
diff for the remediation prompt. Both together = correct + explainable.

Answer: TBD

---

## Constraints

### Q3: Action on conflict -- auto-fix, prompt, or refuse?

When a `.gitignore` conflict is detected, what does `host-link` do?
- (a) **Auto-fix**: silently append/remove rules in the host's
  `.gitignore`, then proceed.
- (b) **Prompt**: show the diff, ask the owner to approve, then either
  apply or proceed-without-fixing per owner choice.
- (c) **Refuse**: exit non-zero with a clear remediation message; owner
  fixes manually and re-runs.
- (d) **Tiered**: MUST-BE-IGNORED missing -> auto-fix; MUST-BE-TRACKED
  ignored -> refuse (cannot safely auto-modify the host's intent).
- (e) **Mode flag**: `--gitignore-mode {strict|prompt|warn|skip}` lets
  the caller decide.

Recommended answer: (e) mode flag with default = `prompt`. Interactive
default for first-real-host dispatch (owner is present and learning the
contract); `strict` for CI / scripted bootstrap; `warn` for opt-out of
the gate while still surfacing the diff; `skip` for emergency override.

Answer: TBD

### Q4: Opt-in vs opt-out -- new flag default

Should the gitignore check be:
- (a) **Opt-out** (runs by default, `--no-gitignore-check` to disable).
- (b) **Opt-in** (off by default, `--gitignore-check` to enable).

Recommended answer: (a) opt-out. The whole reason this feature exists is
that first-real-host dispatch is blocked on the missing check; off-by-
default would defeat the purpose. Provide the opt-out flag for
emergencies.

Answer: TBD

---

## Behavior

### Q5: Behavior when host has no `.gitignore` at all

What does `host-link` do when the host repo has no `.gitignore` file?
- (a) Create a minimal `.gitignore` populated with framework MUST-BE-IGNORED
  rules.
- (b) Refuse the install with a clear message: "host requires a
  `.gitignore`; here is the minimal recommended content."
- (c) Proceed with a strong warning (logged + printed) but no file write.

Recommended answer: (b) refuse. Creating files in the host as a side
effect of `host-link` is a surprising action; refusing keeps the host
in control of its own contents and surfaces the requirement explicitly.

Answer: TBD

### Q6: Framework-required path lists -- where do they live?

Where are the MUST-BE-IGNORED and MUST-BE-TRACKED lists declared?
- (a) Hard-coded Python constants in `cli/bootstrap.py`.
- (b) JSON manifest file at `cli/host_gitignore_manifest.json` versioned
  with the framework.
- (c) Markdown spec in `docs/HOST-INTEGRATION.md` parsed at runtime.

Recommended answer: (b) JSON manifest. Easier to extend without code
review on every path addition; trivially diffable; testable as data.
The bootstrap module reads it; docs reference it.

Answer: TBD

---

## Edge Cases

### Q7: Non-git host -- repo with no `.git/` directory

What does `host-link` do when the target is not a git repo at all?
- (a) Refuse (today's behavior, per Sprint 5 impl) -- no change.
- (b) Proceed but skip the gitignore check (no `.git` -> no `.gitignore`
  contract).
- (c) Refuse with new explicit "this check requires a git repo" message.

Recommended answer: (a). Sprint 5's `host-link` already requires a git
repo (it runs `git rev-parse`). No change to that contract; the
gitignore check inherits the requirement transitively.

Answer: TBD

---

## Out of Scope (proposed -- confirm at /spec)

- `.gitattributes` enforcement (gitignore only for v1).
- Per-file LFS / large-file rules.
- Auto-PR-on-host to fix the host's `.gitignore` (manual or in-place only).
- Retroactive cleanup of framework files already committed in the host
  (covered by a follow-up feature if needed; install-time only here).
- Multi-host / fleet-wide gitignore audit (per-host invocation only).

---

## Question count: 7
