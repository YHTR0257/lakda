#!/usr/bin/env python3
"""
Document Conversion CLI Script

Usage:
    # Single file conversion
    python scripts/convert_documents.py data/uploads/document.pdf -d error-handling

    # Custom filename specification
    python scripts/convert_documents.py data/uploads/document.pdf -d architecture -o custom_name

    # Batch directory conversion
    python scripts/convert_documents.py data/uploads/ -d api-guides -v
"""

import logging
import sys
from pathlib import Path

import click

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from data.processor import DocumentProcessor


@click.command()
@click.argument(
    "input_path",
    type=click.Path(exists=True, path_type=Path),
)
@click.option(
    "-d", "--domain",
    type=str,
    default="general",
    show_default=True,
    help="Target domain directory"
)
@click.option(
    "-o", "--output",
    type=str,
    help="Custom output filename (without extension)"
)
@click.option(
    "-v", "--verbose",
    is_flag=True,
    help="Enable verbose output"
)
def main(input_path: Path, domain: str, output: str, verbose: bool):
    """
    Convert documents to Markdown format.

    INPUT_PATH: Input file or directory path to convert

    \b
    Examples:
      # Single file conversion
      python scripts/convert_documents.py data/uploads/document.pdf -d error-handling

      # Custom filename specification
      python scripts/convert_documents.py data/uploads/document.pdf -d architecture -o custom_name

      # Batch directory conversion with verbose output
      python scripts/convert_documents.py data/uploads/ -d api-guides -v
    """
    # Configure logging
    if verbose:
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

    # Create DocumentProcessor instance
    processor = DocumentProcessor()

    # Determine if input is file or directory
    if input_path.is_file():
        # Single file conversion
        result = processor.convert_file(
            input_path,
            domain=domain,
            output_filename=output
        )

        if result.success:
            click.secho("✓ Conversion succeeded", fg="green")
            click.echo(f"  Source: {result.source_path}")
            click.echo(f"  Output: {result.output_path}")
        else:
            click.secho("✗ Conversion failed", fg="red")
            click.echo(f"  Source: {result.source_path}")
            click.echo(f"  Error: {result.error_message}")
            sys.exit(1)

    elif input_path.is_dir():
        # Batch directory conversion
        results = processor.convert_directory(input_path, domain=domain)

        success_count = sum(1 for r in results if r.success)
        total_count = len(results)

        click.echo("\nBatch Conversion Results:")
        click.echo(f"  Total: {total_count} files")
        click.secho(f"  Success: {success_count} files", fg="green")
        if success_count < total_count:
            click.secho(f"  Failed: {total_count - success_count} files", fg="red")

        # Verbose output
        if verbose:
            click.echo("\nDetails:")
            for result in results:
                if result.success:
                    click.secho(f"  ✓ {result.source_path.name}", fg="green")
                else:
                    click.secho(f"  ✗ {result.source_path.name}", fg="red")
                    click.echo(f"    Error: {result.error_message}")

        if success_count < total_count:
            sys.exit(1)

    else:
        click.secho(f"Error: {input_path} is neither a file nor a directory", fg="red")
        sys.exit(1)


if __name__ == "__main__":
    main()
