---
name: run-comparison
description: Ask one question through all six variants (RAG, Agentic RAG, GraphRAG x Anthropic SDK, Agent SDK) and compare.
---

1. Make sure a document has been ingested (see the ingest-pdf skill).
2. Run `graphrag-cmp compare "<question>"`; add `--only agent_sdk.graphrag` to run one variant.
3. Summarise differences in answer quality, sources cited, tool calls and latency.
