"""Load MCP server definitions from config/mcp_servers.yaml.

The same YAML feeds two consumers:
- Claude Code, via the generated .mcp.json (scripts/sync_mcp.py)
- the Claude Agent SDK, via agent_sdk_servers() passed to ClaudeAgentOptions(mcp_servers=...)
"""

import os
import re
from pathlib import Path
from typing import Any

import yaml

CONFIG_PATH = Path(__file__).resolve().parents[2] / "config" / "mcp_servers.yaml"
_VAR = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}")


def _expand(value: Any, keep_placeholders: bool) -> Any:
    if isinstance(value, str):
        if keep_placeholders:
            return value
        return _VAR.sub(lambda m: os.getenv(m.group(1), ""), value)
    if isinstance(value, list):
        return [_expand(v, keep_placeholders) for v in value]
    if isinstance(value, dict):
        return {k: _expand(v, keep_placeholders) for k, v in value.items()}
    return value


def load_servers(path: Path = CONFIG_PATH, include_disabled: bool = False) -> dict[str, dict]:
    data = yaml.safe_load(path.read_text()) or {}
    servers = data.get("servers") or {}
    return {
        name: cfg
        for name, cfg in servers.items()
        if include_disabled or cfg.get("enabled", True)
    }


def _to_entry(cfg: dict) -> dict:
    kind = cfg.get("type", "stdio")
    if kind == "stdio":
        entry = {"type": "stdio", "command": cfg["command"], "args": cfg.get("args", [])}
        if cfg.get("env"):
            entry["env"] = cfg["env"]
    elif kind in ("http", "sse"):
        entry = {"type": kind, "url": cfg["url"]}
        if cfg.get("headers"):
            entry["headers"] = cfg["headers"]
    else:
        raise ValueError(f"Unsupported MCP server type: {kind}")
    return entry


def claude_code_json(path: Path = CONFIG_PATH) -> dict:
    """.mcp.json content. ${VAR} placeholders are kept; Claude Code expands them itself."""
    servers = load_servers(path)
    return {"mcpServers": {n: _expand(_to_entry(c), True) for n, c in servers.items()}}


def agent_sdk_servers(path: Path = CONFIG_PATH) -> dict[str, dict]:
    """mcp_servers mapping for ClaudeAgentOptions, with env vars resolved now."""
    return {n: _expand(_to_entry(c), False) for n, c in load_servers(path).items()}
