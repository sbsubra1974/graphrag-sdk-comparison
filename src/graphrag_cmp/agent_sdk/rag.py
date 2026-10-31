"""Plain RAG with the Claude Agent SDK: we retrieve, the agent just answers (no tools)."""

import asyncio

from graphrag_cmp.agent_sdk.runner import run_agent
from graphrag_cmp.prompts import SYSTEM, context_prompt
from graphrag_cmp.retrieval.retrievers import format_chunks, vector_search


def answer(question: str) -> dict:
    # Same retrieval as anthropic_sdk/rag.py; only the way we call Claude differs.
    chunks = vector_search(question, k=5)
    prompt = context_prompt(question, format_chunks(chunks))
    return asyncio.run(run_agent(prompt, SYSTEM, use_tools=False))
