# SDD Scorecard

Operational scorecard for the Spec-Driven Development framework. Review weekly during sprint review and monthly during PI review.

| Metric | Target | Measurement Method |
|--------|--------|--------------------|
| Spec-to-code traceability | 100% of merged tasks trace back to a spec requirement | For each completed task, verify the task ID maps to a spec requirement and changed file set in the traceability matrix and review report. |
| Test coverage delta | Non-negative on every merged feature; critical paths gain coverage | Compare before/after coverage or test count for touched modules during validation. Flag any drop below baseline or missing tests for new behavior. |
| Fleet success rate | >= 90% successful dispatches per sprint | `(done dispatches / total dispatches)` from `ledger/fleet.db`, excluding cancelled experiments that never launched. |
| Cycle time (idea to done) | Median <= 14 calendar days | Measure from first idea capture in `backlog/IDEAS.md` or `BACKLOG.md` to final `done` status in sprint tracking or merged delivery record. |
| Rework rate | <= 15% of completed tasks reopened | Count tasks moved from `done` back to `in-progress` or `blocked` after review, divided by completed tasks in the sprint. |
| Stop condition triggers | <= 1 preventable trigger per sprint | Log each stop condition event, classify root cause, and track whether it was avoidable based on missing prep, missing spec data, or conflict detection gaps. |
| Escalation count | Stable or decreasing trend; all escalations resolved within sprint | Count formal escalations to human review or Principal review and record closure timing in sprint notes or ledger blockers. |
| Ceremony skip rate | <= 10% of required ceremonies skipped | Compare scheduled ceremonies (triage, clarify, plan, tasks, review, retro, handoff as applicable) against completed artifacts for each active feature. |
| Knowledge capture (CONTEXT.md growth) | At least 1 meaningful update per sprint when new decisions emerge | Track dated additions to `CONTEXT.md`, ADRs, or clarification outcomes and verify they capture reusable conventions, decisions, or vocabulary. |

## Review Notes

- Review cadence: {WEEKLY_OR_PI}
- Owner: {OWNER}
- Last reviewed: {DATE}
