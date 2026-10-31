---
name: add-mcp-server
description: Add, enable or change an MCP server for this repo, for both Claude Code and the Agent SDK variants.
---

1. Edit `config/mcp_servers.yaml` only. Add an entry under `servers:` with `type`
   (`stdio`, `http` or `sse`), `enabled: true`, and either `command`/`args`/`env` or `url`/`headers`.
2. Reference secrets as `${VAR}` and add `VAR=` to `.env.example`. Never inline a secret.
3. Run `python scripts/sync_mcp.py` to regenerate `.mcp.json`.
4. Run `graphrag-cmp mcp-list` and `pytest tests/test_mcp_config.py`.
5. Commit the YAML, `.mcp.json` and `.env.example` together: `mcp: add <name>`.
