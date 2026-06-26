---
name: archetype-recommender
description: "Use when the human says they're starting a new project (greenfield or brownfield). Walks a guided 5-6 question conversation to recommend the best-fit archetype out of the 5 that ship with the framework, with reasoning. If none fit, guides the human to invent a new archetype via /evolve. Owned by the Executive Manager."
argument-hint: "What kind of project are you starting? (one sentence is enough)"
license: MIT
metadata:
  author: emf-framework
  version: '1.0'
---

# Archetype Recommender

Guided intake for the Executive Manager. Use it to help a human choose the best starting archetype without expecting them to know framework vocabulary or bootstrap syntax.

## Required Reading

Before recommending, read:

- `spec-driven-development/archetypes/README.md` - index of the 5 shipped archetypes
- `spec-driven-development/archetypes/python-library/README.md`
- `spec-driven-development/archetypes/python-web-service/README.md`
- `spec-driven-development/archetypes/data-pipeline/README.md`
- `spec-driven-development/archetypes/cli-tool/README.md`
- `spec-driven-development/archetypes/research-repo/README.md`

Use those files as source of truth. Do not invent extra shipped archetypes.

## When to Use

Load this skill when the human says or implies they are starting a new project, bootstrapping a repo, adopting an existing repo into SDD, or asking which archetype to choose. Use it for both greenfield and brownfield. Do not use it for ordinary feature kickoff after an archetype is already selected.

## Conversation Protocol

Follow the Matt Pocock grill-me pattern:

1. Ask one question at a time.
2. Include options and a recommended default whenever enough information exists.
3. If the human says "I don't know", use the recommendation and move on.
4. After 5-6 questions, recommend one archetype with reasoning, confidence, alternatives, and next command.
5. If the answer is contradictory, ask the human to resolve the contradiction before reporting.

## Questions to Ask

### Q1. What is the primary deliverable?

Ask:

```markdown
What is the primary deliverable, meaning the thing users or dependents will get?

A. A library someone imports (`from mylib import x`)
B. A running service that handles requests over HTTP/WebSocket/gRPC
C. A pipeline that reads input data, transforms it, and writes output
D. A command-line tool someone runs from a shell
E. A reproducible analysis or research output (notebook, paper, model)
F. None of the above

Recommendation: I need your answer here before I can recommend responsibly. Which option is closest?
```

If the human chooses F, trigger the fallback flow after asking which shipped shape is least wrong.

### Q2. Who is the primary user?

Options: A. Other developers (your code is a dependency in their stack); B. End users via a UI or API client; C. Future you reviewing analysis results; D. Operators running scheduled or triggered jobs.

Recommendation mapping: Library -> A; Service -> B; Research -> C; Pipeline -> D; CLI -> A if developer-facing, D if operator-facing.

### Q3. What runs your code in production?

Options: A. Imported into another process (no runtime of its own); B. Web server (uvicorn, gunicorn, asgiref, Cloud Run, Lambda, etc.); C. Scheduler (Airflow, Prefect, Dagster, cron, Azure Data Factory, etc.); D. Shell on a developer or operator's machine; E. Jupyter / interactive notebook server.

Recommendation mapping: Library -> A; Service -> B; Pipeline -> C; CLI -> D; Research -> E.

### Q4. What kind of test coverage matters most?

Options: A. Unit tests of pure functions and classes; B. Integration tests of HTTP contracts and persistence; C. Data-quality checks on transformed outputs; D. CLI integration tests (subprocess + golden files); E. Notebook execution + figure/output verification.

Recommendation mapping: Library -> A; Service -> B; Pipeline -> C; CLI -> D; Research -> E.

### Q5. Persistent state or stateless?

Options: A. No persistent state (pure code, in-memory); B. Persistent state via a real database (Postgres, MySQL, SQLite, etc.); C. Persistent state via files written somewhere (parquet, JSON, blob storage); D. Persistent state in version control (notebooks, configs).

Recommendation mapping: Library -> A; Service -> B if it needs data, otherwise A; Pipeline -> C; CLI -> A or C depending on whether it writes artifacts; Research -> D, or C when generated data artifacts are central.

