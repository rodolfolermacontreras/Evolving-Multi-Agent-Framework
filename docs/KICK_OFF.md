# Framework Kickoff Guide

## Purpose and Boundaries

Use this guide to begin or resume work in the Evolving Multi-Agent Framework.
The framework coordinates specification, implementation, review, and handoff;
it does not replace owner decisions, project-specific engineering practices, or
the host project's security controls.

Keep work scoped to the agreed feature or maintenance task. Do not change
constitution files, introduce dependencies, alter generated artifacts, or make
external changes unless the appropriate owner approval and workflow gate exist.

## Safety First

Before editing, confirm the repository, branch, and worktree are the intended
ones. Read the current Git status and preserve changes that were already
present. Do not reset, discard, or overwrite inherited work merely to make a
worktree look clean.

Use a dedicated feature branch and worktree for implementation. Keep secrets,
local ledgers, generated executive summaries, and host-specific state out of
commits unless the documented workflow explicitly says otherwise.

## Set Up the Framework

For a fresh clone, run:

```bash
make setup
make doctor
```

`make setup` prepares local framework state. `make doctor` checks that the
installation is usable. If `make` is unavailable, follow the alternative setup
instructions in the repository README and then run the documented health check.

## Canonical Session Read Order

Start each working session by reading these documents in order:

1. `INSTRUCTIONS.md`
2. `.github/copilot-instructions.md`
3. `spec-driven-development/CONTEXT.md`
4. `spec-driven-development/docs/HIGH_LEVEL_DEV_TRACKER.md`
5. The relevant management index under `spec-driven-development/docs/Management/`
6. `spec-driven-development/sessions/SESSION-MEMORY.md`
7. `spec-driven-development/constitution/roadmap.md`

For a task-specific continuation, also read the feature's specification,
implementation plan, task list, validation record, and handoff material before
making changes.

## Recovering Work

Treat an existing worktree as inherited context, not as a blank slate. Inspect
its status, recent commits, and task artifacts before acting. Preserve unrelated
changes, identify which changes belong to the current task, and validate the
baseline when a focused test or check exists.

When the inherited state is ambiguous, stop before destructive operations and
record the uncertainty in the task handoff or request an owner decision.

## Select the Right Workflow

Use the smallest workflow that matches the change:

- Small, localized fixes use a focused regression test, a minimal fix, and both
  review stages.
- Features use the lifecycle from idea and clarification through specification,
  plan, tasks, implementation, review, and completion.
- Cross-cutting, architectural, dependency, or schema changes require the
  applicable design decision and approval gates before implementation.

Workers receive a self-contained task brief and work only within its stated
file scope. Parallel work is allowed only after confirming that tasks do not
modify the same files or shared resources.

## Validate and Review

Follow test-driven development: define the expected behavior with a failing
test where practical, implement the smallest change, and rerun focused
validation. Run the relevant project checks before publishing.

Review happens in order:

1. Spec compliance: confirm there is nothing missing, extra, or contradictory.
2. Code quality: check correctness, security, maintainability, conventions,
   and test coverage.

Resolve findings and re-review fixes before integration. Do not treat a passing
test suite as a substitute for either review stage.

## Commit, Publish, and Hand Off

Commit only the files belonging to the task, using the repository's documented
commit convention. Push the feature branch, open a review using the repository's
approved method, and merge only through the documented integration path.

Before ending the session, update the durable handoff record with the completed
work, validation evidence, unresolved risks, and the next concrete action. Keep
the handoff factual so another contributor can continue without relying on chat
history.

## Durable References

- Repository setup and session entry point: `INSTRUCTIONS.md`
- Framework overview and setup alternatives: `README.md`
- Shared terminology: `spec-driven-development/CONTEXT.md`
- Framework rules and quality expectations:
  `spec-driven-development/constitution/`
- Workflow templates: `spec-driven-development/templates/`
- Feature artifacts: `spec-driven-development/specs/`
- Session continuity: `spec-driven-development/sessions/SESSION-MEMORY.md`
- Reusable adoption guidance: `spec-driven-development/GENERALIZATION_SDD.md`