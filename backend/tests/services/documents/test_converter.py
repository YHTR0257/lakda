"""DocumentConverter / FrontmatterConverter のユニットテスト"""

import json

import pytest

from lakda.models.schemas.documents import FrontmatterMeta
from lakda.services.documents.converter import DocumentConverter, FrontmatterConverter

SAMPLE_META = FrontmatterMeta(
    domain="architecture",
    tags=["api", "design"],
    title="Sample Doc",
    created_at="2026-03-25T00:00:00+00:00",
    source_file="sample.pdf",
)

SAMPLE_FRONTMATTER_MD = """\
---
domain: architecture
tags:
- api
- design
title: Sample Doc
created_at: '2026-03-25T00:00:00+00:00'
source_file: sample.pdf
---

# 本文

内容です。
"""

SAMPLE_BODY = "# 本文\n\n内容です。\n"


@pytest.fixture
def converter():
    return FrontmatterConverter()


class TestIsFrontmatterPresent:
    def test_returns_true_when_frontmatter_exists(self, converter):
        assert converter.is_frontmatter_present(SAMPLE_FRONTMATTER_MD) is True

    def test_returns_false_for_plain_markdown(self, converter):
        assert converter.is_frontmatter_present("# タイトル\n本文") is False

    def test_returns_false_for_empty_string(self, converter):
        assert converter.is_frontmatter_present("") is False


class TestParseFrontmatter:
    def test_parses_valid_frontmatter(self, converter):
        meta, body = converter.parse_frontmatter(SAMPLE_FRONTMATTER_MD)
        assert meta is not None
        assert meta.domain == "architecture"
        assert meta.tags == ["api", "design"]
        assert meta.title == "Sample Doc"
        assert meta.source_file == "sample.pdf"
        assert "本文" in body

    def test_returns_none_for_plain_markdown(self, converter):
        meta, body = converter.parse_frontmatter(SAMPLE_BODY)
        assert meta is None
        assert body == SAMPLE_BODY

    def test_returns_none_for_empty_string(self, converter):
        meta, body = converter.parse_frontmatter("")
        assert meta is None
        assert body == ""

    def test_tags_defaults_to_empty_list_when_missing(self, converter):
        md = "---\ndomain: general\ncreated_at: '2026-01-01'\nsource_file: x.pdf\n---\n\n本文"
        meta, _ = converter.parse_frontmatter(md)
        assert meta is not None
        assert meta.tags == []


class TestAddFrontmatter:
    def test_adds_frontmatter_to_plain_markdown(self, converter):
        result = converter.add_frontmatter(SAMPLE_BODY, SAMPLE_META)
        assert result.startswith("---\n")
        assert "domain: architecture" in result
        assert "本文" in result

    def test_idempotent_when_frontmatter_already_present(self, converter):
        result = converter.add_frontmatter(SAMPLE_FRONTMATTER_MD, SAMPLE_META)
        assert result == SAMPLE_FRONTMATTER_MD

    def test_body_preserved_after_frontmatter(self, converter):
        result = converter.add_frontmatter(SAMPLE_BODY, SAMPLE_META)
        assert SAMPLE_BODY.strip() in result


# ---------------------------------------------------------------------------
# DocumentConverter
# ---------------------------------------------------------------------------

PDF_MAGIC_BYTES = b"%PDF-1.4 fake pdf content"
PNG_MAGIC_BYTES = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00"
JPEG_MAGIC_BYTES = b"\xff\xd8\xff\xe0" + b"\x00" * 8


@pytest.fixture
def doc_converter():
    return DocumentConverter()


class TestDetectFormat:
    def test_detects_json(self, doc_converter):
        data = json.dumps({"key": "value"}).encode()
        mime = doc_converter.detect_format(data, "test.json")
        assert mime == "application/json"

    def test_detects_pdf(self, doc_converter):
        mime = doc_converter.detect_format(PDF_MAGIC_BYTES, "test.pdf")
        assert mime == "application/pdf"

    def test_detects_png(self, doc_converter):
        mime = doc_converter.detect_format(PNG_MAGIC_BYTES, "test.png")
        assert mime == "image/png"

    def test_detects_jpeg(self, doc_converter):
        mime = doc_converter.detect_format(JPEG_MAGIC_BYTES, "test.jpg")
        assert mime == "image/jpeg"

    def test_raises_for_unsupported_format(self, doc_converter):
        # ZIP ファイルのマジックバイト
        zip_bytes = b"PK\x03\x04" + b"\x00" * 20
        with pytest.raises(ValueError, match="Unsupported"):
            doc_converter.detect_format(zip_bytes, "test.zip")


class TestConvertToMarkdown:
    def test_converts_json(self, doc_converter):
        data = json.dumps({"name": "test", "value": 42}).encode()
        result = doc_converter.convert_to_markdown(data, "application/json")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_raises_runtime_error_on_failure(self, doc_converter, monkeypatch):
        from markitdown import MarkItDown

        def broken_convert(self, path):
            raise Exception("markitdown internal error")

        monkeypatch.setattr(MarkItDown, "convert", broken_convert)
        data = json.dumps({}).encode()
        with pytest.raises(RuntimeError, match="Conversion failed"):
            doc_converter.convert_to_markdown(data, "application/json")
