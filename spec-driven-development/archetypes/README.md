# SDD Archetypes

Archetypes are lightweight starter profiles for greenfield host projects that adopt Spec-Driven Development. They keep the framework portable as Markdown and YAML while giving new projects a practical first constitution, backlog, and domain skill baseline.

Use an archetype with the bootstrap helper:

```bash
python spec-driven-development/cli/bootstrap.py greenfield python-library --project-name MyLib --owner "Your Name" --target ../MyLib
```

Each archetype may provide:

- `constitution/`: the six host constitution files with `{{PROJECT_NAME}}`, `{{OWNER}}`, and `{{DATE}}` placeholders
- `skills/`: domain skills copied into the host project's `.github/skills/domain/`
- `backlog/IDEAS.md` and `backlog/BACKLOG.md`: optional starter backlog templates

The archetype does not replace project judgment. Treat it as a starting point, then refine it through the Executive Manager, Product Manager, Architect, and Developer workflow.
