"""Answer generation module using Gemini CLI.

This module provides functionality to generate answers by calling Gemini CLI
with MCP server integration (mcp-markdown-ragdocs for document retrieval).
"""

import json
import subprocess
from pathlib import Path
from typing import Any


class GeminiCLIError(Exception):
    """Exception raised when Gemini CLI execution fails."""

    pass


class AnswerGenerator:
    """Generates answers using Gemini CLI with MCP integration.

    In Phase 2, this module acts as a thin wrapper around Gemini CLI,
    which handles question interpretation, document retrieval (via
    mcp-markdown-ragdocs), and answer generation in one flow.
    """

    def __init__(
        self,
        gemini_cli_path: str | None = None,
        config_path: Path | None = None,
        verbose: bool = False,
    ) -> None:
        """Initialize the answer generator.

        Args:
            gemini_cli_path: Path to gemini CLI executable (if None, reads from config)
            config_path: Path to gemini CLI config file (optional)
            verbose: Enable verbose output for debugging
        """
        # Load configuration
        self.config = self._load_config()

        # Set gemini CLI path (prioritize parameter over config)
        self.gemini_cli_path = gemini_cli_path or self.config.get(
            "gemini_cli_path", "gemini"
        )
        self.config_path = config_path
        self.verbose = verbose
        self.timeout = self.config.get("timeout", 120)

    def _load_config(self) -> dict[str, Any]:
        """Load configuration from config/gemini_config.json.

        Returns:
            Configuration dictionary
        """
        config_file = Path(__file__).parent.parent.parent / "config" / "gemini_config.json"

        if not config_file.exists():
            if self.verbose:
                print(f"[DEBUG] Config file not found: {config_file}")
            return {}

        try:
            with open(config_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            if self.verbose:
                print(f"[DEBUG] Failed to load config: {e}")
            return {}

    def generate_answer(self, question: str) -> dict[str, Any]:
        """Generate an answer for the given question using Gemini CLI.

        This method calls Gemini CLI via subprocess, which automatically:
        1. Interprets the question
        2. Retrieves relevant documents via mcp-markdown-ragdocs
        3. Generates an answer with citations

        Args:
            question: User's question

        Returns:
            Dictionary containing:
                - answer: Generated answer text
                - sources: List of source documents (if available)
                - raw_output: Raw CLI output for debugging

        Raises:
            GeminiCLIError: If Gemini CLI execution fails
        """
        try:
            # Build command arguments
            cmd = [self.gemini_cli_path]

            # Add config file if specified
            if self.config_path:
                cmd.extend(["--config", str(self.config_path)])

            # Add the question as prompt
            cmd.append(question)

            if self.verbose:
                print(f"[DEBUG] Executing command: {' '.join(cmd)}")

            # Execute Gemini CLI
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                timeout=self.timeout,
            )

            # Parse the output
            output = result.stdout.strip()

            if self.verbose:
                print(f"[DEBUG] Raw output:\n{output}")

            # In Phase 2, we return the raw output as the answer
            # Phase 3 might include structured parsing of citations
            return {
                "answer": output,
                "sources": self._extract_sources(output),
                "raw_output": output,
            }

        except subprocess.TimeoutExpired as e:
            raise GeminiCLIError(
                f"Gemini CLI timed out after {self.timeout} seconds. Question might be too complex."
            ) from e
        except subprocess.CalledProcessError as e:
            error_msg = f"Gemini CLI failed with exit code {e.returncode}"
            if e.stderr:
                error_msg += f"\nError output: {e.stderr}"
            raise GeminiCLIError(error_msg) from e
        except FileNotFoundError as e:
            raise GeminiCLIError(
                f"Gemini CLI executable not found at '{self.gemini_cli_path}'. "
                "Please ensure it is installed and in PATH."
            ) from e

    def _extract_sources(self, output: str) -> list[str]:
        """Extract source citations from Gemini CLI output.

        This is a simple implementation for Phase 2. It looks for common
        citation patterns in the output.

        Args:
            output: Raw Gemini CLI output

        Returns:
            List of source file paths or citations found in the output
        """
        sources = []

        # Simple pattern matching for file paths
        # Example: "According to error-handling/auth-errors.md..."
        # This is a basic implementation; Phase 3 might use more sophisticated parsing
        lines = output.split("\n")
        for line in lines:
            if ".md" in line.lower():
                # Extract potential markdown file references
                # This is a heuristic approach for Phase 2
                parts = line.split()
                for part in parts:
                    if part.endswith(".md") or ".md:" in part:
                        sources.append(part.strip(",:;()[]"))

        return list(set(sources))  # Remove duplicates

    def validate_cli_available(self) -> bool:
        """Check if Gemini CLI is available and executable.

        Returns:
            True if CLI is available, False otherwise
        """
        try:
            result = subprocess.run(
                [self.gemini_cli_path, "--version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
