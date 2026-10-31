from graphrag_cmp.ingestion.chunk import chunk_pages
from graphrag_cmp.neo4j_store import entity_id
from graphrag_cmp.prompts import cited_sources
from graphrag_cmp.retrieval.retrievers import format_chunks
from graphrag_cmp.variants import VARIANTS


def test_chunks_keep_page_and_ids():
    pages = [{"page": 1, "text": "# Intro\n" + "word " * 400},
             {"page": 2, "text": "## Table\n| a | b |\n|---|---|\n| 1 | 2 |"}]
    chunks = chunk_pages(pages, source="doc.pdf", chunk_size=500, chunk_overlap=50)
    assert len(chunks) >= 3
    assert chunks[0].metadata["id"] == "doc.pdf::0"
    assert chunks[-1].metadata["page"] == 2
    assert [c.metadata["chunk_index"] for c in chunks] == list(range(len(chunks)))


def test_format_chunks_includes_graph_extras():
    text = format_chunks([{"id": "d::0", "page": 1, "text": "hello",
                           "entities": ["Neo4j"], "facts": ["Neo4j STORES Vectors"]}])
    assert "[source: d::0 | page 1]" in text
    assert "Neo4j STORES Vectors" in text


def test_cited_sources_dedupes_in_order():
    answer = "A [source: d.pdf::2] B [source: d.pdf::0] C [source: d.pdf::2 | page 1]"
    assert cited_sources(answer) == ["d.pdf::2", "d.pdf::0"]


def test_entity_id_normalises():
    assert entity_id("  Neo4j   Aura ") == "neo4j aura"


def test_six_variants():
    assert len(VARIANTS) == 6
