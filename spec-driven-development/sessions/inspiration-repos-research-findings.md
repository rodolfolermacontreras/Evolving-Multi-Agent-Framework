# Inspiration Repos: Research Findings & Synthesis

Date: 2026-05-12
Method: 4 parallel research subagents fetched the actual repos and primary sources.
Reports preserved in chat history; this is the consolidated synthesis.

---

## 1. Major factual correction

The framework currently lists FOUR inspirations:
1. Spec-Kit (cited as "by Cline" — actually GitHub's own toolkit)
2. SC Spec-Driven Development Files (Rodolfo's repo)
3. Matt Pocock's Skills
4. DeepLearning.AI SDD course

**The reality from the research:**

- **Spec-Kit is by GitHub**, not Cline. Repo: https://github.com/github/spec-kit. Active CLI at v0.8.9.dev0, ~30+ files, blog post 2025-09-02.
- **`sc-spec-driven-development-files` IS the companion code repo for the DeepLearning.AI SDD course.** Same author teaching the same methodology. They are not two independent inspirations — they are one source (the course) and its supporting code (the companion repo). The course is **"Spec-Driven Development with Coding Agents"** taught by **Paul Everitt of JetBrains**, free on DeepLearning.AI Short Courses. NOT a Coursera/Andrew Ng course; NOT Anthropic-partnered.
- **Matt Pocock's skills repo is real and active.** https://github.com/mattpocock/skills, distributed via skills.sh (`npx skills@latest add mattpocock/skills`).

So we actually have **3 distinct inspirations** plus SAFe-as-methodology, not 4.

---

## 2. Convergent recommendations (multiple sources agree)

When the same gap surfaces in 2+ independent reports, the signal is highest. These are the strongest candidates for adoption:

### A. Pre-implementation validation artifact ⭐⭐⭐
Surfaced by: **all 3 code-based inspirations**.

- **Spec-Kit** calls it `/speckit.checklist` and frames it as "unit tests for requirements" — checks that the spec is complete, clear, consistent, measurable, and covered, BEFORE any code is written.
- **DeepLearning.AI course** calls it the **Validation Scorecard** — manual tests, curl commands, automated test specs, written during the planning conversation and committed alongside the spec.
- **sc-spec companion repo** ships `validation.md` with checkbox format and an explicit **Definition of Done** section.

We have `templates/validation.md` but it's positioned as a post-implementation REVIEW artifact. The convergent insight: **promote validation to a binding pre-implementation contract**. Tied directly to our pending `s2-tdd-enforcement` todo.

### B. Feature directory naming convention ⭐⭐
Surfaced by: **Spec-Kit + sc-spec companion**.

- **Spec-Kit**: `specs/NNN-feature-name/` (numeric prefix + auto-incremented + `feature.json` state file)
- **sc-spec**: `specs/YYYY-MM-DD-feature-name/` (date prefix)

We say "one directory per feature" but the convention is undefined. Both inspirations co-locate ALL feature artifacts (spec, plan, tasks, validation, research) inside one feature directory. Date-prefix is more readable; number-prefix is more orderable. **Recommendation: pick date-prefix** (sc-spec's choice — same author's prior work, lower-friction adoption).

### C. Bootstrap automation ⭐⭐
Surfaced by: **Spec-Kit explicitly + DeepLearning.AI course implicitly**.

Spec-Kit ships a real Python CLI (`uvx --from git+... specify init <name>`) that scaffolds the entire `.specify/` tree, copies templates, installs command files for the chosen agent (Copilot, Claude, Cursor, etc.), and writes `init-options.json`. Tied directly to our pending `s3-greenfield-bootstrap` todo. **Spec-Kit is the existence proof that this works** — we don't have to invent the pattern.

### D. Constitution propagation check ⭐
Surfaced by: **Spec-Kit alone, but high-impact**.

When Spec-Kit's `/speckit.constitution` amends the constitution, it semver-bumps it (MAJOR.MINOR.PATCH), reads all command files and templates for stale references, and outputs a **Sync Impact Report** listing what changed and what needs manual review. We have a 6-file constitution and 22 skills + 13 commands — when we amend, today nothing checks alignment. This is a real risk we currently bear silently.

---

## 3. Single-source recommendations (still worth borrowing)

### From Spec-Kit
- **Inline spec quality gate**: `/specify` runs a 13-criterion checklist on the generated spec before declaring done.
- **Max-3 `[NEEDS CLARIFICATION]` rule**: Hard cap on ambiguity markers per spec, prioritized scope > security > UX > tech.
- **9-category `/clarify` taxonomy**: functional scope, domain/data, UX flow, NFRs, integration, edge cases, constraints, terminology, completion signals. Each question presented one at a time WITH a recommended answer. Coverage table at the end.
- **Read-only `/analyze` constraint**: Never modifies files; always proposes remediation requiring explicit approval.
- **Strict tech-stack separation between `/specify` and `/plan`**: Spec is technology-agnostic (user journeys only); plan is where tech choices live. Worth enforcing in our spec template.
- **`check-prerequisites.sh/ps1` pattern**: Every command's first step is to validate the active feature exists and emit a JSON context block. Cross-platform (bash + PowerShell).

### From Matt Pocock
- **`argument-hint` frontmatter field**: One line per skill, tells the agent what to prompt for before invocation. Removes "I didn't know what to pass" confusion. Trivial to add to all 22 of our skills.
- **Bundled sub-document pattern (progressive disclosure)**: When a SKILL.md exceeds ~100 lines, split format/template content into sibling files (`CONTEXT-FORMAT.md`, `ADR-FORMAT.md`) referenced by the main skill. Keeps the main file scannable; sub-docs loaded only when needed.
- **`handoff` skill**: A skill specifically for compacting one session into a handoff doc for the next session. We have NO equivalent and we're a multi-agent framework — handoffs are architecturally important.
- **ADR minimalism gate**: An ADR is created only when **all three** are true: (1) hard to reverse, (2) surprising without context, (3) result of a real trade-off. Prevents ADR inflation.
- **Skill lifecycle buckets**: `in-progress/`, `deprecated/`, `personal/` folders excluded from the registry by policy. We have no formal deprecation path.

### From DeepLearning.AI course (Paul Everitt / JetBrains)
- **Replanning ceremony**: After every feature merges, formal step to update constitution, check next roadmap item, write/improve agent skills. Slow down to run fast. We have no equivalent — our lifecycle goes DONE → next IDEA without a pause.
- **Per-feature 15-item start checklist**: Encoded as a skill, enforced before context-clearing for the next feature. Catches "starting on dirty context" failures.
- **Collaborative constitution authoring**: Agent uses an `AskUserQuestion`-style structured interview to draft the constitution rather than the human filling templates alone. Course claims significantly higher quality. Directly applies to our greenfield bootstrap.
- **Context clearing as explicit protocol**: `/clear` before feature planning AND again before implementation. We have no mention of context hygiene anywhere.
- **`tech-stack.md` "Gaps / Future Considerations" section**: Forces honest documentation of known limitations; prevents agents from inferring gaps are intentional.
- **Pinned versions in spec**: e.g. "Hono v4.2.1" not "Hono ~v4". Reduces version-drift bugs.

### From sc-spec companion
- **`requirements.md` Scope/Decisions/Context structure**: Tighter than our Problem/Solution. Maps naturally to a 3-question interview (each interview answer feeds one section).
- **`changelog.py` script**: Zero-dependency Python that auto-generates or incrementally updates `CHANGELOG.md` from `git log`. We have no changelog automation.

---

## 4. Things to deliberately NOT borrow

Spec-Kit's research subagent flagged 4 anti-patterns that we should reject outright:

1. **Their single-agent model**. Spec-Kit assumes one human + one AI assistant. Adopting their command prompts verbatim would erase our PM → Architect → SW Dev → Worker handoff chain — the core differentiator of our framework.
2. **Python CLI as primary distribution**. Spec-Kit's `uvx ... specify init` is elegant but adds a runtime dependency. Our portability rests on Markdown + YAML files. A CLI helper is fine; a CLI as the primary install path is not.
3. **`.specify/extensions.yml` before/after hook system**. Useful in single-user workflows; adds coordination overhead in multi-agent orchestration. Our handoffs are implicit between Principal agents.
4. **Folding research into `/plan`**. Spec-Kit's `/plan` has a Phase 0 that resolves `NEEDS CLARIFICATION` items. In our model that work belongs to `/clarify` (PM) and `/analyze` (Architect). Borrow the concept (resolve ambiguity before designing); keep it in the right agent's command.

---

## 5. Confirmation of our existing differentiation

The research confirms we have moved meaningfully BEYOND our inspirations. None of the three has any equivalent of:

- Multi-agent Principal hierarchy (Executive Manager + PM + Architect + SW Dev)
- Generic worker fleet that specializes on demand (ADR-0003)
- Two-stage review order (spec compliance THEN code quality, by different reviewers)
- Spec sizing rule (the no-spec/lightweight/full/+ADR matrix)
- ADR-based decision policy with Level 0/1/2 authority tiers
- Fleet ledger (SQLite dispatch audit trail)
- 6-file constitution with explicit decision-policy and quality-policy files
- Single human entry point via Executive Manager (ADR-0004)

This is reassuring: we're not behind on any structural dimension. We're ahead on agent architecture and behind on tactical tooling (CLI, validation gates, propagation checks).

---

## 6. Faithfulness audit (are we crediting accurately?)

**Spec-Kit**: Currently credited as "by Cline". **Wrong.** It is by GitHub. Fix the README.

**Matt Pocock**: Credited for SKILL.md format and grill-me pattern. **Accurate** — both real and from his repo. **Caveat**: our grill-me is ~600 words plus a separate prompt file; his canonical version is ~60 words ("Interview me relentlessly..."). Most of our elaboration (question caps, taxonomy, logging) is our own extension on top of his core idea. Should clarify the credit: "core grill-me concept from Matt Pocock; SDD-lifecycle framing and structure are our extensions."

**DeepLearning.AI course**: Credited as "conceptual foundation for SDD as methodology". **Accurate but understated.** We've absorbed the full workflow: constitution-mission-tech-stack-roadmap, feature-loop, brownfield bootstrap, agent skills architecture. The credit could be more explicit.

**SAFe**: Credited as "adapted for single developer + AI fleet". Not researched (it's a methodology, not a repo); credit accuracy unverified but reasonable.

---

## 7. Recommended next moves (ranked)

Given the convergent findings and our existing pending todos, this is the recommended order:

1. **Fix the inspirations list** in the root README (Spec-Kit is GitHub not Cline; sc-spec is the DLAI course companion). Fast, factual, no design decisions.
2. **Adopt date-prefix feature directory convention** `specs/YYYY-MM-DD-feature-name/`. Document in tech-stack.md and templates. Cheap.
3. **Ship `s2-tdd-enforcement` already on the pending list, but with the convergent finding folded in**: validation as a pre-implementation binding contract, not just a TDD gate. Use the Spec-Kit "checklist as unit tests for requirements" framing.
4. **Add `argument-hint` to every skill's frontmatter**. Trivial mechanical change; immediate UX gain.
5. **Add `handoff` skill**. Architecturally important for our multi-agent setup; we have no equivalent today.
6. **Constitution semantic versioning + propagation check**. Add a `/constitution` slash command (or extend the Architect agent) that semver-bumps + scans skills/commands/templates for stale references + emits a Sync Impact Report.
7. **Replanning ceremony**. Add `/replan` slash command for the Architect or PM to run after every feature DONE. Use the DLAI 15-item checklist as the basis.
8. **Bootstrap automation** (existing `s3-greenfield-bootstrap` pending todo): use Spec-Kit's `specify init` as the design model, but ship as Markdown + a small Python script (NOT a full CLI distribution). Honors our portability constraint.

Items 4-7 each require small design decisions; items 1, 2, 8 are mostly mechanical given the design is already specified.
