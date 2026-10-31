"""Agentic RAG with the Claude Agent SDK.

Compare with anthropic_sdk/agentic_rag.py: there we wrote the tool loop by hand.
Here the SDK runs the loop; we only expose the tools as an in-process MCP server.
"""

import asyncio

from graphrag_cmp.agent_sdk.runner import run_agent
from graphrag_cmp.prompts import AGENTIC_SYSTEM


def answer(question: str) -> dict:
    return asyncio.run(run_agent(question, AGENTIC_SYSTEM, use_tools=True))
