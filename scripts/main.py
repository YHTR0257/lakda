#!/usr/bin/env python3
"""Entry point script for Knowledge Retrieval Assistant.

This script can be run directly from the scripts/ directory:
    python scripts/main.py ask "How do I handle errors?"

For installed package usage, use the `lakda` command instead:
    lakda ask "How do I handle errors?"
"""

import sys
from pathlib import Path

# Add src/ to Python path so lakda module can be imported
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from lakda.main import cli

if __name__ == "__main__":
    cli()
