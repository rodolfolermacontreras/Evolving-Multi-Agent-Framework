# Ideas Inbox

Raw ideas captured here. Triage moves them to BACKLOG.md with RICE scoring.

## Format
- **[YYYY-MM-DD]** Idea title -- brief description

## Ideas

- **[2026-05-16]** Dashboard "About / Where we are" section -- "the website needs to include a section talking about the purpose of the project, and where we are in the development of the project (high level picture) so people that is new to the project can see what is happening (I know that this is very meta, because the website right now is showing the progress on this project, which is a meta project that will help us to other projects to use the spec driven development framework)" -- captured verbatim from human, 2026-05-16 -> BACKLOG P2 (SDD-010)

- **[2026-05-16]** Dashboard data-freshness investigation -- "the values in there seemm static" -- live container rebuilds the HTML per request but reads a snapshot of the repo that was baked into the image at deploy time; new commits/ledger writes do not appear until next `az containerapp up`. Decide whether to (a) document this as expected, (b) auto-redeploy on push, or (c) mount/sync live repo into container. -> BACKLOG P2 (SDD-009)
