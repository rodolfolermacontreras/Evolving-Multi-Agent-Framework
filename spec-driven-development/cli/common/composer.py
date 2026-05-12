"""Prompt composition scaffold.

Purpose:
    Combine a base role prompt, selected skills, project context, and task brief
    into a runtime prompt suitable for manual or automated worker dispatch.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable


@dataclass(slots=True)
class PromptComponents:
    """Structured prompt parts used during composition."""

    base_prompt: str
    skills: list[str] = field(default_factory=list)
    context_blocks: list[str] = field(default_factory=list)
    task_brief: str = ""


def compose_prompt(components: PromptComponents) -> str:
    """Compose a runtime prompt from the provided prompt components."""
    parts: list[str] = [components.base_prompt.strip()]
    parts.extend(skill.strip() for skill in components.skills if skill.strip())
    parts.extend(block.strip() for block in components.context_blocks if block.strip())
    if components.task_brief.strip():
        parts.append(components.task_brief.strip())

    runtime_prompt = "\n\n".join(parts)
    # TODO: add structured conflict notes, output contract, and prompt hashing.
    return runtime_prompt


def append_sections(base: str, sections: Iterable[str]) -> str:
    """Append prebuilt sections to an existing prompt body."""
    chunks = [base.strip(), *[section.strip() for section in sections if section.strip()]]
    return "\n\n".join(chunk for chunk in chunks if chunk)
