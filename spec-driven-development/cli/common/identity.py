"""Agent identity scaffold.

Purpose:
    Define worker specialization and naming rules for the SDD fleet, including
    the ``{role}-{firstname}-{domain}-{NNN}`` convention from ADR-003.
"""

from __future__ import annotations

from dataclasses import dataclass


FIRST_NAME_POOL = [
    "alex",
    "blair",
    "casey",
    "devon",
    "jordan",
    "morgan",
]


@dataclass(slots=True)
class AgentIdentity:
    """Structured identity for a specialized worker."""

    role: str
    first_name: str
    domain: str
    sequence: int

    @property
    def identifier(self) -> str:
        """Return the rendered agent identifier."""
        return f"{self.role}-{self.first_name}-{self.domain}-{self.sequence:03d}"


def next_identity(role: str, domain: str, sequence: int = 1) -> AgentIdentity:
    """Create the next specialized identity using the fixed first-name pool."""
    first_name = FIRST_NAME_POOL[(sequence - 1) % len(FIRST_NAME_POOL)]
    # TODO: replace with ledger-backed sequence allocation and specialization rules.
    return AgentIdentity(role=role, first_name=first_name, domain=domain, sequence=sequence)
