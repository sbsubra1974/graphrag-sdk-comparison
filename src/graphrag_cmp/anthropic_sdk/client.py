"""Shared Anthropic client for the three Anthropic SDK variants."""

import anthropic

from graphrag_cmp.settings import settings

_client = None


def client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    return _client


def text_of(response) -> str:
    """Join the text blocks of a Messages API response."""
    return "".join(block.text for block in response.content if block.type == "text")
