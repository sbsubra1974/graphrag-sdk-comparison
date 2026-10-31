"""GraphRAG with the Anthropic SDK: vector entry points + graph expansion, one call."""

from graphrag_cmp.anthropic_sdk.client import client, text_of
from graphrag_cmp.prompts import SYSTEM, cited_sources, context_prompt
from graphrag_cmp.retrieval.retrievers import format_chunks, graph_search
from graphrag_cmp.settings import settings


def answer(question: str) -> dict:
    # Same as plain RAG, except the retriever walks the graph from each matching
    # chunk to add entities, related facts and the following chunk.
    chunks = graph_search(question, k=5)

    response = client().messages.create(
        model=settings.claude_model,
        max_tokens=1500,
        system=SYSTEM,
        messages=[{"role": "user", "content": context_prompt(question, format_chunks(chunks))}],
    )
    text = text_of(response)
    return {"answer": text, "sources": cited_sources(text), "tool_calls": 0}
