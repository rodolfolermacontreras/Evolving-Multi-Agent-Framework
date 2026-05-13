# Foundations Strategy: Evolving Multi-Agent Framework

Working notes for the strategic direction of the framework. Not committed to the repo
yet — promote to a real doc (e.g. `spec-driven-development/docs/FOUNDATIONS.md` or an
ADR) once direction is confirmed.

Date: 2026-05-12
Author: working session with Rodolfo

---

## 1. What "evolving, ever-adapting" actually means

The word "evolving" in the project name is currently aspirational, not mechanical.
The framework as it stands is a static asset bundle (agents, skills, prompts,
templates, constitution). Nothing in the system mechanically improves it from
project experience.

For the framework to genuinely *evolve*, three feedback loops must exist:

1. **Project → framework:** patterns that prove valuable in a host project flow back
   as new skills, updated templates, or refined agent definitions. Currently
   undefined.
2. **Retro → process:** sprint retros produce action items, but there is no
   enforced channel from a retro action to a framework change (skill update, ADR,
   article amendment). Currently undefined.
3. **Worker → specialist:** a generic worker that excels in a domain earns a
   permanent identity and skill pack. The mechanic is described in CONTEXT.md but
   has never been exercised. Currently undefined in code.

Until at least one of these loops is closed, the framework is *spec-driven* but
not *evolving*. Closing loop 1 should be the first priority once the first pilot
proves the lifecycle works.

---

## 2. Greenfield vs. brownfield: two entry paths, one lifecycle

The single biggest gap in the framework today is that there is no defined way to
*start using it*. GENERALIZATION_SDD.md is 62KB — too much for a quick adoption
decision. Both entry paths need a concrete on-ramp.

### Greenfield path (new project, empty repo)

Characteristics:
- No existing code, tests, or conventions to respect
- Tech stack is a *decision*, not a *constraint*
- Constitution is *authored*, not *extracted*
- TDD can be enforced from commit zero

Required artifacts:
- A `cli/bootstrap.py greenfield` (or just a `greenfield-init.md` checklist) that:
  - Copies `.github/` and `spec-driven-development/` into the new repo
  - Prompts the human for: project name, owner, primary language, primary domain
  - Generates a *blank-but-structured* `mission.md`, `tech-stack.md`,
    `principles.md` from the human's answers and a chosen archetype
  - Initializes `ledger/fleet.db` and an empty `IDEAS.md`
- A small *archetype library* of starter constitutions:
  - `archetypes/python-library/`
  - `archetypes/python-web-service/`
  - `archetypes/data-pipeline/`
  - `archetypes/cli-tool/`
  - `archetypes/research-repo/`
  - Each archetype is a constitution skeleton plus 2–3 archetype-specific skills
- A "first feature in 30 minutes" walkthrough that proves the lifecycle on a
  trivial feature (e.g. "add a /healthz endpoint" or "add a CLI --version flag")

### Brownfield path (existing project, established patterns)

Characteristics:
- Existing code, tests, deploy pipelines, team conventions
- Tech stack is *fact*, not decision
- Constitution must be *extracted from observation*, not invented
- Hidden constraints (CI quirks, undocumented agreements) must surface before
  agents are unleashed

Required artifacts:
- A `cli/bootstrap.py brownfield <path>` (or a `brownfield-adoption.md` playbook)
  with these phases:
  1. **Archaeology pass** — agent inventories the host repo:
     - Languages, frameworks, build tools (parse `package.json`, `pyproject.toml`,
       `*.csproj`, `go.mod`, etc.)
     - Test frameworks and current pass count
     - Branching model (`git log --graph` heuristics)
     - Deploy mechanism (Dockerfiles, CI configs)
     - Existing convention files (`.editorconfig`, `pyproject.toml [tool.*]`, etc.)
  2. **Pain-point grilling** — Principal PM runs `/grill-with-docs` against the
     human, capturing existing frustrations and goals
  3. **Constitution draft** — Architect generates a *proposed* constitution from
     archaeology + grilling output, marked DRAFT until human approves
  4. **Adoption pilot** — choose one small feature or refactor as the first
     SDD-managed change. Measure friction. Adjust skills.
  5. **Coexistence rules** — explicit agreement about what SDD owns and what
     stays under the existing process (e.g. emergency hotfixes may bypass SDD)
- A `respect-existing` skill that constrains workers from rewriting code that
  isn't in their task scope, even if they think it's bad

### What the two paths share

Both paths converge on the same lifecycle (IDEA → BACKLOG → CLARIFY → SPEC → PLAN
→ TASKS → IMPLEMENT → REVIEW → DONE) and the same agents. Only the *bootstrap*
differs. This is the right design — the framework's value is the lifecycle, not
the entry path.

---

## 3. SDD + TDD integration

SDD currently *mentions* TDD in `/implement` ("test first, then implement") but
does not enforce it. TDD enforcement should be mechanical, not cultural.

Concrete moves:

