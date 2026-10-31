---
name: ingest-pdf
description: Load a PDF into Neo4j for this repo (LlamaParse, LangChain chunking, OpenAI embeddings, graph extraction).
---

1. Check `docker compose ps` shows Neo4j running and `.env` has OpenAI, LlamaCloud and Anthropic keys.
2. Put the PDF under `data/` (git-ignored).
3. Run `graphrag-cmp ingest data/<file>.pdf`.
4. Verify in Neo4j: `MATCH (c:Chunk) RETURN count(c)` and `MATCH (e:Entity) RETURN count(e)`.
