"""Shared helper that runs one Claude Agent SDK query and collects the result.

The Agent SDK runs the agent loop for us (inside the bundled Claude Code CLI),
so each variant only chooses a prompt, a system prompt and which tools to expose.
"""

import asyncio

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ResultMessage,
    TextBlock,
    ToolUseBlock,
    create_sdk_mcp_server,
    query,
    tool,
)

from graphrag_cmp.mcp_config import agent_sdk_servers
from graphrag_cmp.prompts import cited_sources
from graphrag_cmp.retrieval.tools import TOOL_SCHEMAS, run_tool
from graphrag_cmp.settings import settings


def _wrap(schema: dict):
    """Turn one shared tool schema into an in-process MCP tool."""

    @tool(schema["name"], schema["description"], schema["input_schema"])
    async def _handler(args: dict) -> dict:
        # run_tool talks to Neo4j synchronously, so run it off the event loop.
        text = await asyncio.to_thread(run_tool, schema["name"], args)
        return {"content": [{"type": "text", "text": text}]}

    return _handler


# One in-process MCP server ("kb") exposing the same tools the Anthropic SDK uses.
KB_SERVER = create_sdk_mcp_server(name="kb", tools=[_wrap(s) for s in TOOL_SCHEMAS])
KB_TOOL_NAMES = [f"mcp__kb__{s['name']}" for s in TOOL_SCHEMAS]


async def run_agent(prompt: str, system: str, use_tools: bool, max_turns: int = 8) -> dict:
    if use_tools:
        # Our kb tools plus any servers enabled in config/mcp_servers.yaml.
        extra = agent_sdk_servers()
        mcp_servers = {"kb": KB_SERVER, **extra}
        # "mcp__<server>" allows every tool on that server.
        allowed = KB_TOOL_NAMES + [f"mcp__{name}" for name in extra]
    else:
        mcp_servers, allowed = {}, []

    options = ClaudeAgentOptions(
        model=settings.claude_model,
        system_prompt=system,
        mcp_servers=mcp_servers,
        allowed_tools=allowed,
        tools=[],              # turn off Claude Code's built-ins (Bash, Read, ...)
        max_turns=max_turns if use_tools else 1,
    )

    text_parts, tool_calls, final = [], 0, None
    async for message in query(prompt=prompt, options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    text_parts.append(block.text)
                elif isinstance(block, ToolUseBlock):
                    tool_calls += 1
        elif isinstance(message, ResultMessage):
            final = message.result  # the agent's final answer text

    text = final or "".join(text_parts)
    return {"answer": text, "sources": cited_sources(text), "tool_calls": tool_calls}
