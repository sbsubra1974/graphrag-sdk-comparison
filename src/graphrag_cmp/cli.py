"""Command-line entry point. Ingest and ask commands are added in later steps."""

import typer
from rich.console import Console
from rich.table import Table

from graphrag_cmp.mcp_config import load_servers

app = typer.Typer(help="Compare RAG, Agentic RAG and GraphRAG across two Claude SDKs.")
console = Console()


@app.callback()
def main() -> None:
    """Keep subcommands as subcommands even while only one exists."""


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
