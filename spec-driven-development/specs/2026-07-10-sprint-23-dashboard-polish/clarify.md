---
id: SDD-20260710SPRINT23POLISH-clarification
type: clarification
status: done
owner: principal-architect
updated: 2026-07-10
feature: 2026-07-10-sprint-23-dashboard-polish
---

# CLARIFY: F-63 Sprint 23 dashboard polish

- IDs: SDD-038, SDD-056, SDD-057
- Date: 2026-07-10
- Status: **DONE**
- Source: `feature-prompts/SPRINT-23-KICKOFF.prompt.md` and PM triage commit `4ac03f9`

---

## Article XI bundle decision

F-63 uses one cohesive spec directory for the three IDs. This is justified rather
than three concurrent spec directories because all three outcomes share the
state-builder build pipeline, generated dashboard, Article X lock evidence, and
close smoke test. One bundle keeps CLARIFY and SPEC serial while preserving
independent per-ID requirements, acceptance criteria, validation rows, file
scopes, and tasks. It is not permission to merge their implementation evidence.

## Decisions

| Q | Decision | Rationale |
|---|----------|-----------|
| Q-1 architecture | Use existing additive loader and `inject_*` post-render patterns. Do not edit `render_html`, `render_markdown`, `load_sprint_table`, `load_sprint_goal`, `detect_current_sprint`, or `load_decisions`. | SDD-037/040/042 proved the pattern; no new cross-module architecture is introduced. |
| Q-2 PI navigation | Add `inject_pi_pills_html(html_doc, *, pis, active_pi)` after `render_html`. It rebuilds only `<nav class="pi-pills">` from the already-loaded live `PIBlock` list and the resolved active PI. | Data-driven, no roadmap/constitution edit, and exactly one `aria-current="page"`. |
| Q-3 active sprint source | Add `load_active_sprint_from_current_pi(sdd_root)` in `state_builder_data.py`. Select the highest-numbered `sprints/PI-*/CURRENT_PI.md` whose frontmatter is `status: active` and whose body declares the PI ACTIVE; parse one explicit non-closed Sprint marker into the existing sprint-dict shape. | The current PI artifact is the sprint source of truth; no deprecated Management path is required. |
| Q-4 sprint parsing | Recognize explicit overall sprint markers in the ACTIVE status line, an ACTIVE/CURRENT/IN-PROGRESS sprint heading, or a Sprint Allocation row. Reject markers qualified CLOSED/DONE/PROPOSED. Prefer an explicit overall sprint number; use the PI-local number only when no overall number is present. Multiple conflicting active markers are invalid and return no live candidate. | Robust selection without guessing. Sprint 23 must be explicitly marked active in PI-9 before the real smoke test. |
| Q-5 fallback | In `build()`, pass the additive loader result to the unchanged `detect_current_sprint`. If the loader returns no unambiguous active sprint, fall back to unchanged `load_sprint_table`; if both are empty, preserve `No active sprint found.` | Backward-compatible and no fabricated sprint. |
| Q-6 lifecycle tokens | Adopt the Principal UI Designer's original nine-token IDE-native set listed below. Apply it with `inject_lifecycle_tokens_html` after `inject_lifecycle_html`; the injector adds state classes and CSS variables to repository-controlled HTML. | One semantic color per canonical lifecycle state; raw Markdown keeps textual state labels as its renderer-independent fallback. |
| Q-7 accessibility | State text and `aria-current="step"` remain mandatory. Do not use opacity to convey lifecycle state. Normal-size text and UI boundaries must meet WCAG AA contrast against the darkest raised surface; solid token fills use carbon text. | Color is not the sole signal. |
| Q-8 wording | Change only the two known residual phrases: Sprint 5 line 35 and the Sprint 6 sentence beginning `Do NOT start Sprint 7 in this session. It runs in its own fresh session`. Replace each with the SDD-039 choice: fresh session **or** EM-routed subagent dispatch. | Preserves historical instructions while removing the false mandatory-session implication; no broad scrub. |
| Q-9 governance | Level-1, no ADR. No dependency, schema, API, constitution, or governance-pattern change. Validation uses the normal Article X lock plus Article XII only for visual token application. | Existing additive patterns are reused. |
| Q-10 execution | State-builder work is serialized. The two-prompt wording task is parallel-safe only because SDD-049 file-scope comparison shows no overlap with state-builder files. Generated exec files are regenerated once at the end. | Prevents same-file conflict and stale generated output. |

## Approved token set (SDD-038)

| State | Token | Value | Contrast on `#1C1B18` |
|-------|-------|-------|-----------------------|
| IDEA | `--lifecycle-idea` | `#B39DDB` | 7.19:1 |
| BACKLOG | `--lifecycle-backlog` | `#7FA8C9` | 6.85:1 |
| CLARIFY | `--lifecycle-clarify` | `#58B8B0` | 7.30:1 |
| SPEC | `--lifecycle-spec` | `#82B57A` | 7.25:1 |
| PLAN | `--lifecycle-plan` | `#C2A85D` | 7.42:1 |
| TASKS | `--lifecycle-tasks` | `#D48B52` | 6.24:1 |
| IMPLEMENT | `--lifecycle-implement` | `#D36F86` | 5.24:1 |
| REVIEW | `--lifecycle-review` | `#B884C4` | 5.85:1 |
| DONE | `--lifecycle-done` | `#6FA37A` | 5.90:1 |

Contrast values use WCAG 2.1 sRGB relative luminance against the darkest raised
surface. Every value exceeds 4.5:1 for normal text and 3:1 for UI boundaries.
Carbon `#0A0A0A` is used when a token becomes a solid background. The palette was
created for this framework and is not copied from an external design system.

## Exact wording replacements (SDD-056)

1. `Each F-## runs in its own fresh session.` becomes `Each F-## runs in its own context-isolated unit: a fresh session or an EM-routed subagent dispatch.`
2. `Do NOT start Sprint 7 in this session. It runs in its own fresh session` becomes `Do NOT start Sprint 7 in this context-isolated unit. Start it in a fresh session or through an EM-routed subagent dispatch` (the following kickoff-file clause remains intact).

## Findings and prerequisites

- PI-9 `CURRENT_PI.md` is ACTIVE but currently records Sprint 22 as closed and has
  no explicit Sprint 23 active marker. SDD-057 MUST NOT infer Sprint 23 from that
  absence. The Sprint EM/PM must record Sprint 23 as ACTIVE in the current PI
  artifact before implementation close; this is source-data hygiene, not a
  loader workaround.
- No `constitution/**` change is required or allowed.
- No ADR is required.
- No open clarification remains. SPEC gate: **APPROVED**.
