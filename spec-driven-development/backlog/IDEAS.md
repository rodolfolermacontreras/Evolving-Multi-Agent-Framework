# Ideas Inbox

Raw ideas captured here. Triage moves them to BACKLOG.md with RICE scoring.

## Format
- **[YYYY-MM-DD]** Idea title -- brief description

## Ideas

- **[2026-05-16]** Dashboard "About / Where we are" section -- "the website needs to include a section talking about the purpose of the project, and where we are in the development of the project (high level picture) so people that is new to the project can see what is happening (I know that this is very meta, because the website right now is showing the progress on this project, which is a meta project that will help us to other projects to use the spec driven development framework)" -- captured verbatim from human, 2026-05-16 -> BACKLOG P2 (SDD-010)

- **[2026-05-16]** Dashboard data-freshness investigation -- "the values in there seemm static" -- live container rebuilds the HTML per request but reads a snapshot of the repo that was baked into the image at deploy time; new commits/ledger writes do not appear until next `az containerapp up`. Decide whether to (a) document this as expected, (b) auto-redeploy on push, or (c) mount/sync live repo into container. -> BACKLOG P2 (SDD-009)

- **[2026-05-25]** Navigation layer on the visual dashboard -- "this needs to be added to the visual interface website" -- the three-tier Management/ navigation pyramid (tracker -> PI INDEX -> sprint SPEC) should be surfaced in the live dashboard so humans can see what is being developed and track it visually, not just via Markdown files on disk. Adds transparency for non-developer stakeholders. Natural fit for S4 (Live UI v2 Spec) requirements. -> Route to PM for triage; include as S4 requirement when ADR-0010 is approved.

- **[2026-05-25]** Live per-agent context window visibility and human intervention -- "this other system allows you to see the context window for each agent working on each task, we can decide to interfere or let it run. We do not have that here" -- the ability for a human to see into each running agent's context window in real-time and choose to steer or halt mid-execution. Current framework has only after-the-fact visibility (AGENT_NOTES.md, fleet ledger, HITL gates). This would require agents to emit real-time progress events into the ledger and the dashboard to stream them. Significant infrastructure work. -> Route to PM for triage + Architect for feasibility assessment.

- **[2026-06-02]** Auto-launch dashboard on session start -- "that dashboard has to be launched automatically when we start a project, at least for me. The owner of this framework." -- when the framework owner starts a Copilot CLI session in this repo, the live Azure dashboard should open automatically in the browser. Could be a VS Code task, a session-start hook in copilot-instructions.md, or a script that checks if the dashboard tab is already open. For non-owner users, the URL should be prominently displayed at session start.
