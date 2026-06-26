# AI Agent Super-Skill Reference

## Source

- **Repository**: [get-zeked/ai-agent-super-skill](https://github.com/get-zeked/ai-agent-super-skill)
- **Full Skill**: [SKILL.md](https://github.com/get-zeked/ai-agent-super-skill/blob/main/SKILL.md)
- **Loaded As**: Custom instruction in Copilot CLI

## What It Provides

A comprehensive framework for designing, building, and evaluating AI agents. Key capabilities used in this project:

| Capability | How We Use It |
|-----------|---------------|
| Gap Analysis Table | Map capability domains to coverage levels and identify improvement areas |
| Agent Architecture Patterns | ReAct, Plan-Execute patterns for the host project's agent evaluation |
| Subagent Coordination | Dispatching parallel explore agents for codebase analysis |
| Prompt Engineering | Evaluating and improving LLM prompt templates in `agent/prompts/templates.py` |
| Execution Planning | Phased improvement plan with dependency tracking |
| MCP Server Development | Reference for any future MCP integration work |
| RAG System Construction | Reference for knowledge graph / RAG roadmap items |

## How to Activate

This skill is loaded automatically via Copilot CLI custom instructions. No manual activation needed.

## Complementary Agents

- **Thinking Beast Mode** (`.github/agents/Thinking-Beast-Mode.agent.md`) -- Deep adversarial evaluation
- **AI Agent Super-Skill** (this reference) -- Methodology and framework
- **GitNexus** (`.claude/skills/gitnexus/`) -- Codebase knowledge graph

## When to Use

- Evaluating code quality across multiple dimensions
- Planning multi-phase improvement work
- Designing new agent capabilities or workflows
- Building MCP servers or RAG pipelines
- Optimizing LLM prompts
