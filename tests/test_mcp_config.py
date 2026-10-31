from pathlib import Path

from graphrag_cmp.mcp_config import agent_sdk_servers, claude_code_json, load_servers

YAML = """
servers:
  local:
    type: stdio
    command: uvx
    args: ["thing"]
    env: {TOKEN: "${TEST_TOKEN}"}
  remote:
    type: http
    url: https://example.com/mcp
  off:
    enabled: false
    type: stdio
    command: nope
"""


def _write(tmp_path: Path) -> Path:
    p = tmp_path / "mcp.yaml"
    p.write_text(YAML)
    return p


def test_disabled_servers_are_skipped(tmp_path):
    assert set(load_servers(_write(tmp_path))) == {"local", "remote"}


def test_claude_code_json_keeps_placeholders(tmp_path):
    out = claude_code_json(_write(tmp_path))
    assert out["mcpServers"]["local"]["env"]["TOKEN"] == "${TEST_TOKEN}"
    assert out["mcpServers"]["remote"] == {"type": "http", "url": "https://example.com/mcp"}


def test_agent_sdk_servers_expand_env(tmp_path, monkeypatch):
    monkeypatch.setenv("TEST_TOKEN", "abc")
    assert agent_sdk_servers(_write(tmp_path))["local"]["env"]["TOKEN"] == "abc"
