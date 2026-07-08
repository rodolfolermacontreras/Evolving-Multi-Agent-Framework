---
id: SDD-20260626MAINT-clarify
type: clarification
status: done
owner: principal-product-manager
updated: 2026-06-26
feature: 2026-06-26-sdd-048-maintainability
---

# CLARIFY: SDD-048 -- Maintainability + right-sizing (C-1 / C-2 / C-3 / D-2)

- Epic ID: SDD-048 (PI-7 Sprint 17 / PI-7 Sprint 4 -- the final PI-7 sprint)
- Spec source: [`../../docs/Temp/EMF-HARDENING-PLAN.md`](../../docs/Temp/EMF-HARDENING-PLAN.md) Part C (C-1, C-2, C-3) + Part D (D-2)
- Lead: Sprint Executive Manager (routes); PM + Architect own this CLARIFY/SPEC.
- Dispatch: F-44 is DESIGN-ONLY (CLARIFY -> SPEC -> PLAN -> TASKS). F-45 implements.

---

## Per-item SDD-IDs

CLARIFY assigns one ID per audit item, each with its own validation contract
(mirrors the SDD-047 A-2/A-3/D-1/D-3 pattern). The audit item label IS the
per-item ID under the SDD-048 umbrella:

| Per-item ID | Audit item | Validation contract |
|-------------|-----------|---------------------|
| C-1 | Break up the `state_builder.py` god-module | [`validation-C1.md`](validation-C1.md) |
| C-2 | Right-size the stdlib-only rule where it hurts (render wall) | [`validation-C2.md`](validation-C2.md) |
| C-3 | Replace the hardcoded grandfather date | [`validation-C3.md`](validation-C3.md) |
| D-2 | Add a lightweight-spec path for small features | [`validation-D2.md`](validation-D2.md) |

---

## Locked owner decisions (recorded, not re-asked)

The owner pre-locked all six CLARIFY surfaces (Q-A..Q-F) at dispatch. They are
recorded here as binding answers. No surface is re-opened.

### Q-A -- C-1 lock approach (THE design risk)

**Decision: approach (a) -- refactor AROUND the five Article X locked functions.**

- The five S1-footprint locked functions (`render_html`, `load_sprint_table`,
  `load_sprint_goal`, `detect_current_sprint`, `load_decisions`) are IMMUTABLE.
  They are guarded byte-for-byte by `TestS1FootprintLockGuard` in
  `cli/test_state_builder.py` against commit `257b081` golden SHA-256 hashes.
- Do NOT move, rewrite, or re-factor any locked function. The C-1 ~120-line
  target applies ONLY to the NON-locked surface.
- The five locked functions are a documented, owner-ratified exception to the
  ~120-line target. NO Article X re-baseline. NO approach (b).
- If the ~120-line target proves IMPOSSIBLE for a NON-locked function without
  touching a locked function, F-45 STOPS and reports as OWNER-ATTENTION
  escalation. (See stale-check below -- only `render_html` collides, and it is
  already covered by the locked exception, so no escalation is currently open.)

### Q-B -- C-1 extraction plan

**Decision: module decomposition, one extraction per commit, pure refactor.**

- Decompose into sibling modules: data assembly, markdown render, html render,
  HTTP server, doc-count, work-index.
- ONE extraction per commit; the existing `test_state_builder` suite stays green
  after EVERY extraction.
- Pure refactor: no behavior change, no test-assertion change. Concrete module
  boundaries and extraction order are locked in [`plan.md`](plan.md).

### Q-C -- C-2 stdlib-vs-templating

**Decision: STAY STDLIB-ONLY. Factor the NON-locked render wall into
`string.Template`-based helpers (still stdlib). NO new third-party dependency.**

- Article V (stdlib-only) is preserved as the distribution guarantee.
- C-2 produces an ADR ([`../../docs/ADR/023-dashboard-render-stdlib-only.md`](../../docs/ADR/023-dashboard-render-stdlib-only.md))
  recording the decision + its trade-off. **Status: Proposed** in F-44; the owner
  ratifies to Accepted at F-46/close.
- C-2 folds into C-1: the `string.Template` factoring happens inside the markdown
  and html render extractions, not as a separate code stream.

### Q-D -- C-3 cutover date

**Decision: move `ARTICLE_XI_CUTOVER` out of CLI logic into a config source,
with a comment explaining why the cutover exists. Stdlib-only.**

- Destination: a field in `project.config.json` (the established config surface,
  created by SDD-047). `fleet.py` reads it via stdlib `json`, with a fallback
  constant and the existing explanatory comment retained.
- No hardcoded calendar date remains in CLI logic without a config source + comment.

### Q-E -- D-2 lightweight-spec shape

**Decision: ONE combined doc (story + requirements + validation contract) for
<5-file features; cross-links instead of four near-duplicate files; STILL
satisfies Article X.**

- The validation lock is NOT weakened -- only duplication is collapsed. The
  combined doc still authors a checkable validation contract BEFORE
  implementation (Article X preserved).
