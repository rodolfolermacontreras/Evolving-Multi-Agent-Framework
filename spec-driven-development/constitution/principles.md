---
version: '1.3.0'
ratified: 2026-05-12
last_amended: 2026-06-08
---

# Framework Principles

Eleven binding articles. They define how the **framework itself** works -- the rules
that any host project adopting SDD inherits. All agents (Principals and workers)
must honor these. Exceptions require a Level 2 decision and an ADR entry.

These are framework-level rules. The host project's own engineering principles
(coding conventions, testing baselines, security rules tied to its stack) live in
a separate `principles.md` *inside the host project's adapted constitution*. When
a host project bootstraps SDD, it inherits these ten framework articles and adds
its own host-level articles on top.

---

## Article I: Two-Folder Split Is Invariant

`.github/` holds Copilot-native files (agents, skills, prompts, instructions) so
VS Code Copilot Chat auto-discovers them. `spec-driven-development/` holds
process state (constitution, specs, sprints, ledger, templates, CLI). The
boundary is non-negotiable: process state never leaks into `.github/`,
agent definitions never leak into `spec-driven-development/`. This split is
what makes the framework portable. Documented in ADR-0002.

## Article II: Single Human Entry Point

The Principal Executive Manager is the human's default entry point to the
fleet. The human talks to one agent first; the Executive Manager either
answers from its big-picture context or routes to the right Principal,
synthesizes the answer, and returns it at executive register. The human is
welcome to attend ceremonies (sprint planning, PI planning, retros) directly,
but ad-hoc questions and new ideas flow through the Executive Manager by
default. Documented in ADR-0004.

## Article III: Two-Stage Review Order Is Fixed

Every implementation passes through two distinct review gates, in order:
**spec compliance first** (does the implementation match the spec?), then
**code quality second** (is it well-written?). The two reviews must be
performed by different agents. Quality review never starts before compliance
review passes -- the order prevents wasted review cycles on
spec-non-compliant code. This is the framework's primary defense against the
"AI wrote something that looks right but doesn't match the spec" failure
mode.

## Article IV: Specialization Over Generalism

Agents have constrained scopes by design. A worker dispatched on a task
modifies 1-3 files maximum. A reviewer reviews; it does not implement. A
Principal owns one strategic dimension (product, architecture, implementation,
or orchestration); it does not encroach on the others. Constrained agents
catch more, miss less, and produce more consistent output than general
assistants given the same context budget.

## Article V: Generic By Default, Specialized On Demand

Workers (Developer, UX Designer, QA Engineer, Data Scientist) start generic.
A worker that demonstrates excellence in a domain across multiple dispatches
earns a permanent identity and a domain-specific skill pack
(e.g. `Data Scientist Bob Forecast Expert 1`). Specialization is *earned* by
demonstrated competence, not assigned by configuration. This prevents the
sprawl of pre-emptively defined agent roles that never get used.
Documented in ADR-0003.

## Article VI: Ceremony Proportional To Risk (Spec Sizing Rule)

Not every change deserves the full lifecycle. The framework enforces
proportionality:

- Bug fix, less than 3 files: no spec; task + test + review only
- Feature, less than 5 files: lightweight spec (user story + requirements + success criteria)
- Feature, 5 or more files: full spec with all sections
- Cross-cutting change or schema change: full spec + ADR + Level 2 human approval

The rule prevents two failure modes: (a) ceremony bloat that strangles small
changes, and (b) under-specified large changes that arrive at review without
acceptance criteria.

## Article VII: Every Artifact Is A File; Every Dispatch Is Logged

Specs, plans, tasks, ADRs, retros, and clarification logs are all Markdown
files committed to the repo. No project state lives in chat history or in any
agent's memory alone. Every fleet dispatch (one task assigned to one worker)
is recorded in `spec-driven-development/ledger/fleet.db` with timestamp,
task, agent, and outcome. The answer to "why was this built this way?" is
always a file you can open. The answer to "who did this and when?" is always
a ledger row.

**One feature, one session.** A direct corollary of the rule above: chat
sessions are ephemeral context, not project state. Each in-flight feature
SHOULD use its own dedicated Copilot session so context from one feature does
not contaminate work on another. The Principal Executive Manager session
stays high-level (routing, status, synthesis) and never absorbs feature
implementation depth. When a session ends, the durable artifacts (specs,
tasks, validation, ledger rows, session checkpoints under
`spec-driven-development/sessions/`) carry the state forward -- not the chat
history.

## Article VIII: Constitution Is Immutable Without An ADR

The six constitution files (`mission.md`, `tech-stack.md`, `principles.md`,
`roadmap.md` -- excluding entry additions, `decision-policy.md`,
`quality-policy.md`) define the project's identity and rules. They cannot be
modified without an Architecture Decision Record explaining the change, the
alternatives considered, and the consequences. This applies both to the
framework's own constitution and to any host project's adapted constitution.
Roadmap *additions* (new completed items, new tech-debt entries) do not
require an ADR; *removals* and *direction changes* do.

## Article IX: Human Holds Final Approval

Decision authority is tiered. **Level 0** (status, routing, capture) belongs
to the Executive Manager. **Level 1** (cross-module decisions, ADRs,
product/technical choices) belongs to the four Principals. **Level 2**
(irreversible decisions: new dependencies, schema migrations, external
integrations, production merges, scope changes after sprint commitment)
**always requires a human-in-the-loop**. No agent ever makes a Level 2
decision unilaterally, no matter how confident. Gates with Level 2 stakes
include the human as a mandatory approver.

## Article X: Validation Is a Pre-Implementation Contract

