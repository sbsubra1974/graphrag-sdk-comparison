"""Command-line entry point: ingest a PDF, ask one variant, or compare all six."""

import time

import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.table import Table

from graphrag_cmp.mcp_config import load_servers
from graphrag_cmp.variants import VARIANTS, get_answer_fn

app = typer.Typer(help="Compare RAG, Agentic RAG and GraphRAG across two Claude SDKs.")
console = Console()


@app.callback()
def main() -> None:
    """Keep subcommands as subcommands."""


@app.command()
def ingest(pdf_path: str, no_graph: bool = typer.Option(False, help="Skip entity extraction"),
           reset: bool = typer.Option(False, help="Wipe Neo4j first")) -> None:
    """Parse, chunk, embed and store a PDF in Neo4j."""
    from graphrag_cmp import neo4j_store
    from graphrag_cmp.ingestion.pipeline import ingest as run_ingest

    if reset:
        neo4j_store.reset()
    stats = run_ingest(pdf_path, build_graph=not no_graph)
    console.print(f"Ingested [bold]{stats['source']}[/]: {stats['pages']} pages, "
                  f"{stats['chunks']} chunks")


def _run(variant: str, question: str) -> dict:
    """Run one variant and time it. Errors are captured so a comparison keeps going."""
    start = time.perf_counter()
    try:
        result = get_answer_fn(variant)(question)
    except Exception as exc:  # noqa: BLE001 - show any failure in the table
        result = {"answer": f"ERROR: {exc}", "sources": [], "tool_calls": 0}
    result["seconds"] = round(time.perf_counter() - start, 1)
    return result


@app.command()
def ask(question: str, variant: str = typer.Option("anthropic_sdk.rag", help=", ".join(VARIANTS))):
    """Answer one question with one variant."""
    result = _run(variant, question)
    console.print(Markdown(result["answer"]))
    console.print(f"\n[dim]{variant} | {result['seconds']}s | tool calls: "
                  f"{result['tool_calls']} | sources: {', '.join(result['sources'])}[/]")


@app.command()
def compare(question: str,
            only: list[str] = typer.Option(None, help="Limit to these variants (repeatable)")):
    """Run the same question through every variant and show them side by side."""
    table = Table("variant", "seconds", "tools", "sources", "answer", show_lines=True)
    for variant in only or VARIANTS:
        console.print(f"[dim]running {variant}...[/]")
        r = _run(variant, question)
        table.add_row(variant, str(r["seconds"]), str(r["tool_calls"]),
                      "\n".join(r["sources"]), r["answer"][:600])
    console.print(table)


@app.command("mcp-list")
def mcp_list() -> None:
    """Show MCP servers defined in config/mcp_servers.yaml."""
    table = Table("name", "type", "enabled", "target")
    for name, cfg in load_servers(include_disabled=True).items():
        target = cfg.get("url") or " ".join([cfg.get("command", "")] + cfg.get("args", []))
        table.add_row(name, cfg.get("type", "stdio"), str(cfg.get("enabled", True)), target)
    console.print(table)


if __name__ == "__main__":
    app()
