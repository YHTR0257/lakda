"""Main CLI entry point for Knowledge Retrieval Assistant.

This module provides the command-line interface for the KRA system.
"""

import click
from rich.console import Console

console = Console()


@click.group()
@click.version_option(version="0.1.0", prog_name="kra")
def cli() -> None:
    """Knowledge Retrieval Assistant - Domain-agnostic RAG system."""
    pass


@cli.command()
@click.argument("question", type=str, required=False)
@click.option(
    "--file",
    "-f",
    type=click.Path(exists=True),
    help="Read question from a file instead of command line argument",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Enable verbose output with detailed retrieval information",
)
def ask(question: str | None, file: str | None, verbose: bool) -> None:
    """Ask a question and get an answer with citations.

    You can provide the question either as a command line argument or from a file.

    Examples:
        kra ask "How do I handle authentication errors?"
        kra ask "What is the system architecture?" -v
        kra ask --file /tmp/question.txt
        kra ask -f /tmp/question.txt -v
    """
    # Read question from file or command line
    if file:
        with open(file, "r", encoding="utf-8") as f:
            question_text = f.read().strip()
        console.print(f"[dim]Reading question from: {file}[/dim]")
    elif question:
        question_text = question
    else:
        console.print("[red]Error: Please provide a question either as argument or via --file[/red]")
        return

    console.print(f"[bold cyan]Question:[/bold cyan] {question_text}")
    if verbose:
        console.print("[dim]Verbose mode enabled[/dim]")

    # Phase 2: Call Gemini CLI with mcp-markdown-ragdocs integration
    # mcp-markdown-ragdocs searches all domains in data/documents/ based on config.toml
    console.print("\n[yellow]⚠ Not yet implemented - Phase 2 development in progress[/yellow]")


@cli.command()
@click.argument("file_path", type=click.Path(exists=True))
@click.option(
    "--target",
    "-t",
    type=str,
    required=True,
    help="Target directory under data/documents/ (e.g., error-handling, api-guides)",
)
def upload(file_path: str, target: str) -> None:
    """Upload and process a document (PDF, Word, etc.) to a specified directory.

    The document will be:
    1. Converted to Markdown using markdownify-mcp
    2. Processed with LLM-generated metadata/Frontmatter
    3. Placed in data/documents/{target}/

    Examples:
        kra upload docs/api-guide.pdf --target api-guides
        kra upload manual.docx -t error-handling
    """
    console.print(f"[bold cyan]Uploading:[/bold cyan] {file_path}")
    console.print(f"[dim]Target: data/documents/{target}/[/dim]")

    # Phase 2:
    # 1. Copy to data/uploads/
    # 2. Call markdownify-mcp for document conversion
    # 3. Generate metadata/Frontmatter via LLM
    # 4. Move to data/documents/{target}/
    console.print("\n[yellow]⚠ Not yet implemented - Phase 2 development in progress[/yellow]")


@cli.command()
def list_domains() -> None:
    """List available domains in the knowledge base."""
    console.print("[bold cyan]Available Domains:[/bold cyan]")

    # Phase 2: Read from data/documents/ directory structure
    console.print("\n[yellow]⚠ Not yet implemented - Phase 2 development in progress[/yellow]")


@cli.command()
@click.option(
    "--format",
    "-f",
    type=click.Choice(["json", "csv", "text"]),
    default="text",
    help="Output format for feedback logs",
)
def feedback(format: str) -> None:
    """View feedback logs for generated answers.

    Examples:
        kra feedback
        kra feedback --format json
    """
    console.print(f"[bold cyan]Feedback Logs[/bold cyan] (format: {format})")

    # Phase 2: Read from data/feedback/ directory
    console.print("\n[yellow]⚠ Not yet implemented - Phase 2 development in progress[/yellow]")


if __name__ == "__main__":
    cli()
