# graphrag-sdk-comparison

RAG vs Agentic RAG vs GraphRAG over a multimodal PDF, each implemented with the
Anthropic Python SDK and the Claude Agent SDK. Neo4j is both the vector store and the graph.

## Quick start
```bash
cp .env.example .env        # fill in keys
docker compose up -d        # Neo4j
pip install -e ".[dev]"
pytest
```

See `CLAUDE.md` for layout and conventions, `SKILLS.md` for project skills,
and `config/mcp_servers.yaml` to add MCP servers.
