---
id: SDD-20260710SPRINT23POLISH-tasks
type: tasks
status: active
owner: principal-software-developer
updated: 2026-07-10
feature: 2026-07-10-sprint-23-dashboard-polish
---

# TASKS: F-63 Sprint 23 dashboard polish

- IDs: SDD-038, SDD-056, SDD-057
- Spec: [`spec.md`](./spec.md)
- Plan: [`plan.md`](./plan.md)
- Validation: [`validation.md`](./validation.md) -- **LOCKED**

---

## Rules

- TDD is mandatory: each behavior group starts RED.
- No REQUIRED validation deferral.
- Run SDD-049 file-scope overlap detection before any batch; never use
  `--allow-overlap` for overlapping state-builder work.
- Task file scope is an allowlist. Generated exec files are written by build only.

## Atomic Tasks

| Task | Tag | Description | File Scope (max 3) | Validation | Deps | Mode | Dispatch | Status |
|------|-----|-------------|--------------------|------------|------|------|----------|--------|
| T-X-01 | [S] | Capture >=623/2 baseline, focused lock hashes, schema/origin/staledoc lints, strict local doctor. Record counts without changing production files. | `tasks.md`, `validation.md` | VX-2, VX-3 | none | AFK | No | pending |
| T-057-01 | [S] | Write failing tests for active-PI selection, all accepted sprint marker forms, overall-number precedence, malformed/closed/conflicting/absent/read-error rejection, build live/fallback paths. | `cli/test_state_builder.py` | V57-1..V57-3, VX-1 | T-X-01 | AFK | No | pending |
| T-057-02 | [S] | Implement pure additive `load_active_sprint_from_current_pi` and re-export it. No facade build wiring yet. | `cli/state_builder_data.py`, `cli/state_builder.py`, `cli/test_state_builder.py` | V57-1, V57-2 | T-057-01 | AFK | No | pending |
| T-057-03 | [S] | Wire live-list/legacy-list selection in non-locked `build()` and feed selected list to unchanged `detect_current_sprint`; preserve empty fallback. | `cli/state_builder.py`, `cli/test_state_builder.py` | V57-3, VX-2 | T-057-02 | AFK | No | pending |
| T-056-01 | [S] | Write failing PI-nav tests, then implement/re-export `inject_pi_pills_html` with numeric ordering, sole current+ARIA, escaping, missing-marker fallback, and idempotence. Do not wire build yet. | `cli/state_builder_html.py`, `cli/state_builder.py`, `cli/test_state_builder.py` | V56-1, V56-2, VX-1 | T-057-03 | AFK | No | pending |
| T-056-02 | [S] | Wire PI-nav injector immediately after `render_html` in `build()` using existing `pis` + resolved PI; verify no roadmap/constitution write. | `cli/state_builder.py`, `cli/test_state_builder.py` | V56-1, V56-4, VX-2 | T-056-01 | AFK | No | pending |
| T-038-01 | [S] | Write failing token/mapping/idempotence/contrast/accessibility tests, then implement/re-export lifecycle token injector with exact nine tokens and state classes. | `cli/state_builder_html.py`, `cli/state_builder.py`, `cli/test_state_builder.py` | V38-1..V38-4, VX-1 | T-056-02 | AFK | No | pending |
| T-038-02 | [S] | Wire token injector immediately after lifecycle injector; verify labels/ARIA remain and opacity no longer communicates state. | `cli/state_builder.py`, `cli/test_state_builder.py` | V38-2, V38-4, VX-2 | T-038-01 | AFK | No | pending |
| T-056-03 | [P] | Write exact-scope guard, then replace only the two locked historical phrases with the approved context-isolation wording. | `cli/test_sdd056.py`, `feature-prompts/SPRINT-05-KICKOFF.prompt.md`, `feature-prompts/SPRINT-06-KICKOFF.prompt.md` | V56-3, VX-1 | T-X-01 | AFK | Yes only parallel to T-057/038 state work | pending |
| T-X-02 | [S] | Sprint EM/PM records explicit Sprint 23 ACTIVE source marker; run build to regenerate three exec files; assert real PI/Sprint/token/wording smoke; run full tests, lints, lock hashes, local doctor, clean CI doctor, ledger B-1, and public CI. Check validation with evidence and append close progress. | `sprints/PI-9/CURRENT_PI.md`, `exec/state.html`, `validation.md` | V56-4, V57-4, V38-3, VX-2..VX-5, M-1..M-3 | all | HITL close | No | pending |

## Sequencing

```
T-X-01
  -> T-057-01 -> T-057-02 -> T-057-03
  -> T-056-01 -> T-056-02
  -> T-038-01 -> T-038-02
  -> T-X-02

T-056-03 may run after T-X-01 in parallel with the state-builder chain because
its normalized file scope has an empty intersection. It must finish before T-X-02.
```

## Generated-output note

T-X-02's table scope lists only the three files that require direct gate
attention. `state_builder.py build` also generates `exec/state.md` and
`exec/work-index.md`; those are command outputs, never hand-edited. If the task
runner requires all generated paths in its allowlist, treat the three exec files
as one generated-output group and keep the task serialized.

## Handoff condition

Principal Software Developer may start only after confirming this contract is
locked, the Article XI bundle is the sole active CLARIFY/SPEC unit, and the
Sprint 23 ACTIVE marker ownership is assigned to Sprint EM/PM rather than inferred
by implementation.
