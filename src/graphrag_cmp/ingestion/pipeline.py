"""Run the whole ingestion: parse -> chunk -> embed -> store -> extract graph."""

from pathlib import Path

from rich.progress import track

from graphrag_cmp import neo4j_store
from graphrag_cmp.ingestion.chunk import chunk_pages
from graphrag_cmp.ingestion.embed import embed_texts
from graphrag_cmp.ingestion.extract_graph import extract_graph
from graphrag_cmp.ingestion.parse import parse_pdf


def ingest(pdf_path: str, build_graph: bool = True) -> dict:
    source = Path(pdf_path).name

    # 1. Parse the PDF (text, tables, image descriptions) into markdown pages.
    pages = parse_pdf(pdf_path)

    # 2. Chunk the pages with LangChain.
    chunks = chunk_pages(pages, source=source)

    # 3. Embed every chunk with OpenAI.
    vectors = embed_texts([c.page_content for c in chunks])

    # 4. Store chunks + vectors in Neo4j.
    neo4j_store.create_schema()
    rows = [
        {"id": c.metadata["id"], "text": c.page_content, "page": c.metadata["page"],
         "chunk_index": c.metadata["chunk_index"], "embedding": v}
        for c, v in zip(chunks, vectors)
    ]
    neo4j_store.save_chunks(source, rows)

    # 5. Build the knowledge graph (one Claude call per chunk; skip for plain RAG).
    if build_graph:
        for c in track(chunks, description="Extracting graph"):
            neo4j_store.save_graph(c.metadata["id"], extract_graph(c.page_content))

    return {"source": source, "pages": len(pages), "chunks": len(chunks)}
