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
- `src/graphrag_cmp/ingestion/` parse, chunk, embed, write to Neo4j (shared by all variants)
- `src/graphrag_cmp/retrieval/` SDK-agnostic retrievers: vector search, graph traversal
- `src/graphrag_cmp/anthropic_sdk/` rag.py, agentic_rag.py, graphrag.py using `anthropic.Anthropic`
- `src/graphrag_cmp/agent_sdk/` same three, using `claude_agent_sdk` with in-process MCP tools
- `config/mcp_servers.yaml` the only place MCP servers are defined (see below)
- `.claude/skills/` project skills; `SKILLS.md` indexes them

## Rules
- Both SDK folders must call the same retrievers in `retrieval/`, so comparisons are fair.
- Keep each variant file self-contained and readable; this repo is for learning.
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
- `graphrag-cmp mcp-list` list configured MCP servers
