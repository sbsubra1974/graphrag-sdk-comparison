"""Exercises the Cypher in neo4j_store and retrievers against a real Neo4j.

Uses random vectors instead of OpenAI, so no API keys are needed.
Skipped automatically when Neo4j isn't running (start it with `docker compose up -d`).
WARNING: wipes the database.
"""

import random

import pytest

from graphrag_cmp import neo4j_store
from graphrag_cmp.retrieval import retrievers, tools


def _neo4j_up() -> bool:
    try:
        neo4j_store.driver().verify_connectivity()
        return True
    except Exception:  # noqa: BLE001
        return False


pytestmark = pytest.mark.skipif(not _neo4j_up(), reason="Neo4j not running")


def _vec() -> list[float]:
    return [random.random() for _ in range(1536)]


@pytest.fixture(autouse=True)
def seeded(monkeypatch):
    monkeypatch.setattr(retrievers, "embed_query", lambda q: _vec())
    neo4j_store.reset()
    neo4j_store.create_schema()
    neo4j_store.run("CALL db.awaitIndexes(60)")
    rows = [{"id": f"d.pdf::{i}", "text": f"chunk {i}", "page": 1, "chunk_index": i,
             "embedding": _vec()} for i in range(4)]
    neo4j_store.save_chunks("d.pdf", rows)
    neo4j_store.save_graph("d.pdf::0", {
        "entities": [{"name": "Neo4j", "type": "Product"}, {"name": "Cypher", "type": "Language"}],
        "relationships": [{"source": "Neo4j", "target": "Cypher", "type": "uses query language"}],
    })


def test_graph_shape():
    counts = {r["t"]: r["n"] for r in neo4j_store.run(
        "MATCH ()-[r]->() RETURN type(r) AS t, count(*) AS n")}
    assert counts == {"HAS_CHUNK": 4, "NEXT": 3, "MENTIONS": 2, "RELATED_TO": 1}


def test_graph_search_adds_facts():
    hits = {h["id"]: h for h in retrievers.graph_search("anything", k=4)}
    assert hits["d.pdf::0"]["facts"] == ["Neo4j USES_QUERY_LANGUAGE Cypher"]
    assert hits["d.pdf::0"]["next_text"] == ["chunk 1"]


def test_tools():
    assert "USES_QUERY_LANGUAGE" in tools.run_tool("lookup_entity", {"name": "cypher"})
    assert tools.run_tool("search_chunks", {"query": "q", "k": 2}).count("[source:") == 2
