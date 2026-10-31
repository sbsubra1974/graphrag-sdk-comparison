"""Prompts shared by all six variants, so only the SDK and retrieval style differ."""

import re

SYSTEM = (
    "You answer questions about a document using only the provided context or tool "
    "results. Cite sources inline like [source: file.pdf::3]. If the context does not "
    "contain the answer, say you don't know."
)

AGENTIC_SYSTEM = SYSTEM + (
    " Use the tools to gather evidence before answering. Search more than once when the "
    "question has several parts, and use lookup_entity for questions about how things relate."
)


def context_prompt(question: str, context: str) -> str:
    """User message for the non-agentic variants: retrieved context, then the question."""
    return f"<context>\n{context}\n</context>\n\nQuestion: {question}"


def cited_sources(answer: str) -> list[str]:
    """Pull the [source: ...] ids out of an answer, in order, without duplicates."""
    ids = re.findall(r"source:\s*([^\]|,\s]+)", answer)
    return list(dict.fromkeys(ids))
