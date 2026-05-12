# ADR-0004: Principal Executive Manager as Orchestrator and Single Entry Point

- Status: Accepted
- Date: 2026-05-12
- Deciders: Rodolfo Lerma (project owner)
- Supersedes: original passive-reporter framing of the Principal Executive Manager
- Related: ADR-0001 (SDD framework), ADR-0002 (two-folder split), ADR-0003 (specialization naming)

---

## Context

The framework has four Principal agents (Executive Manager, Product Manager,
Architect, Software Developer) plus a fleet of generic workers. Until now, the
human had no single entry point: they had to know in advance which Principal owned
which question, then open that Principal's chat directly. The original Principal
Executive Manager was scoped as a passive reporter -- it could read only
`exec/state.md` and produce status summaries. It could not kick off work, could
not actively answer ad-hoc questions outside its briefing, and could not act as a
"front desk" for the project.

This created several problems:

1. The human had to mentally route their own questions ("Is this a PM thing or an
   Architect thing?"), which defeats the point of having a coordinator.
2. New ideas had no clear owner of capture. The convention was "drop into
   IDEAS.md and open the PM with `/triage`," but that requires the human to
   remember the protocol and do the routing themselves.
3. There was no agent with full project picture awareness on the human's behalf.
   The four Principals each owned a slice; nobody owned the whole.
4. The vendor/engagement-manager analogy that the human reasoned from was missing
   its central character: the engagement manager who takes the client's call.

## Decision

Re-scope the existing Principal Executive Manager from "passive reporter of
`exec/state.md`" to **active orchestrator and single human-facing entry point**.

Concretely:

1. The Executive Manager is the human's default entry point for any question,
   request, idea, or status check. The human talks to the Executive Manager first.
2. The Executive Manager owns kickoff: when the human brings a new idea, the
   Executive Manager captures it in `IDEAS.md` and hands it off to the PM via the
   labeled handoff, with full context.
3. The Executive Manager owns the **ad-hoc Q&A routing protocol**, exposed as the
   `/ask` slash command:
   - Try to answer from own context (state.md + big-picture awareness).
   - If not, classify the question, hand off to the right Principal, wait for the
     answer, **synthesize** it to executive register, return to the human.
   - Update `state.md` if the answer changed project state.
4. The Executive Manager retains all existing guardrails: no code, no specs, no
   Level 1 or Level 2 decisions, no direct dispatch of workers.
5. Read access expands from "only `exec/state.md`" to "defaults to `exec/state.md`,
   may read raw artifacts to answer routed questions, never modifies any artifact
   other than (optionally) `exec/state.md`."
6. Output to the human is *always* at executive register, regardless of how deep
   the underlying answer was.
7. The other three Principals (PM, Architect, SW Dev) gain a new return-handoff:
   "Return to Executive Manager with Answer."
8. The human is **not walled off** from individual Principals. The Executive
   Manager is the *default* entry point, not the only one. The human is welcome
   to attend ceremonies (sprint planning, PI planning, retros) directly.

We considered adding a fifth Principal ("Chief of Staff" or "Project Orchestrator")
to preserve the Executive Manager's previous isolation. We rejected this because
(a) re-scoping is simpler than adding a new role, (b) the previous isolation was
not architecturally load-bearing -- it was a stylistic constraint that produced
weak briefings rather than strong ones, and (c) four Principals is already the
right cognitive ceiling for the human to track.

## Consequences

### Positive

- The human has one phone number to call.
- New ideas have a clear capture owner.
- The big-picture is owned by exactly one agent on the human's behalf.
- The vendor/engagement-manager mental model is intact and complete.
- Other Principals can return answers to the Executive Manager rather than
  expecting the human to track partial answers across multiple chats.

### Negative or risky

- The Executive Manager becomes a potential bottleneck if it tries to answer too
  much itself. Mitigation: the routing matrix is explicit; the agent's
  non-negotiable list is unchanged ("when in doubt, route").
- Read-access expansion means the Executive Manager could drift into producing
  engineering-depth output. Mitigation: the agent definition repeats the
  "executive register only" rule three times and includes error-handling for the
  case where it does not understand a returned answer.
- Synthesizing routed answers introduces a translation layer that could lose
  fidelity. Mitigation: the synthesis format always cites the source Principal
  so the human can ask for the raw answer if needed.

### Process changes

- `spec-driven-development/README.md` "How to Get Started" updated to make the
  Executive Manager the entry point for both new ideas and ad-hoc questions.
- `.github/copilot-instructions.md` Architecture section updated to describe the
  Executive Manager as orchestrator rather than reporter.
- `spec-driven-development/CONTEXT.md` glossary updated.
- `spec-driven-development/constitution/mission.md` non-negotiable updated:
  the Executive Manager is read-restricted on *modifications*, not on *reads*.
- New slash command `/ask` registered.
- Three Principal agent files (`principal-product-manager`, `principal-architect`,
  `principal-software-developer`) gain a "Return to Executive Manager with Answer"
  handoff.

## Status

Accepted. Implemented in commit that introduces this ADR.
