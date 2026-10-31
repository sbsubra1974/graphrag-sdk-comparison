"""Step 4 of ingestion: ask Claude for entities and relationships in each chunk.

We force Claude to call a "record_graph" tool, which is the simplest way to get
reliable JSON back from the Anthropic SDK.
"""

import anthropic

from graphrag_cmp.settings import settings

GRAPH_TOOL = {
    "name": "record_graph",
    "description": "Record the entities and relationships found in the text.",
    "input_schema": {
        "type": "object",
        "properties": {
            "entities": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "type": {"type": "string", "description": "e.g. Person, Product, Concept"},
                        "description": {"type": "string"},
                    },
                    "required": ["name", "type"],
                },
            },
            "relationships": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "source": {"type": "string"},
                        "target": {"type": "string"},
                        "type": {"type": "string", "description": "UPPER_SNAKE_CASE verb"},
                    },
                    "required": ["source", "target", "type"],
                },
            },
        },
        "required": ["entities", "relationships"],
    },
}


def extract_graph(text: str, client: anthropic.Anthropic | None = None) -> dict:
    """Return {"entities": [...], "relationships": [...]} for one chunk."""
    client = client or anthropic.Anthropic(api_key=settings.anthropic_api_key)
    response = client.messages.create(
        model=settings.claude_model,
        max_tokens=2000,
        tools=[GRAPH_TOOL],
        # Forcing this tool means the reply is always structured data.
        tool_choice={"type": "tool", "name": "record_graph"},
        messages=[{
            "role": "user",
            "content": "Extract the key entities and the relationships between them. "
                       "Only use relationships stated in the text.\n\n" + text,
        }],
    )
    for block in response.content:
        if block.type == "tool_use":
            return block.input
    return {"entities": [], "relationships": []}
