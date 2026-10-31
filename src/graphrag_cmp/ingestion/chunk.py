"""Step 2 of ingestion: split page text into overlapping chunks with LangChain."""

from langchain_core.documents import Document
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter

# Split on markdown headings first, so a chunk rarely mixes two sections.
HEADERS = [("#", "h1"), ("##", "h2"), ("###", "h3")]


def chunk_pages(pages: list[dict], source: str, chunk_size: int = 1000,
                chunk_overlap: int = 150) -> list[Document]:
    """Return LangChain Documents with metadata: source, page, chunk_index, id."""
    header_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=HEADERS, strip_headers=False)
    # Then cap each section's size; overlap keeps sentences that span a cut.
    size_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)

    chunks: list[Document] = []
    for page in pages:
        sections = header_splitter.split_text(page["text"])
        for piece in size_splitter.split_documents(sections):
            piece.metadata.update({"source": source, "page": page["page"]})
            chunks.append(piece)

    # Give every chunk a stable id, e.g. "manual.pdf::12".
    for i, chunk in enumerate(chunks):
        chunk.metadata["chunk_index"] = i
        chunk.metadata["id"] = f"{source}::{i}"
    return chunks