- Proven on a real <5-file feature in F-45. F-44 designs the combined-doc SHAPE
  only (it does NOT create the template file -- that is implementation).

### Q-F -- max-function-length lint

**Decision: OPTIONAL nice-to-have.** If cheap + stdlib-only (an `ast` walk),
scope it to EXCLUDE the five locked functions. Do NOT block the sprint. Marked
OPTIONAL (not REQUIRED) in [`validation-C1.md`](validation-C1.md).

---

## DA-Evidence stale-check against the live repo (2026-06-26)

Per DA-Evidence Discipline: every audit "Evidence" line was re-verified against
the LIVE repo before CLARIFY. The audit was written 2026-06-24; PI-7 sprints
have since grown the dashboard generator. Findings:

### C-1 evidence (`state_builder.py` god-module)

| Audit claim (2026-06-24) | Live repo (2026-06-26) | Verdict |
|--------------------------|------------------------|---------|
| 3082 lines | **~4153 lines** | DRIFT -- file grew ~1071 lines. Item MORE valid. |
| 56 top-level functions | **~79 functions / 6 classes** | DRIFT -- grew ~23. Item MORE valid. |
| `render_markdown` 762 lines | **762 lines (L897-1659)** | MATCH. NON-locked -> primary decompose target. |
| `render_html` 658 lines | **658 lines (L1746-2404)** | MATCH. **LOCKED (S1 footprint).** |
| HTTP server present | `served_html_with_refresh`, `DashboardHandler`, `_port_available`, `serve`, `handle_reorder_request` present | MATCH. |
| doc-counter present | `build_doc_count`, `build_doc_count_by_sprint`, `render_count_table`, `cmd_count` present | MATCH. |
| work-index builder present | `build_index`, `_discover_sprints`, `_detect_sprint_status`, `_query_ledger_for_pi`, `_render_sprint_table` present | MATCH. |

**Stale-check result:** C-1 is NOT stale; the file is LARGER than audited, which
strengthens the case. No item dropped. Surfaced drift: the audit line/function
counts are stale-low and are restated to live values in [`spec.md`](spec.md).

**Single locked collision with the ~120-line target:** of the five locked
functions, only `render_html` (658 lines) exceeds ~120. The other four
(`load_sprint_table` ~21, `load_sprint_goal` ~62, `detect_current_sprint` ~15,
`load_decisions` ~42) are already under 120. So `render_html` is the ONLY locked
function in tension with C-1, and it is fully covered by the Q-A documented
exception -- NO open OWNER-ATTENTION escalation.

### C-2 evidence (render wall)

- Audit: "1420 lines of hand-rolled rendering ... a 700-line f-string wall."
- Live: `render_markdown` (762, NON-locked) + `render_html` (658, LOCKED) = 1420.
  MATCH. **But `render_html` is LOCKED and cannot be factored under approach (a).**
- **Surfaced consequence:** C-2's "no longer one 700-line f-string wall" is
  satisfiable ONLY for `render_markdown` (762, non-locked) plus the non-locked
  html injectors. `render_html` remains a 658-line wall as the documented
  Article X exception. This nuance is recorded in the ADR and [`validation-C2.md`](validation-C2.md);
  it is NOT an escalation (Q-A/Q-C already ratify it).

### C-3 evidence (grandfather date)

- Audit: `fleet.py` `ARTICLE_XI_CUTOVER = "2026-06-08"`.
- Live: `fleet.py` line 45 `ARTICLE_XI_CUTOVER = "2026-06-08"` with an explanatory
  comment already present; consumed at line 472 as the default `cutover` arg of
  `_is_grandfathered`. MATCH.
- New since audit: `project.config.json` now EXISTS (SDD-047) -> a clean config
  destination is available.

### D-2 evidence (lightweight path)

- Audit: `specs/2026-05-12-fleet-ledger/RETRO.md` LESSON-001/003 ("lifecycle
  artifact volume is high for a small CLI"); Article VI authorizes lighter
  ceremony for <5-file features.
- Live: the four-document lifecycle (clarify/spec/plan/tasks + per-item
  validation) is still the only path; no combined-doc template exists yet. MATCH.

**Overall:** no audit item is stale enough to drop. The only correction is the
restated (larger) C-1 counts and the explicitly surfaced C-2 `render_html`-locked
nuance. Both carry into [`spec.md`](spec.md) and the per-item validation contracts.

---

## Scope corrections recorded

- **DE-1 (C-1 locked exception):** the ~120-line acceptance criterion is
  rewritten to "no NON-locked function exceeds ~120 lines; the five S1-footprint
  locked functions are an explicit documented exception." This SHARPENS the audit
  acceptance to match the Article X reality (does not weaken it).
- **DE-2 (C-2 honest factoring scope):** C-2's "no 700-line wall" target applies
  to the NON-locked render surface only; `render_html` stays locked. Recorded so
  F-45 does not chase an impossible target on a locked function.
