"""Step 1 of ingestion: turn a (multimodal) PDF into markdown text, one entry per page."""

from llama_parse import LlamaParse

from graphrag_cmp.settings import settings


def parse_pdf(pdf_path: str) -> list[dict]:
    """Parse a PDF with LlamaParse and return [{"page": 1, "text": "..."}, ...]."""
    parser = LlamaParse(
        api_key=settings.llama_cloud_api_key,
        # Markdown keeps headings and tables, which helps the chunker later.
        result_type="markdown",
        # Agent mode reads each page as an image too, so charts, diagrams and
        # photos come back as text descriptions instead of being dropped.
        parse_mode="parse_page_with_agent",
        extract_charts=True,
    )

    # load_data returns one llama_index Document per page by default.
    documents = parser.load_data(pdf_path)

    pages = []
    for page_number, doc in enumerate(documents, start=1):
        text = doc.text.strip()
        if text:  # skip blank pages
            pages.append({"page": page_number, "text": text})
    return pages
