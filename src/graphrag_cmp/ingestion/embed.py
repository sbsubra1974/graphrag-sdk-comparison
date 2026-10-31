"""Step 3 of ingestion (and query time): turn text into vectors with OpenAI."""

from openai import OpenAI

from graphrag_cmp.settings import settings

_client = None


def _openai() -> OpenAI:
    # Create the client lazily so importing this module needs no API key.
    global _client
    if _client is None:
        _client = OpenAI(api_key=settings.openai_api_key)
    return _client


def embed_texts(texts: list[str], batch_size: int = 100) -> list[list[float]]:
    """Embed many texts, sending them to OpenAI in batches."""
    vectors: list[list[float]] = []
    for start in range(0, len(texts), batch_size):
        batch = texts[start:start + batch_size]
        response = _openai().embeddings.create(
            model=settings.embedding_model,
            input=batch,
            dimensions=settings.embedding_dimensions,
        )
        vectors.extend(item.embedding for item in response.data)
    return vectors


def embed_query(text: str) -> list[float]:
    """Embed a single question. Must use the same model as the chunks."""
    return embed_texts([text])[0]
