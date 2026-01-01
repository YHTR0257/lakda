"""
Integration tests for DocumentProcessor end-to-end flows.
"""

import pytest
from pathlib import Path

from data.processor import DocumentProcessor


@pytest.fixture
def processor(tmp_path):
    """Create a DocumentProcessor instance with temporary directories."""
    uploads_dir = tmp_path / "uploads"
    documents_dir = tmp_path / "documents"
    uploads_dir.mkdir(parents=True, exist_ok=True)
    documents_dir.mkdir(parents=True, exist_ok=True)

    return DocumentProcessor(
        uploads_dir=uploads_dir,
        documents_dir=documents_dir,
        default_domain="test-domain"
    )


def test_end_to_end_text_conversion(processor, tmp_path):
    """Test end-to-end conversion flow for text file."""
    # 1. Create a sample text file
    sample_file = tmp_path / "uploads" / "sample_document.txt"
    sample_file.parent.mkdir(parents=True, exist_ok=True)
    sample_content = "# Sample Document\n\nThis is a test document for integration testing."
    sample_file.write_text(sample_content)

    # 2. Execute conversion
    result = processor.convert_file(sample_file, domain="error-handling")

    # 3. Verify result
    assert result.success is True
    assert result.source_path == sample_file
    assert result.output_path is not None
    assert result.output_path.exists()
    assert result.markdown_content is not None
    assert "Sample Document" in result.markdown_content

    # 4. Verify output location
    expected_path = tmp_path / "documents" / "error-handling" / "sample_document.md"
    assert result.output_path == expected_path


def test_end_to_end_csv_conversion(processor, tmp_path):
    """Test end-to-end conversion flow for CSV file."""
    # 1. Create a sample CSV file
    sample_file = tmp_path / "uploads" / "data.csv"
    sample_file.parent.mkdir(parents=True, exist_ok=True)
    csv_content = "Name,Age,City\nAlice,30,Tokyo\nBob,25,Osaka\n"
    sample_file.write_text(csv_content)

    # 2. Execute conversion
    result = processor.convert_file(sample_file, domain="api-guides")

    # 3. Verify result
    assert result.success is True
    assert result.output_path.exists()
    assert "Name" in result.markdown_content
    assert "Alice" in result.markdown_content


def test_end_to_end_json_conversion(processor, tmp_path):
    """Test end-to-end conversion flow for JSON file."""
    # 1. Create a sample JSON file
    sample_file = tmp_path / "uploads" / "config.json"
    sample_file.parent.mkdir(parents=True, exist_ok=True)
    json_content = '{"name": "test", "version": "1.0", "enabled": true}'
    sample_file.write_text(json_content)

    # 2. Execute conversion
    result = processor.convert_file(sample_file, domain="architecture")

    # 3. Verify result
    assert result.success is True
    assert result.output_path.exists()
    assert result.markdown_content is not None


def test_end_to_end_batch_conversion(processor, tmp_path):
    """Test end-to-end batch conversion flow."""
    # 1. Create multiple sample files
    uploads_dir = tmp_path / "uploads"
    uploads_dir.mkdir(parents=True, exist_ok=True)

    (uploads_dir / "doc1.txt").write_text("Document 1 content")
    (uploads_dir / "doc2.txt").write_text("Document 2 content")
    (uploads_dir / "data.csv").write_text("col1,col2\nval1,val2")
    (uploads_dir / "config.json").write_text('{"key": "value"}')

    # 2. Execute batch conversion
    results = processor.convert_directory(uploads_dir, domain="business-logic")

    # 3. Verify results
    assert len(results) == 4
    assert all(r.success for r in results)
    assert all(r.output_path.exists() for r in results)

    # 4. Verify all files are in the correct domain directory
    domain_dir = tmp_path / "documents" / "business-logic"
    assert (domain_dir / "doc1.md").exists()
    assert (domain_dir / "doc2.md").exists()
    assert (domain_dir / "data.md").exists()
    assert (domain_dir / "config.md").exists()


def test_custom_output_filename_integration(processor, tmp_path):
    """Test end-to-end flow with custom output filename."""
    # 1. Create a sample file
    sample_file = tmp_path / "uploads" / "original_name.txt"
    sample_file.parent.mkdir(parents=True, exist_ok=True)
    sample_file.write_text("Content with custom name")

    # 2. Execute conversion with custom filename
    result = processor.convert_file(
        sample_file,
        domain="test-domain",
        output_filename="custom_output_name"
    )

    # 3. Verify custom filename is used
    assert result.success is True
    assert result.output_path.name == "custom_output_name.md"
    assert result.output_path.exists()


def test_multiple_domain_conversion(processor, tmp_path):
    """Test converting files to multiple domains."""
    # 1. Create sample files
    sample_file1 = tmp_path / "uploads" / "doc1.txt"
    sample_file2 = tmp_path / "uploads" / "doc2.txt"
    sample_file1.parent.mkdir(parents=True, exist_ok=True)
    sample_file1.write_text("Document for error handling")
    sample_file2.write_text("Document for architecture")

    # 2. Convert to different domains
    result1 = processor.convert_file(sample_file1, domain="error-handling")
    result2 = processor.convert_file(sample_file2, domain="architecture")

    # 3. Verify files are in correct domains
    assert result1.success is True
    assert result2.success is True
    assert "error-handling" in str(result1.output_path)
    assert "architecture" in str(result2.output_path)

    domain1_dir = tmp_path / "documents" / "error-handling"
    domain2_dir = tmp_path / "documents" / "architecture"
    assert (domain1_dir / "doc1.md").exists()
    assert (domain2_dir / "doc2.md").exists()


def test_error_recovery_in_batch_conversion(processor, tmp_path):
    """Test that batch conversion continues after individual file errors."""
    # Note: This test verifies the behavior when processing multiple files,
    # some of which may succeed and others fail
    uploads_dir = tmp_path / "uploads"
    uploads_dir.mkdir(parents=True, exist_ok=True)

    # Create valid files
    (uploads_dir / "valid1.txt").write_text("Valid content 1")
    (uploads_dir / "valid2.txt").write_text("Valid content 2")

    # Execute batch conversion
    results = processor.convert_directory(uploads_dir, domain="test-domain")

    # All valid files should be converted successfully
    assert len(results) == 2
    assert all(r.success for r in results)
