---
id: SDD-20260609UIVARIANT-retro
type: retro
status: done
owner: principal-software-developer
updated: 2026-06-08
feature: 2026-06-09-ui-lifecycle-variant
---

# Retrospective: UI Lifecycle Variant (SDD-018)

- Feature: SDD-018
- Sprint: PI-5 / Sprint 3 (= overall Sprint 7)
- Closed: 2026-06-08 at F-11 final pass
- Spec: [`./spec.md`](./spec.md)
- Validation: [`./validation.md`](./validation.md)
- ADR: [`../../docs/ADR/014-ui-lifecycle-variant.md`](../../docs/ADR/014-ui-lifecycle-variant.md) (status: proposed; awaits owner Level-2 Article XII landing)

---

## Commit chain

- `df3bffb` -- F-10 pass 1: scaffold + CLARIFY question battery + Article XI live contention test PASS
- `754fda6` -- F-10 CLARIFY closed (Q1-Q9 + 3 OWNER-ATTENTION resolutions + SDD-034 filed)
- `d81ac3d` -- F-10 pass 2: spec/validation/plan/tasks finalized; ADR-014 drafted (proposed)
- `7993fac` -- T-018-02: schema_lint variant dispatch + 32 new tests (UIVariantMarkerRecognition, DeltaEntrySchema, DeltaAppendOnlyAndErrorPrefix, RetroactiveDemoPathAllowlist + 3 live-repo fixture classes)
- `3f6f520` -- T-018-03: template stubs in feature-spec.md and validation.md
- `b46a32f` -- T-018-04: state-dashboard retroactive-demo migration (the SDD-018 proof case)
- `5233c29` -- T-018-06: docs/UI-LIFECYCLE-VARIANT.md authoring guide
- close commit -- T-018-01 baseline + T-018-07 final verification + validation.md item flips + this RETRO.md

---

## Outcomes vs plan

- Spec, validation, plan, tasks, ADR-014, schema_lint variant dispatch,
  template stubs, state-dashboard demo, docs page, and final verification
  all delivered as planned in the F-10 pass 2 commit `d81ac3d`. No
  scope drift in F-11.
- 16/16 REQUIRED + 3/3 OPTIONAL items closed. 2/4 manual checks
  closed at F-11 close (M-3 spot-check self-attested via lint + tests;
  M-4 state.html regen verified). 2/4 manual checks routed to owner
  async (M-1 ADR-014 read; M-2 Article XII tone review).
- Tests: 273 baseline -> 305 final (+32 net), no regressions in
  existing 22 schema_lint tests or any other module.
- `schema_lint` exit 0 across whole repo at F-11 close.
- `state_builder.py` exit 0 at F-11 close; `exec/state.md`,
  `exec/state.html`, `exec/work-index.md` regenerated cleanly.

---

## What worked

- **Two-pass design + implementation split**: F-10 pass 1 (scaffold +
  CLARIFY) -> F-10 pass 2 (spec/validation/plan/tasks/ADR finalized)
  -> F-11 (implementation + close) kept the constitutional change
  reviewable and made the ADR drafting separable from the runtime
  change. The owner sees the ADR text in F-10 pass 2 and can ratify
  it after F-11 closes, with the constitution edit as a separate
  Level-2 commit.
- **Single-worker sequential execution** was the correct call for
  F-11. The 7 tasks had tight sequencing (T-018-04 depends on
  T-018-02's validator existing; T-018-06 depends on T-018-04's
  artifact). Fleet dispatch overhead would have exceeded the
  parallelism gain.
- **Mechanism (b) append-only enforcement** (always-on parse-time
  monotonic check + `git show HEAD:` comparison) proved testable
  inside `tempfile.TemporaryDirectory` + `git init` fixtures
  without dragging in any new dependency. The trade-off (first
  DE-NN entry must land in a single commit) is acceptable.
- **Hard-coded length-1 allow-list** for `item-type: retroactive-demo`
  is the right rigidity: any future retroactive demo requires both
  a constitution edit AND a `schema_lint.py` allow-list edit, which
  is the right friction level.

---

## What surprised us

- **The state-dashboard `validation.md` had 8 more lines than the
  first read showed**: my initial T-018-04 insertion split the
  `## v0.2 additions` subsection, violating lock-surface protection 7.
  Recovered by `git checkout HEAD -- validation.md` and re-inserting
  at the true end of file. Lesson: when "appending" to a file, read
  the full file first; do not trust a partial scroll.
- **PowerShell `Get-Content | Measure-Object -Line` undercounted** the
  file's true line count by 8 (45 vs 53). This was a contributing
  factor in the lock-surface near-miss above. Switched to
  `(Get-Content -Raw).Split("\`n").Length` for reliable line counts.
- **State_builder requires a `RETRO.md`** to flip a feature from
  REVIEW to DONE even when all checkboxes are checked. Discovered
  at T-018-07 final verification. Resolved by writing this file.

---

## What we'd do differently

- Read the FULL file before any "surgical append" -- not just the
  section heading we plan to insert near. The 8 missed lines in
  state-dashboard `validation.md` cost ~10 minutes of recovery.
- For long lookups, prefer `(Get-Content -Raw).Split("\`n").Length` to
  PowerShell's `Measure-Object -Line` which appears to lose lines on
  Windows-line-ending files.

---

## Article XII (pending; not F-11 work)

Per F-10 + F-11 design, the actual `constitution/principles.md` edit
to add Article XII is a separate Level-2 commit performed by the
owner after reading [`../../docs/ADR/014-ui-lifecycle-variant.md`](../../docs/ADR/014-ui-lifecycle-variant.md).
The ADR carries the verbatim proposed Article XII text the owner
pastes; F-11 does NOT touch `constitution/principles.md`. ADR-014
status flips `proposed -> accepted` at that point.

Sprint 7 push is gated on owner approval (Sprint 7 close criterion #8);
this RETRO + the close commit land locally and stay unpushed until the
owner ratifies Article XII and authorizes the push.

---

## Open follow-ups (informational; not blocking)

- **SDD-034** (dedup content-shingle upgrade, P3 unscheduled) -- filed
  during F-10 pass 1 when the dedup scan returned 100% false-positive
  title-shingle artifacts.
- **F-beta** (Sprint Burndown / Velocity widget, PI-6 candidate) --
  first real variant consumer per `clarify.md` Q7. PI-6 PM to label
  it as "the variant proof case" at plan time.
- **`live-ui-v2` retroactive migration** (C1 stretch candidate per
  `clarify.md` Q5) -- post-PI-6 if it earns priority.
- **`/spec-ui` slash command** -- deferred to P3; file SDD-035 if
  friction emerges per `clarify.md` Q2 + OWNER-ATTENTION 1.
