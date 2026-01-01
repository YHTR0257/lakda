"""
Document Processing Module

Converts uploaded documents (PDF, Word, Excel, PowerPoint, etc.) to Markdown format
using the markitdown library.
"""

import logging
from enum import Enum
from pathlib import Path
from typing import List, Optional

from markitdown import MarkItDown
from pydantic import BaseModel, Field


# Logging configuration
logger = logging.getLogger(__name__)


class SupportedFormat(str, Enum):
    """Supported document formats for conversion."""

    PDF = ".pdf"
    DOCX = ".docx"
    XLSX = ".xlsx"
    PPTX = ".pptx"
    HTML = ".html"
    TXT = ".txt"
    CSV = ".csv"
    JSON = ".json"
    XML = ".xml"


class ConversionResult(BaseModel):
    """Document conversion result model."""

    success: bool = Field(..., description="Conversion success flag")
    source_path: Path = Field(..., description="Source file path")
    output_path: Optional[Path] = Field(None, description="Output file path")
    error_message: Optional[str] = Field(None, description="Error message if conversion failed")
    markdown_content: Optional[str] = Field(None, description="Converted Markdown content")


class DocumentProcessor:
    """Document conversion processor class."""

    def __init__(
        self,
        uploads_dir: Path = Path("data/uploads"),
        documents_dir: Path = Path("data/documents"),
        default_domain: str = "general"
    ):
        """
        Initialize the DocumentProcessor.

        Args:
            uploads_dir: Upload source directory
            documents_dir: Converted document destination directory
            default_domain: Default domain name for saving documents
        """
        self.uploads_dir = uploads_dir
        self.documents_dir = documents_dir
        self.default_domain = default_domain
        self.converter = MarkItDown()
        self.logger = logging.getLogger(__name__)

        # Ensure directories exist
        self.uploads_dir.mkdir(parents=True, exist_ok=True)
        self.documents_dir.mkdir(parents=True, exist_ok=True)

    def convert_file(
        self,
        file_path: Path,
        domain: Optional[str] = None,
        output_filename: Optional[str] = None
    ) -> ConversionResult:
        """
        Convert a single file to Markdown format.

        Args:
            file_path: File path to convert
            domain: Target domain name (uses default_domain if None)
            output_filename: Custom output filename (without extension)

        Returns:
            ConversionResult: Conversion result
        """
        # 1. Check file existence
        if not file_path.exists():
            error_msg = f"File not found: {file_path}"
            self.logger.error(error_msg)
            return ConversionResult(
                success=False,
                source_path=file_path,
                error_message=error_msg
            )

        # 2. Check format support
        if not self._is_supported_format(file_path):
            error_msg = f"Unsupported format: {file_path.suffix}"
            self.logger.error(error_msg)
            return ConversionResult(
                success=False,
                source_path=file_path,
                error_message=error_msg
            )

        try:
            # 3. Convert using markitdown
            result = self.converter.convert(str(file_path))
            markdown_content = result.text_content

            # 4. Generate output path
            target_domain = domain or self.default_domain
            domain_dir = self.documents_dir / target_domain
            domain_dir.mkdir(parents=True, exist_ok=True)

            filename = self._generate_filename(file_path, output_filename)
            output_path = domain_dir / filename

            # 5. Save Markdown
            self._save_markdown(markdown_content, output_path)

            self.logger.info(f"Successfully converted: {file_path} → {output_path}")

            return ConversionResult(
                success=True,
                source_path=file_path,
                output_path=output_path,
                markdown_content=markdown_content
            )

        except Exception as e:
            error_msg = str(e)
            self.logger.error(f"Conversion failed: {file_path}, Error: {error_msg}")
            return ConversionResult(
                success=False,
                source_path=file_path,
                error_message=error_msg
            )

    def convert_directory(
        self,
        source_dir: Optional[Path] = None,
        domain: Optional[str] = None
    ) -> List[ConversionResult]:
        """
        Convert all files in a directory to Markdown format.

        Args:
            source_dir: Source directory to convert (uses uploads_dir if None)
            domain: Target domain name (uses default_domain if None)

        Returns:
            List[ConversionResult]: List of conversion results
        """
        source = source_dir or self.uploads_dir

        if not source.exists():
            self.logger.error(f"Source directory not found: {source}")
            return []

        results = []

        # Process only files with supported extensions
        supported_extensions = [fmt.value for fmt in SupportedFormat]

        for file_path in source.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
                result = self.convert_file(file_path, domain=domain)
                results.append(result)

        # Summary log
        success_count = sum(1 for r in results if r.success)
        total_count = len(results)
        self.logger.info(
            f"Batch conversion completed: {success_count}/{total_count} files succeeded"
        )

        return results

    def _save_markdown(self, content: str, output_path: Path) -> None:
        """
        Save Markdown content to a file.

        Args:
            content: Markdown content
            output_path: Output file path
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)

    def _generate_filename(
        self,
        original_path: Path,
        custom_name: Optional[str] = None
    ) -> str:
        """
        Generate output filename.

        Args:
            original_path: Original file path
            custom_name: Custom filename (without extension)

        Returns:
            str: Output filename with .md extension
        """
        if custom_name:
            base_name = custom_name
        else:
            base_name = original_path.stem

        return f"{base_name}.md"

    def _is_supported_format(self, file_path: Path) -> bool:
        """
        Check if the file format is supported.

        Args:
            file_path: File path to check

        Returns:
            bool: True if supported, False otherwise
        """
        return file_path.suffix.lower() in [fmt.value for fmt in SupportedFormat]
