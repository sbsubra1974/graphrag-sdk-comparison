# Project skills

Skills live in `.claude/skills/<name>/SKILL.md` so Claude Code picks them up automatically
when this repo is opened. This file is the human-readable index.

| Skill | Use it when |
|---|---|
| [ingest-pdf](.claude/skills/ingest-pdf/SKILL.md) | Loading a new PDF into Neo4j (parse, chunk, embed, extract graph) |
| [run-comparison](.claude/skills/run-comparison/SKILL.md) | Asking one question across all six SDK and retrieval variants |
| [add-mcp-server](.claude/skills/add-mcp-server/SKILL.md) | Adding or enabling an MCP server for Claude Code and the Agent SDK |

To add a skill: create `.claude/skills/<name>/SKILL.md` with `name` and `description`
frontmatter, then add a row here in the same commit.