Every spec ships with a validation block that defines testable acceptance
criteria before implementation begins; the validation contract is committed
alongside the spec, reviewed at the SPEC gate, and locked when `/tasks` is
invoked. Implementation is complete when and only when every checked item in
the validation contract passes. Production-code changes without a corresponding
test are rejected at the IMPLEMENT gate unless the task is explicitly tagged
`[NO-TEST-NEEDED]` with a written justification accepted by the
spec-compliance reviewer. This codifies the convergent finding from Spec-Kit
(`/checklist` unit tests for requirements), the DeepLearning.AI SDD course
(Validation Scorecard), and sc-spec (`validation.md` with Definition of Done):
validation criteria belong before implementation, not after.

## Article XI: Cross-Feature Serial Gate at CLARIFY and SPEC

At most one feature may occupy the CLARIFY phase at any moment, and at most
one feature may occupy the SPEC phase at any moment. The framework enforces
two independent per-phase locks at the repo level. The gate prevents
inter-feature context contamination that Article VII's one-feature-one-session
rule cannot catch -- Article VII binds the session, Article XI binds the repo.
Lock state derives from artifact frontmatter (clarification status != done;
spec.md status == draft), reusing SDD-FDC-001 as the substrate. Hard refusal
applies to automated `fleet.py` dispatch; advisory warnings apply to
interactive slash commands. Override requires `fleet.py lock force-release`
with a mandatory `--reason` flag and a ledger-audited row. Phases outside
CLARIFY and SPEC remain parallelizable.

## Article XII: UI Lifecycle Variant of the Validation Contract

A spec dir MAY opt into the UI Lifecycle Variant of Article X by
declaring `ui-variant: true` in its `spec.md` frontmatter. The variant
applies only to that spec dir; it does NOT propagate to siblings,
parents, or path-pattern matches. Variant spec dirs follow these
amendments to Article X:

1. **Lock timing is preserved.** `validation.md` is still LOCKED at
   `/tasks` time. The variant does not loosen the lock event.
2. **Append-only delta mechanism replaces the no-loosening clause.**
   After lock, variant spec dirs MAY append entries to a
   `## Delta Entries` section in `validation.md`. Each entry is a
   level-3 sub-section with mandatory fields `timestamp` (ISO 8601
   UTC), `author`, `rationale`, and `item-type` (closed enum
   `{add, wontfix, re-check, retroactive-demo}`). Existing locked
   items are not edited; deltas are append-only and themselves
   become part of the locked contract the moment they are committed.
3. **Required-completeness rule is preserved.** Zero unchecked
   REQUIRED items before implementation is considered complete --
   for both base items AND `item-type: add` delta entries.
   `item-type: wontfix` entries annotate without removing; the
   underlying REQUIRED item remains in the contract unless an
   explicit `re-check` supersedes it.
4. **Forward-only migration.** Pre-existing locked contracts are
   not retroactively eligible to adopt the variant. The single
   sanctioned exception is the SDD-018 proof case
   (`specs/2026-05-16-state-dashboard/`), tagged
   `item-type: retroactive-demo` and enforced by a hard-coded
   `schema_lint` allow-list.

`cli/schema_lint.py` enforces this article. Delta-originated lint
findings are prefixed `[delta]`. Authoring guidance lives in
`docs/UI-LIFECYCLE-VARIANT.md`. The variant is documented in
ADR-014.

---

## Design Heuristics (not binding articles, but strong defaults)

These are not enforceable rules; they are biases the framework prefers when
trade-offs are otherwise balanced.

- **Convention over configuration**: follow existing patterns before introducing new ones.
- **Existing patterns over new abstractions**: read the codebase before deciding something is missing.
- **Small, frequent commits over large batches**: each commit explainable in one sentence.
- **Read before modifying**: open the file, understand current state, show diffs before committing.
- **Clean as you go**: no orphan code, no commented-out blocks, no unused variables, no stale scripts.
- **Symbolic cadence over wall-clock cadence**: PI/Sprint exist to provide ceremony rhythm, not to gate calendar weeks. The AI fleet compresses wall-clock time dramatically.
- **Stdlib over dependencies (for the framework's own CLI)**: new third-party dependencies in the framework's CLI require Architect approval and an ADR.

---

## Host Project Articles

A host project that adopts SDD inherits these ten framework articles and
adds its own articles capturing host-specific rules: coding conventions tied
to its language/framework, security rules tied to its data sensitivity,
testing baselines tied to its current state, deployment rules tied to its
infrastructure. Host articles are numbered starting from H1 to distinguish
them from framework articles (I-X).

The Day-to-Day Agent host project's articles -- the original nine that lived
in this file before generalization -- are an example of host articles. They
described that project's specific rules (Engine singleton, World State
contract, 743-test baseline, FastAPI route discipline, etc.). Those articles
remain valid for the Day-to-Day Agent project; they do not belong here in the
framework's constitution.

Reference: see `spec-driven-development/GENERALIZATION_SDD.md` for the
procedure a host project follows to bootstrap its own articles.
---

## Governance

The constitution is versioned per file using semantic versioning (`version`,
`ratified`, `last_amended` in YAML frontmatter). Amendments use the
`/constitution` slash command:

- **MAJOR**: principle changed or removed (e.g. Article III rewritten)
- **MINOR**: new article or principle added, or new section appended
- **PATCH**: clarification, example added, typo, or non-semantic edit

Every amendment runs a propagation scan via the `constitution-sync` skill,
which lists all skills, prompts, and templates that reference the amended
content. The `/constitution` command emits a Sync Impact Report attached to
the amending commit. References found NEEDS-REVIEW or NEEDS-UPDATE are
flagged; resolution is the Architect's responsibility before the
amendment commit lands. Documented in ADR-0006.