### Q6. One-line summary of the project

Ask for the human's own words. Recommend this shape: "I am building <thing> for <user> so they can <outcome>." Use it to confirm that the recommendation feels right.

## Recommendation Logic

Use Q1 as the primary signal:

| Primary deliverable (Q1) | Recommend |
|---|---|
| A library | `python-library` |
| HTTP service | `python-web-service` |
| Data pipeline | `data-pipeline` |
| CLI tool | `cli-tool` |
| Research/analysis | `research-repo` |
| None of the above | trigger fallback to `/evolve` |

Cross-check Q3 and Q5. If Q1 says library but Q3 says web server, service but Q3 says imported, pipeline but no scheduler/data state, CLI but Q3 says web server, or research but Q3 says scheduler/web server, surface the contradiction and ask the human to resolve it. Do not silently override Q1.

## Confidence Rules

- HIGH: Q1, Q3, Q4, and Q5 all align with the same archetype.
- MEDIUM: Q1 is clear but one secondary signal is mixed or optional.
- LOW: Q1 is clear but multiple secondary signals conflict, or the project spans two archetypes.

Always recommend exactly one primary archetype. Use alternatives for uncertainty.

## Recommendation Output Format

After Q6, produce this report:

````markdown
## Archetype Recommendation

Based on your answers, I recommend: **`<archetype-name>`**

### Why
- Q1 deliverable: <answer> -> primary signal for `<archetype>`
- Q2 user: <answer>
- Q3 runtime: <answer>
- Q4 testing: <answer>
- Q5 state: <answer>

### Confidence
HIGH | MEDIUM | LOW

### Alternatives worth considering
- `<other-archetype>` -- if you said X, this would be the answer instead

### Next step
Run:
```powershell
python spec-driven-development\cli\bootstrap.py greenfield <recommended-archetype> `
  --project-name <YourProjectName> `
  --owner "Your Name" `
  --target ..\<YourProjectName>
```

Or if you want to run brownfield against an existing repo:
```powershell
python spec-driven-development\cli\bootstrap.py brownfield ..\<existing-project> `
  --owner "Your Name" --draft-only
```

Reply "approve" to proceed, "alt <name>" to use a different archetype, or "evolve" if none fit.
````

If the human already said this is brownfield, make the brownfield command the primary next step and mention greenfield second.

## Fallback to /evolve

If the human chooses "F. None of the above" on Q1, or says after the recommendation that none of the 5 fit, produce this:

```markdown
## No existing archetype fits

That's useful information. The framework ships 5 archetypes that cover ~90% of solo-dev project shapes, but the framework is designed to evolve. New archetypes are created when a real project surfaces the need.

### Recommended path
1. Start with the **closest** existing archetype (I recommend: `<closest>` because <reason>).
2. Bootstrap with that.
3. Walk one feature through the lifecycle. Notice what's awkward.
4. File a `lesson-capture` candidate tagged `new-archetype` with proposal: a new archetype called `<your-name>` should ship with `<key-properties>`.
5. After the feature ships, run `/evolve` to curate the candidate into a real archetype that future projects can use.

Alternative: if you have time and the project shape is *very* different, you can fork the closest archetype manually under `spec-driven-development/archetypes/<your-name>/` before bootstrapping, then use it. I can guide you through that -- say "fork <name>" and I'll walk you through it.

Reply with your choice: `start <closest>`, `fork <name>`, or `wait` to think about it.
```

Choose `<closest>` by asking which shipped shape is least wrong: library, service, pipeline, CLI, or research. If the human is unsure, choose the archetype that matches the expected runtime.

## Guardrails

- Never recommend more than ONE archetype as the primary recommendation.
- Always cite the answers that drove the recommendation.
- If the human says "I don't know", recommend the default and move on.
- If the human is starting brownfield, Q1-Q5 are still useful, but the next step suggests `bootstrap.py brownfield --draft-only`.
- Do not add this skill to slash command grids. It is loaded by the Executive Manager on demand.
- Do not pretend `/evolve` instantly creates a polished archetype. It curates lessons after real use.
