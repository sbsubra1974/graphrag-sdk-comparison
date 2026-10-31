"""Tool definitions shared by the agentic variants of both SDKs.

The Anthropic SDK uses TOOL_SCHEMAS directly; the Agent SDK wraps the same
functions as in-process MCP tools. run_tool() is the single implementation.
"""

import json

from graphrag_cmp.retrieval.retrievers import entity_neighbourhood, format_chunks, vector_search

TOOL_SCHEMAS = [
    {
        "name": "search_chunks",
        "description": "Semantic search over the ingested document. Returns the most "
                       "relevant passages with their source ids. Call it again with a "
                       "rephrased or narrower query if results are not good enough.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "What to search for"},
                "k": {"type": "integer", "description": "How many passages (1-10)", "default": 5},
            },
            "required": ["query"],
        },
    },
    {
        "name": "lookup_entity",
        "description": "Look up a named entity (person, product, concept...) in the "
                       "knowledge graph and return its description and relationships.",
        "input_schema": {
            "type": "object",
            "properties": {"name": {"type": "string"}},
            "required": ["name"],
        },
    },
]


def run_tool(name: str, args: dict) -> str:
    """Execute a tool call and return text for the model."""
    if name == "search_chunks":
        k = max(1, min(int(args.get("k", 5)), 10))
        return format_chunks(vector_search(args["query"], k=k))
    if name == "lookup_entity":
        return json.dumps(entity_neighbourhood(args["name"]), indent=2)
    return f"Unknown tool: {name}"
