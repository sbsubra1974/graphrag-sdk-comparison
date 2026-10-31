"""Plain RAG with the Anthropic SDK: retrieve once, then one Messages API call."""

from graphrag_cmp.anthropic_sdk.client import client, text_of
from graphrag_cmp.prompts import SYSTEM, cited_sources, context_prompt
from graphrag_cmp.retrieval.retrievers import format_chunks, vector_search
from graphrag_cmp.settings import settings


def answer(question: str) -> dict:
    # 1. Retrieve: our code decides what context Claude sees.
    chunks = vector_search(question, k=5)

    # 2. Generate: a single call with the context pasted into the prompt.
    response = client().messages.create(
        model=settings.claude_model,
        max_tokens=1500,
        system=SYSTEM,
        messages=[{"role": "user", "content": context_prompt(question, format_chunks(chunks))}],
    )
    text = text_of(response)
    return {"answer": text, "sources": cited_sources(text), "tool_calls": 0}
