# graphrag-sdk-comparison

Sample code comparing three retrieval styles (RAG, Agentic RAG, GraphRAG) built twice:
once with the **Anthropic Python SDK** and once with the **Claude Agent SDK**.

## Stack (fixed, do not swap without asking)
- Parsing: LlamaParse (multimodal PDF: text, tables, image descriptions)
- Chunking: LangChain text splitters
- Embeddings: OpenAI (`OPENAI_EMBEDDING_MODEL`, default `text-embedding-3-small`)
- Vector store and graph store: Neo4j (one database, vector index on `Chunk.embedding`)
- LLM: Claude (`CLAUDE_MODEL`)

## Layout
- `src/graphrag_cmp/ingestion/` parse.py, chunk.py, embed.py, extract_graph.py, pipeline.py
- `src/graphrag_cmp/neo4j_store.py` all Cypher for writing chunks, vectors and the graph
- `src/graphrag_cmp/retrieval/` SDK-agnostic retrievers: vector search, graph traversal
- `src/graphrag_cmp/anthropic_sdk/` rag.py, agentic_rag.py, graphrag.py using `anthropic.Anthropic`
- `src/graphrag_cmp/agent_sdk/` same three, using `claude_agent_sdk` with in-process MCP tools
- `src/graphrag_cmp/retrieval/tools.py` tool schemas + run_tool(), shared by both agentic variants
- `src/graphrag_cmp/prompts.py` system prompts shared by all six variants
- `src/graphrag_cmp/variants.py` registry of the six `<sdk>.<style>` variants used by the CLI
- `config/mcp_servers.yaml` the only place MCP servers are defined (see below)
- `.claude/skills/` project skills; `SKILLS.md` indexes them

## Rules
- Both SDK folders must call the same retrievers in `retrieval/`, so comparisons are fair.
- Keep code simple with inline comments; each variant file should read on its own. This repo is for learning.
- Secrets come from `.env` only. Never commit `.env` or API keys.
- Run `pytest` and `ruff check .` before every commit.
- Commit per step with a clear message (`ingestion: ...`, `agent_sdk: ...`, `mcp: ...`).

## MCP servers
Add or change servers only in `config/mcp_servers.yaml`, then run `python scripts/sync_mcp.py`
to regenerate `.mcp.json`. The Agent SDK variants load the YAML at runtime via
`graphrag_cmp.mcp_config.agent_sdk_servers()`. Use the `add-mcp-server` skill.

## Commands
- `docker compose up -d` start Neo4j (browser at http://localhost:7474)
- `pip install -e ".[dev]"` install
- `graphrag-cmp ingest data/file.pdf [--reset] [--no-graph]` load a PDF
- `graphrag-cmp ask "question" --variant agent_sdk.graphrag` one variant
- `graphrag-cmp compare "question"` all six side by side
- `graphrag-cmp mcp-list` list configured MCP servers
- `pytest` unit tests; Neo4j integration tests run when Neo4j is up (they wipe the DB)
