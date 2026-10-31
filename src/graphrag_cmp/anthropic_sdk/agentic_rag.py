"""Agentic RAG with the Anthropic SDK: Claude decides what to search, in a tool-use loop.

With the raw Messages API we write the agent loop ourselves:
call Claude -> run any tools it asked for -> send results back -> repeat.
"""

from graphrag_cmp.anthropic_sdk.client import client, text_of
from graphrag_cmp.prompts import AGENTIC_SYSTEM, cited_sources
from graphrag_cmp.retrieval.tools import TOOL_SCHEMAS, run_tool
from graphrag_cmp.settings import settings

MAX_TURNS = 6  # safety limit so a confused model can't loop forever


def answer(question: str) -> dict:
    messages = [{"role": "user", "content": question}]
    tool_calls = 0

    for _ in range(MAX_TURNS):
        response = client().messages.create(
            model=settings.claude_model,
            max_tokens=1500,
            system=AGENTIC_SYSTEM,
            tools=TOOL_SCHEMAS,
            messages=messages,
        )
        # Keep Claude's turn (including its tool_use blocks) in the history.
        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason != "tool_use":
            break  # Claude has written its final answer

        # Run every tool Claude asked for and return the results in one user turn.
        results = []
        for block in response.content:
            if block.type == "tool_use":
                tool_calls += 1
                results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": run_tool(block.name, block.input),
                })
        messages.append({"role": "user", "content": results})

    text = text_of(response)
    return {"answer": text, "sources": cited_sources(text), "tool_calls": tool_calls}