- **Promote `tdd` from a skill to a binding article** in the framework's own
  generalized `principles.md`. Make it:
  - "Every implementation task that produces production code must produce a test
    in the same commit. Reviewers reject PRs where production-code lines added
    exceed test-code lines added unless the task is explicitly tagged
    [NO-TEST-NEEDED] with a written justification."
- **Add a `tdd-gate` skill** that the QA reviewer loads and runs:
  - Parses the diff
  - Checks: any `.py`/`.ts`/`.go`/etc. file in production paths has a
    corresponding change under `tests/` or `*_test.*` or `*.spec.*`
  - Returns PASS/FAIL with a one-line rationale
- **Update `/implement` prompt** to require the worker to output, in this order:
  1. The failing test
  2. The implementation that makes it pass
  3. The full test run output showing green
- **Make spec acceptance criteria testable.** The `feature-spec.md` template
  should require each acceptance criterion to be phrased as something a test can
  assert. The `/spec` prompt enforces this.

The SDD spec defines *what* to build; the TDD test defines *when it's built*. The
two are complementary halves of "definition of done."

---

## 4. The evolution mechanism (loop 1: project → framework)

This is the move that makes the name honest. Proposal:

- Add a `lessons/` directory to each PI: `sprints/PI-{N}/lessons.md`
- Every retro produces 0..N **lesson candidates**, each tagged:
  - `skill-update` — proposes a change to an existing skill
  - `new-skill` — proposes a new skill, with draft body
  - `agent-update` — proposes a change to an agent definition
  - `constitution-amendment` — proposes a change to a constitution article (requires ADR)
  - `template-update` — proposes a template improvement
- A new slash command `/evolve` (or extend `/retro`) that:
  - Reads the latest lessons.md
  - For each candidate, opens the relevant framework file, drafts the change,
    and queues a PR back to the framework repo
  - Records the lesson in `ledger/fleet.db` with provenance (which sprint, which
    feature, which retro action)
- A `lesson-curator` agent role (could initially be the Architect) that decides
  which candidates ship vs. defer

This is what makes the framework *evolving*: every sprint can leave it stronger
than it was, with full provenance for every change.

---

## 5. Adoption barrier reduction

Right now the smallest adoption gesture is "read 62KB of docs." That's a wall.
Three on-ramps to add:

1. **30-second elevator pitch** in the root `README.md` (still missing).
2. **5-minute quickstart** — one page, copy-paste commands, produces a working
   `/triage` against a sample idea.
3. **Project-type recipes** — short tutorials per archetype: "SDD for a Python
   library in 30 minutes," "SDD for a brownfield FastAPI service in 60 minutes."

The 62KB GENERALIZATION_SDD.md becomes the *deep dive*, not the entry point.

---

## 6. Concrete next moves (recommended order)

| # | Move                                                            | Why first | Effort |
|---|------------------------------------------------------------------|-----------|--------|
| 1 | Root `README.md` (elevator + quickstart + bootstrap pointer)     | Removes the biggest adoption barrier in 30 minutes of work | S |
| 2 | First pilot — fleet ledger schema (dogfood the lifecycle)        | Proves the framework works on itself before promising it works elsewhere | M |
| 3 | Generalize `principles.md` (the last Day-to-Day-coupled file)    | Makes the constitution coherent | S |
| 4 | Mark or replace Day-to-Day domain skills                         | Removes confusion for new users | S |
| 5 | TDD enforcement (binding article + `tdd-gate` skill + spec template change) | Locks in the second half of the methodology | M |
| 6 | `cli/bootstrap.py greenfield` + 1 archetype (python-library)     | First real proof of portability claim | M |
| 7 | `cli/bootstrap.py brownfield` archaeology agent                  | Validates the larger and harder of the two paths | L |
| 8 | Lesson loop (`/evolve`, `lessons/` directory, lesson-curator)    | Makes the framework actually "evolving" | L |

Moves 1–4 are the immediate cleanup that finishes PI-1 honestly. 5 closes the
SDD/TDD loop. 6–7 deliver the greenfield/brownfield promise. 8 makes the name
true.

---

## 7. Risks and open questions

- **Risk: framework over-engineering.** The framework itself can fall into the
  trap it warns host projects about. Spec sizing rule applies recursively — most
  framework changes should be small skill or template tweaks, not new agents or
  new lifecycle phases.
- **Risk: dogfooding paralysis.** The framework can be perpetually "almost ready
  to pilot." Setting a hard date for pilot-1 (or just doing it this week) avoids
  this.
- **Open question: how does the framework version itself?** When a host project
  adopts framework v0.1, what happens when v0.2 ships? Is there a migration
  path? Recommend semver on the framework + a `framework-version` field in the
  host's `mission.md`.
- **Open question: distribution model.** GitHub template repo, scaffolding CLI,
  npm/pip package, or something else? Pick *one* for v1.0, defer the others.
- **Open question: what counts as "the framework" vs "the host's adaptation"?**
  When the host modifies a framework skill, does that diverge or fork? Need a
  clear rule (e.g. "skills under `.github/skills/host/` are host-owned and never
  overwritten by framework upgrades; everything else is framework-owned").
