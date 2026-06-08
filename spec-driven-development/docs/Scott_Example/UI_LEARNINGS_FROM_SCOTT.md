# UI Learnings Brief: Adopting Patterns from Scott's WWIC Analyst Backlog

## Why this brief exists

A team member (Scott) shared his "WWIC Analyst Backlog" UI — a tool he built for managing a feature backlog mirrored to Azure DevOps but with a JSON file as the source of truth. We are not adopting his tool. We are extracting the **patterns that solve problems we currently have** and proposing how to streamline our existing Azure-hosted dashboard around them.

This brief connects directly to the navigation-layer feedback already in play: Scott's UI is, in effect, the *live* expression of the same transparency principle the Markdown tracker + PI/Sprint INDEX structure provides at rest. Both are "views of one truth." Adopting his strongest patterns lets the dashboard finish the job — give a human a single screen that answers *what is happening, where it sits in the process, and where the documents are*.

## What we observed

Scott's tool has two screens:

**A list view.** Every work item in a single dense table — ID, type, status, priority, area, title, doc counts, ADO id, last-updated. Color-coded status tags. Sidebar with the same items as a quick-jump list. Filters at the top (status, type, area, "hide done," "blocked-on-owner only"). A "valid" pill that signals the JSON file itself passes schema validation.

**A detail view.** Title and meta header. A horizontal status pipeline showing every stage in the workflow, each in its own color, with the current stage filled and visually emphasized. A description card with full markdown. An acceptance-criteria card. **Three separate documentation cards** — Story Docs, Spec Docs, Sprint Docs — each linking to a Markdown file at a known path. A commits card listing every git commit whose message references the work item, with branch, message, and timestamp.

The whole thing is monospace, dark, near-zero chrome. The aesthetic is "this was built by someone who lives in an IDE" — which matches the audience.

## The five learnings, with mapping to what we have

### 1. The status flow pipeline (highest-value pattern)

Eight named stages laid out horizontally: Intake → Story Drafting → Spec Drafting → Planning Ready → In Development → UAT → Accepted → Done. Each stage has its own color. The current stage is filled and glows; pending stages are outlined only.

**Why it works.** It answers "where is this work in the process?" in a single glance. No reading. No clicking. The lifecycle is *visible*, which means deviations from it are also visible — if something has been in "In Development" for two weeks, that fact is staring at you.

**Map to us.** This maps almost perfectly onto our lifecycle: `IDEA → BACKLOG → CLARIFY → SPEC → PLAN → TASKS → IMPLEMENT → REVIEW → DONE → /replan`. Put this exact pipeline on **every sprint card** and **every feature card** in the dashboard, and put a static rendering of it at the top of the Markdown sprint detail file too. One visual, two surfaces, same information. This is the single highest-leverage change.

### 2. Layered documentation cards

On the detail view, Scott surfaces three separate document cards: Story Docs, Spec Docs, Sprint Docs. Each is a clickable link to a Markdown file at a deterministic path (`docs/requirements/stories/...`, `docs/requirements/specs/...`, `docs/sprints/...`). Three layers of documentation, surfaced side by side.

**Why it works.** The layered-doc principle (intent → contract → execution) is made *operational*. You don't have to remember where the spec lives; the UI tells you, and you click. It is the dashboard equivalent of our drill-down: tracker → PI INDEX → Sprint folder.

