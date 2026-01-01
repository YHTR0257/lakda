"""
Unit tests for DocumentProcessor class.
"""

import pytest
from pathlib import Path

from data.processor import DocumentProcessor, SupportedFormat, ConversionResult


@pytest.fixture
def temp_processor(tmp_path):
    """Create a temporary DocumentProcessor instance for testing."""
    uploads_dir = tmp_path / "uploads"
    documents_dir = tmp_path / "documents"
    return DocumentProcessor(
        uploads_dir=uploads_dir,
        documents_dir=documents_dir,
        default_domain="test-domain"
    )


def test_supported_format_check(temp_processor):
    """Test format support checking."""
    assert temp_processor._is_supported_format(Path("test.pdf")) is True
    assert temp_processor._is_supported_format(Path("test.docx")) is True
    assert temp_processor._is_supported_format(Path("test.xlsx")) is True
    assert temp_processor._is_supported_format(Path("test.pptx")) is True
    assert temp_processor._is_supported_format(Path("test.html")) is True
    assert temp_processor._is_supported_format(Path("test.txt")) is True
    assert temp_processor._is_supported_format(Path("test.csv")) is True
    assert temp_processor._is_supported_format(Path("test.json")) is True
    assert temp_processor._is_supported_format(Path("test.xml")) is True
    assert temp_processor._is_supported_format(Path("test.xyz")) is False
    assert temp_processor._is_supported_format(Path("test.exe")) is False


def test_generate_filename(temp_processor):
    """Test filename generation."""
    assert temp_processor._generate_filename(Path("test.pdf")) == "test.md"
    assert temp_processor._generate_filename(Path("document.docx")) == "document.md"
    assert temp_processor._generate_filename(Path("test.pdf"), "custom") == "custom.md"
    assert temp_processor._generate_filename(Path("test.pdf"), "my_file") == "my_file.md"


def test_convert_file_not_found(temp_processor):
    """Test conversion of non-existent file."""
    result = temp_processor.convert_file(Path("nonexistent.pdf"))

    assert result.success is False
    assert result.source_path == Path("nonexistent.pdf")
    assert "not found" in result.error_message.lower()
    assert result.output_path is None
    assert result.markdown_content is None


def test_convert_file_unsupported_format(temp_processor, tmp_path):
    """Test conversion of unsupported file format."""
    # Create a file with unsupported extension
    test_file = tmp_path / "test.xyz"
    test_file.write_text("Test content")

    result = temp_processor.convert_file(test_file)

    assert result.success is False
    assert result.source_path == test_file
    assert "unsupported format" in result.error_message.lower()
    assert result.output_path is None


def test_convert_file_success(temp_processor, tmp_path):
    """Test successful file conversion."""
    # Create a text file
    test_file = tmp_path / "uploads" / "test.txt"
    test_file.parent.mkdir(parents=True, exist_ok=True)
    test_file.write_text("Test content for conversion")

    result = temp_processor.convert_file(test_file, domain="test-domain")

    assert result.success is True
    assert result.source_path == test_file
    assert result.output_path is not None
    assert result.output_path.exists()
    assert result.markdown_content is not None
    assert "Test content" in result.markdown_content


def test_convert_file_with_custom_filename(temp_processor, tmp_path):
    """Test file conversion with custom output filename."""
    test_file = tmp_path / "uploads" / "test.txt"
    test_file.parent.mkdir(parents=True, exist_ok=True)
    test_file.write_text("Test content")

    result = temp_processor.convert_file(
        test_file,
        domain="test-domain",
        output_filename="custom_name"
    )

    assert result.success is True
    assert result.output_path.name == "custom_name.md"


def test_convert_directory_empty(temp_processor, tmp_path):
    """Test conversion of empty directory."""
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()

    results = temp_processor.convert_directory(empty_dir)

    assert len(results) == 0


def test_convert_directory_not_found(temp_processor):
    """Test conversion of non-existent directory."""
    results = temp_processor.convert_directory(Path("nonexistent_dir"))

    assert len(results) == 0


def test_convert_directory_success(temp_processor, tmp_path):
    """Test successful directory batch conversion."""
    # Create multiple test files
    source_dir = tmp_path / "uploads"
    source_dir.mkdir(parents=True, exist_ok=True)

    (source_dir / "test1.txt").write_text("Content 1")
    (source_dir / "test2.txt").write_text("Content 2")
    (source_dir / "test3.csv").write_text("col1,col2\nval1,val2")

    results = temp_processor.convert_directory(source_dir, domain="test-domain")

    assert len(results) == 3
    assert all(r.success for r in results)
    assert all(r.output_path.exists() for r in results)


def test_convert_directory_mixed_results(temp_processor, tmp_path):
    """Test directory conversion with mixed success/failure."""
    source_dir = tmp_path / "uploads"
    source_dir.mkdir(parents=True, exist_ok=True)

    # Valid file
    (source_dir / "test1.txt").write_text("Content 1")
    # Unsupported format (should be skipped)
    (source_dir / "test2.xyz").write_text("Content 2")
    # Another valid file
    (source_dir / "test3.json").write_text('{"key": "value"}')

    results = temp_processor.convert_directory(source_dir, domain="test-domain")

    # Only supported formats should be processed
    assert len(results) == 2  # .txt and .json files only
    assert all(r.success for r in results)


def test_save_markdown(temp_processor, tmp_path):
    """Test Markdown content saving."""
    content = "# Test Markdown\n\nThis is a test."
    output_path = tmp_path / "documents" / "test-domain" / "test.md"

    temp_processor._save_markdown(content, output_path)

    assert output_path.exists()
    assert output_path.read_text(encoding='utf-8') == content


def test_supported_format_enum():
    """Test SupportedFormat enum values."""
    assert SupportedFormat.PDF.value == ".pdf"
    assert SupportedFormat.DOCX.value == ".docx"
    assert SupportedFormat.XLSX.value == ".xlsx"
    assert SupportedFormat.PPTX.value == ".pptx"
    assert SupportedFormat.HTML.value == ".html"
    assert SupportedFormat.TXT.value == ".txt"
    assert SupportedFormat.CSV.value == ".csv"
    assert SupportedFormat.JSON.value == ".json"
    assert SupportedFormat.XML.value == ".xml"


def test_conversion_result_model():
    """Test ConversionResult model validation."""
    # Success case
    result = ConversionResult(
        success=True,
        source_path=Path("test.pdf"),
        output_path=Path("output.md"),
        markdown_content="# Test"
    )
    assert result.success is True
    assert result.source_path == Path("test.pdf")
    assert result.output_path == Path("output.md")
    assert result.markdown_content == "# Test"
    assert result.error_message is None

    # Failure case
    result = ConversionResult(
        success=False,
        source_path=Path("test.pdf"),
        error_message="Conversion failed"
    )
    assert result.success is False
    assert result.error_message == "Conversion failed"
    assert result.output_path is None
    assert result.markdown_content is None
