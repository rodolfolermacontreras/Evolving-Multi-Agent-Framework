# Python stdlib CLI Pattern for Framework Utilities

Provenance: LESSON-001, source feature `specs/2026-05-12-fleet-ledger/`

---

## When to use

Any Python script under `spec-driven-development/cli/` or
`spec-driven-development/ledger/` that provides a command-line interface
for framework contributors.

## Rules

1. **Stdlib only at runtime.** Import only `argparse`, `datetime`, `json`,
   `pathlib`, `re`, `shutil`, `sqlite3`, `subprocess`, `sys`, and typing
   helpers. Third-party libraries require Level 2 approval.
2. **Testable `main(argv)` signature.** Every script exposes
   `main(argv: list[str] | None = None) -> int` so pytest can call it
   without subprocess overhead.
3. **`if __name__ == "__main__": sys.exit(main())`** at the bottom.
4. **Explicit `parse_args(argv)` function.** Separate parsing from logic
   so tests can construct `Namespace` objects directly when needed.
5. **`pathlib.Path` for all file operations.** No `os.path` string
   manipulation.
6. **Default paths relative to `__file__`**, not the working directory.
   Example: `Path(__file__).resolve().with_name("fleet.db")`.
7. **Custom exception class** for expected failures.
   Example: `class LedgerInitError(Exception)`.
8. **Print errors to stderr**: `print(f"ERROR: {exc}", file=sys.stderr)`.
   Return non-zero from `main()` on failure.
9. **Subcommands via `add_subparsers`** when a script has more than one
   action. Each subcommand gets its own handler function.
10. **UTC timestamps** via `datetime.now(timezone.utc)` formatted as
    ISO 8601 with trailing `Z`.

## Skeleton

```python
#!/usr/bin/env python3
"""One-line description of the script."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


class MyError(Exception):
    """Expected failure with a human-readable message."""


def do_work(path: Path) -> None:
    """Core logic, tested directly by unit tests."""
    ...


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="my_script.py",
        description="What this script does.",
    )
    parser.add_argument("--flag", help="Explain the flag.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])
    try:
        do_work(Path(args.flag))
    except (MyError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

## Reference implementations

- `spec-driven-development/ledger/init_ledger.py` -- single-action script
- `spec-driven-development/ledger/ledger_cli.py` -- multi-subcommand script
- `spec-driven-development/cli/bootstrap.py` -- multi-subcommand with file I/O
