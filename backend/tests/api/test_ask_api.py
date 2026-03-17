"""ask API エンドポイントテスト"""

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from lakda.main import app
from lakda.models.schemas.ask import AnswerResponse, SourceItem


client = TestClient(app)


def _make_answer_response() -> AnswerResponse:
    return AnswerResponse(
        session_id="session-abc",
        question="AttributeError の原因は？",
        answer="AttributeError はオブジェクトに存在しない属性にアクセスしたときに発生します。",
        sources=[
            SourceItem(
                file="doc-001",
                snippet="AttributeError の説明テキスト",
                score=0.95,
            )
        ],
        timestamp="2026-03-17T00:00:00+00:00",
    )


class TestConfirmEndpoint:
    def test_confirm_success_200(self):
        """正常なリクエストで 200 が返ること"""
        with patch(
            "lakda.api.ask.AskService"
        ) as mock_service_cls:
            mock_service = MagicMock()
            mock_service.answer.return_value = _make_answer_response()
            mock_service_cls.return_value = mock_service

            response = client.post(
                "/ask/confirm",
                json={
                    "session_id": "session-abc",
                    "confirmed_question": "AttributeError の原因は？",
                    "options": {"max_results": 3},
                },
            )

        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == "session-abc"
        assert data["question"] == "AttributeError の原因は？"
        assert "answer" in data
        assert len(data["sources"]) == 1

    def test_confirm_service_error_500(self):
        """サービスが例外を投げると 500 が返ること"""
        with patch(
            "lakda.api.ask.AskService"
        ) as mock_service_cls:
            mock_service = MagicMock()
            mock_service.answer.side_effect = RuntimeError("Neo4j connection failed")
            mock_service_cls.return_value = mock_service

            response = client.post(
                "/ask/confirm",
                json={
                    "session_id": "session-xyz",
                    "confirmed_question": "質問テキスト",
                    "options": {"max_results": 5},
                },
            )

        assert response.status_code == 500
        data = response.json()
        assert "Neo4j connection failed" in data["detail"]
