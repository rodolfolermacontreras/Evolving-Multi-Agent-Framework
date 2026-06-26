---
id: SDD-20260626DEAUTHOR-validation-a2
type: validation
status: done
owner: principal-architect
updated: 2026-06-26
feature: 2026-06-26-sdd-047-de-author
---

# VALIDATION: SDD-047 / A-2 -- owner/identity becomes a config value

- Per-item ID: A-2 | Spec: [`spec.md`](spec.md) | Source: EMF-HARDENING-PLAN A-2 Acceptance
- Lock statement: LOCKED at F-41. F-42 may CHECK with evidence; may not weaken a REQUIRED item. Deltas are numbered DE-xx and must SHARPEN.

## Required Items (Strict)

- [x] **R-1 (config surface exists).** `project.config.json` at repo root holds `owner`, `team`, `repo_url`; valid JSON; readable with stdlib only. Evidence: `json.load(open('project.config.json'))` succeeds; keys present.
- [x] **R-2 (no hardcoded name in generic files).** No file under `.github/agents/**`, `.github/skills/**`, `INSTRUCTIONS.md`, or README-as-instruction contains a hardcoded personal name; all owner references resolve to config or "the host project's owner". Evidence: `origin_lint.py` clean (EXIT=0) + doctor `origin tokens absent: ok`.
- [x] **R-3 (PM agent traces to config).** `principal-product-manager.agent.md` traces user value to "the host project's owner", not a named person.
- [x] **R-4 (neutral skill author).** Every `SKILL.md` `author:` frontmatter is `emf-framework`; schema_lint stays clean. Evidence: 35x SKILL.md set to `emf-framework`; `schema_lint.py` DEFAULT_EXIT=0.
- [x] **R-5 (lint reads config).** `cli/origin_lint.py` loads a personal-name denylist from `project.config.json`; a test proves a re-added personal name in a generic file FAILS the lint. Evidence: `test_origin_lint.py` re-add case asserts non-zero exit; passes in full suite.
- [x] **R-6 (Level-2, owner-gated).** `constitution/mission.md` (line 17) and `constitution/decision-policy.md` (line 57) owner-name lines de-authored under accepted ADR-022 + recorded owner approval + constitution version bump (mission 1.0.0->1.1.0, decision-policy 1.1.0->1.2.0). Evidence: governance_check.py + doctor `governance coherent: ok`.

## Manual Checks

- [x] **M-1.** Reviewer confirms a fresh-clone reader cannot identify the author from any generic file. (Generic surfaces resolve owner to config / "the host project's owner".)
- [x] **M-2.** Owner pre-push approval recorded; ADR-022 accepted before R-6 lands. Evidence: ADR-022 Status: Accepted; owner approved the epic + Level-2 edit.

## Definition of Done

R-1..R-5 checked with real-run evidence; R-6 landed under approved ADR-022;
M-1..M-2 confirmed; full suite + schema_lint green.
