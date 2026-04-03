"""documents API エンドポイントテスト"""

import io
import json
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from lakda.main import app

client = TestClient(app)

PDF_BYTES = b"%PDF-1.4 fake"
JSON_BYTES = json.dumps({"key": "value"}).encode()
ZIP_BYTES = b"PK\x03\x04" + b"\x00" * 20


class TestUploadEndpoint:
    def test_unsupported_format_returns_422(self):
        """非対応フォーマット（ZIP）は 422 を返す"""
        response = client.post(
            "/documents/upload",
            files={"file": ("test.zip", io.BytesIO(ZIP_BYTES), "application/zip")},
        )
        assert response.status_code == 422
        assert "Unsupported" in response.json()["detail"]

    def test_upload_json_success(self):
        """JSON ファイルのアップロードが成功して ConvertResponse を返す"""
        with patch("lakda.api.documents._doc_converter") as mock_conv:
            mock_conv.detect_format.return_value = "application/json"
            mock_conv.convert_to_markdown.return_value = "# JSON content"

            response = client.post(
                "/documents/upload",
                files={"file": ("data.json", io.BytesIO(JSON_BYTES), "application/json")},
                data={"domain": "test-domain", "tags": ["tag1"]},
            )

        assert response.status_code == 200
        body = response.json()
        assert "doc_id" in body
        assert "markdown" in body
        assert body["format"] == "application/json"
        assert body["indexed"] is False
        assert "domain: test-domain" in body["markdown"]
        assert "source_file: data.json" in body["markdown"]

    def test_upload_with_auto_index(self):
        """auto_index=True で indexed=True が返る"""
        with (
            patch("lakda.api.documents._doc_converter") as mock_conv,
            patch("lakda.api.documents.IndexService") as mock_svc_cls,
        ):
            mock_conv.detect_format.return_value = "application/json"
            mock_conv.convert_to_markdown.return_value = "# content"
            mock_svc = MagicMock()
            mock_svc_cls.return_value = mock_svc

            response = client.post(
                "/documents/upload",
                files={"file": ("data.json", io.BytesIO(JSON_BYTES), "application/json")},
                data={"domain": "general", "auto_index": "true"},
            )

        assert response.status_code == 200
        assert response.json()["indexed"] is True

    def test_conversion_failure_returns_500(self):
        """変換失敗時は 500 を返す"""
        with patch("lakda.api.documents._doc_converter") as mock_conv:
            mock_conv.detect_format.return_value = "application/pdf"
            mock_conv.convert_to_markdown.side_effect = RuntimeError("markitdown crashed")

            response = client.post(
                "/documents/upload",
                files={"file": ("doc.pdf", io.BytesIO(PDF_BYTES), "application/pdf")},
            )

        assert response.status_code == 500
        assert "markitdown crashed" in response.json()["detail"]