**Map to us.** For each work item / feature, expose four cards in the dashboard, mirroring our standing artifacts:
- **Constitution articles touched** (links into `spec-driven-development/constitution/`)
- **Spec** (the feature's SDD spec)
- **Sprint detail** (link into `docs/Management/PI-#/Sprint-#/`)
- **ADRs referenced** (the architectural decisions this work depends on or produced)

This makes the layered-documentation discipline visible *and* removes the "where is the spec for this thing?" friction. It also makes missing docs glaringly obvious — an empty card is a problem.

### 3. The commits panel

Scott's detail view pulls every git commit whose message references the work-item ID and lists them inline: short SHA, branch, message, timestamp. The work item and the code are stitched together in one view.

**Why it works.** Traceability becomes visible, not just queryable. Anyone reading the work item also sees the code activity it produced — branches, message discipline, recency.

**Map to us.** We already have a SQLite ledger that records every dispatch with full traceability. We have *more* data than Scott has — but it's locked in a database that nobody opens. Mirror his pattern with a **Dispatches card**: for each feature/sprint, show every dispatch from the ledger — agent, role, task, status, when. Optionally a second card for git commits filtered by feature ID, matching his pattern directly. The ledger stays authoritative; the dashboard becomes its readable projection.

### 4. The "valid" pill and JSON-as-source-of-truth signaling

The top-right of his list view carries a small green "valid" pill. It is telling the reader: the underlying JSON file passes schema validation right now. The data you are looking at is structurally sound.

**Why it works.** It surfaces a normally-invisible health signal. If validation fails, that pill flips, and the reader knows not to trust the page until it's fixed. This is a tiny element with a large reliability payoff.

**Map to us.** Our equivalent invisible health signals are:
- Constitution semver consistency across files
- Skill-frontmatter schema validity
- Whether the ledger is reachable
- Whether any feature's tracker/INDEX entry is stale relative to its last dispatch

Surface these as small pills in the dashboard header. Green for healthy, amber for warn, red for fail. Click-through to the failure detail. This costs little and gives the reader durable confidence that what they're seeing reflects reality.

### 5. The aesthetic system (adopt selectively, do not photocopy)

Scott's UI is monospace throughout (JetBrains Mono or equivalent), near-black background with a slight blue undertone, color-coded badges with thin borders, and almost no decorative chrome. Status colors are consistent: yellow for incoming, cyan for drafting, green for ready, magenta for active, gray for not-yet.

**Why it works for him.** His audience lives in editors. Monospace + dark + dense = native.

**Map to us.** Our audience is the same kind of person. Adopt the principle (IDE-native, dense, monospace, color-as-information) — do not photocopy his specific palette or token names. Define our own color tokens for lifecycle states and reuse them everywhere a state appears (dashboard, sprint Markdown rendering, agent UIs). One color per state, used consistently across surfaces.

## What we should NOT copy

- **The ADO mirror model.** Scott's tool exists in part to reconcile ADO. We have no ADO. The JSON-source-of-truth concept is good; the ADO machinery is irrelevant.
- **The drag-to-reorder backlog interaction.** Useful for him; for us, ordering is determined by the PM agent and the PI plan, not by mouse.
- **Per-row inline ID/ADO references.** Our work items live in the ledger and Markdown, not in an external tracker — we don't need an "external system ID" column.
- **The flat backlog.** Scott has one backlog. We have PIs, sprints, and features, in that nesting. Use his patterns *inside* our hierarchy, not in place of it.

## Mapping summary

| Scott's concept            | Our equivalent                                                   |
|----------------------------|------------------------------------------------------------------|
| Work item (WI-#####)       | Feature (SDD-###) inside a Sprint inside a PI                    |
| Backlog (flat list)        | `HIGH_LEVEL_DEV_TRACKER.md` + per-PI `INDEX.md`                  |
| Status flow stages         | Our lifecycle: IDEA → … → DONE → /replan                         |
| Story / Spec / Sprint docs | Constitution refs / Spec / Sprint detail / ADRs                  |
| Commits panel              | Ledger dispatches + git commits filtered by feature ID           |
| "valid" pill               | Health pills: constitution semver, skills schema, ledger, stale  |
| JSON source of truth       | Our existing in-repo Markdown + ledger; no change needed         |

## Proposed streamlining of the current dashboard, in priority order

1. **Add the lifecycle pipeline component** and render it on every feature card and every sprint card. Use it as the single answer to "where is this in the process?"
2. **Replace per-feature scattered links with the four-card documentation row** (Constitution / Spec / Sprint / ADRs). Empty cards are intentional — they make missing artifacts visible.
3. **Add a Dispatches card** that reads from the ledger. This is where the ledger finally becomes a thing humans look at.
4. **Add the health-pills strip** in the dashboard header.
5. **Standardize the lifecycle color tokens** across the dashboard and the rendered Markdown views, so a state has one color everywhere.

Anything that does not directly serve "open the dashboard, instantly know where every active piece of work is and where its documents live" is a candidate for removal, not addition. Streamlining means subtracting noise as much as adding signal.

## Questions to answer before implementing

- Does the current dashboard render Markdown from the repo, or read state purely from the ledger? The four-card documentation row works cleanest if it can deep-link into rendered Markdown.
- Is there an existing lifecycle-state field per feature in the ledger schema, or do we need to add one and backfill?
- Are dispatches in the ledger already tagged by feature ID, or only by sprint/PI? The Dispatches card needs feature-level grouping.
- What is the cost (in scale-to-zero terms) of adding the health-pill checks to the dashboard's cold-start path? If meaningful, run them on a schedule and cache.

Propose answers and a small implementation spec before touching code. This is a UX change with structural implications; it should go through the normal CLARIFY → SPEC → PLAN path, not be hand-built.
