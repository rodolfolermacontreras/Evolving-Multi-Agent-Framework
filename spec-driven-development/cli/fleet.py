"""Fleet orchestrator scaffold.

Purpose:
    Compose prompts, generate dispatch packets, and track dispatch metadata in the
    SDD ledger. Phase 1 is manual dispatch generation only; worker processes are
    launched by the operator after reviewing the emitted packets.

Current status:
    TODO: Phase 2 implementation.
    For now, fleet dispatch is manual via /fleet prompt command.
"""

from __future__ import annotations

import argparse
from pathlib import Path


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser for fleet orchestration commands."""
    parser = argparse.ArgumentParser(description="Fleet orchestrator scaffold.")
    parser.add_argument("command", nargs="?", default="dispatch", help="Command to run.")
    parser.add_argument("--sprint", dest="sprint", help="Sprint identifier or path.")
    parser.add_argument("--batch", dest="batch", help="Batch number or identifier.")
    return parser


def main() -> int:
    """Run the fleet CLI scaffold."""
    parser = build_parser()
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[2]
    print(f"TODO: implement fleet orchestration for command '{args.command}'.")
    print(f"Project root: {project_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
