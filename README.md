# graphrag-sdk-comparison

Ask questions about a multimodal PDF in six ways and compare the answers:

| | Plain RAG | Agentic RAG | GraphRAG |
|---|---|---|---|
| **Anthropic Python SDK** | `anthropic_sdk/rag.py` | `anthropic_sdk/agentic_rag.py` | `anthropic_sdk/graphrag.py` |
| **Claude Agent SDK** | `agent_sdk/rag.py` | `agent_sdk/agentic_rag.py` | `agent_sdk/graphrag.py` |

- **Plain RAG**: our code runs a vector search, pastes the top chunks into the prompt, one Claude call.
- **Agentic RAG**: Claude gets `search_chunks` and `lookup_entity` tools and decides what to look up,
  over several turns. With the Anthropic SDK we write that loop ourselves; the Agent SDK runs it for us
  and the tools are exposed as an in-process MCP server.
- **GraphRAG**: vector search finds entry chunks, then Cypher walks the knowledge graph to add the
  entities they mention, related facts one hop away, and the next chunk. One Claude call.

## Pipeline

```
PDF ──LlamaParse (agent mode: text, tables, chart/image descriptions)──► markdown pages
    ──LangChain (markdown headers, then 1000-char chunks, 150 overlap)──► chunks
    ──OpenAI text-embedding-3-small──► vectors ──► Neo4j vector index on :Chunk(embedding)
    ──Claude (forced tool call)──► entities + relationships ──► Neo4j graph
```

Neo4j graph:
`(:Document)-[:HAS_CHUNK]->(:Chunk)-[:NEXT]->(:Chunk)`,
`(:Chunk)-[:MENTIONS]->(:Entity)-[:RELATED_TO {type}]->(:Entity)`

## Quick start

```bash
cp .env.example .env            # add ANTHROPIC_API_KEY, OPENAI_API_KEY, LLAMA_CLOUD_API_KEY
docker compose up -d            # Neo4j at http://localhost:7474 (neo4j / password123)
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest                          # unit tests + Neo4j tests (these wipe the database)

graphrag-cmp ingest data/your.pdf --reset
graphrag-cmp ask "What does the report say about X?" --variant anthropic_sdk.agentic_rag
graphrag-cmp compare "How is A related to B?"
```

The Claude Agent SDK ships with the Claude Code CLI it drives, so no separate install is needed.

## MCP servers

Define servers once in `config/mcp_servers.yaml`, then run `python scripts/sync_mcp.py`.
That writes `.mcp.json` for Claude Code, and the Agent SDK agentic variant loads every enabled
server at runtime alongside its own `kb` tools. `graphrag-cmp mcp-list` shows what's configured.

## Working on the repo with Claude Code

`CLAUDE.md` holds the conventions; `SKILLS.md` indexes the project skills in `.claude/skills/`
(`ingest-pdf`, `run-comparison`, `add-mcp-server`).
