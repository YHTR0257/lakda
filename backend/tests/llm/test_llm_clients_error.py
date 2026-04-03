"""LLMクライアントの異常系ユニットテスト

モックを使用して各LLMプロバイダーの異常系をテストします。
"""

from unittest.mock import MagicMock, patch

import httpx
import pytest
from pydantic import BaseModel

from lakda.llm.exceptions import (
    LlmAuthenticationError,
    LlmConnectionError,
    LlmRateLimitError,
    LlmResponseParseError,
    LlmTimeoutError,
)
from lakda.llm.providers.anthropic import AnthropicLlmClient
from lakda.llm.providers.google_genai import GoogleGenAILlmClient
from lakda.llm.providers.llamacpp import LlamaCppLlmClient
from lakda.llm.providers.openrouter import OpenRouterLlmClient


class SampleResponse(BaseModel):
    answer: str
    confidence: float


class TestAnthropicLlmClientError:
    """Anthropic Claudeクライアントの異常系テスト"""

    @patch("lakda.llm.providers.anthropic.Anthropic")
    def test_authentication_error(self, mock_anthropic_class: MagicMock) -> None:
        """case1: 認証エラー（無効なAPIキー）"""
        mock_llm = MagicMock()
        mock_anthropic_class.return_value = mock_llm
        mock_structured_llm = MagicMock()
        mock_llm.as_structured_llm.return_value = mock_structured_llm

        class MockAuthError(Exception):
            pass

        error = MockAuthError("Invalid API key")
        error.__class__.__name__ = "AuthenticationError"
        mock_structured_llm.complete.side_effect = error

        client = AnthropicLlmClient(api_key="invalid-key")

        with pytest.raises(LlmAuthenticationError):
            client.generate_response(prompt="Hello", response_model=SampleResponse)

    @patch("lakda.llm.providers.anthropic.Anthropic")
    def test_rate_limit_error(self, mock_anthropic_class: MagicMock) -> None:
        """case2: レートリミットエラー"""
        mock_llm = MagicMock()
        mock_anthropic_class.return_value = mock_llm
        mock_structured_llm = MagicMock()
        mock_llm.as_structured_llm.return_value = mock_structured_llm

        class MockRateLimitError(Exception):
            pass

        error = MockRateLimitError("Rate limit exceeded")
        error.__class__.__name__ = "RateLimitError"
        mock_structured_llm.complete.side_effect = error

        client = AnthropicLlmClient(api_key="test-key")

        with pytest.raises(LlmRateLimitError):
            client.generate_response(prompt="Hello", response_model=SampleResponse)

    @patch("lakda.llm.providers.anthropic.Anthropic")
    def test_response_parse_error(self, mock_anthropic_class: MagicMock) -> None:
        """case3: レスポンスパースエラー（Noneレスポンス）"""
        mock_llm = MagicMock()
        mock_anthropic_class.return_value = mock_llm
        mock_structured_llm = MagicMock()
        mock_llm.as_structured_llm.return_value = mock_structured_llm
        mock_response = MagicMock()
        mock_response.raw = None
        mock_structured_llm.complete.return_value = mock_response

        client = AnthropicLlmClient(api_key="test-key")

        with pytest.raises(LlmResponseParseError):
            client.generate_response(prompt="Hello", response_model=SampleResponse)

    @patch("lakda.llm.providers.anthropic.Anthropic")
    def test_health_check_failure(self, mock_anthropic_class: MagicMock) -> None:
        """case4: ヘルスチェック失敗"""
        mock_llm = MagicMock()
        mock_anthropic_class.return_value = mock_llm
        mock_llm.complete.side_effect = Exception("Connection failed")

        client = AnthropicLlmClient(api_key="test-key")

        assert client.health_check() is False


class TestLlamaCppLlmClientError:
    """LlamaCppクライアントの異常系テスト"""

    @pytest.fixture
    def respx_mock(self):
        """respxモックのフィクスチャ"""
        import respx

        with respx.mock:
            yield respx

    @patch("lakda.llm.providers.llamacpp.OpenAILike")
    def test_connection_error(self, mock_openai_like_class: MagicMock) -> None:
        """case5: 接続エラー（サーバー未起動）"""
        mock_llm = MagicMock()
        mock_openai_like_class.return_value = mock_llm
        mock_structured_llm = MagicMock()
        mock_llm.as_structured_llm.return_value = mock_structured_llm

        class MockConnectionError(Exception):
            pass

        error = MockConnectionError("Connection refused")
        error.__class__.__name__ = "ConnectionError"
        mock_structured_llm.complete.side_effect = error

        client = LlamaCppLlmClient(base_url="http://localhost:11406")

        with pytest.raises(LlmConnectionError) as exc_info:
            client.generate_response(prompt="Hello", response_model=SampleResponse)

        assert "Connection refused" in str(exc_info.value)

    @patch("lakda.llm.providers.llamacpp.OpenAILike")
    def test_timeout_error(self, mock_openai_like_class: MagicMock) -> None:
        """case6: タイムアウトエラー"""
        mock_llm = MagicMock()
        mock_openai_like_class.return_value = mock_llm
        mock_structured_llm = MagicMock()
        mock_llm.as_structured_llm.return_value = mock_structured_llm

        class MockTimeoutError(Exception):
            pass

        error = MockTimeoutError("Request timed out")
        error.__class__.__name__ = "TimeoutError"
        mock_structured_llm.complete.side_effect = error

        client = LlamaCppLlmClient(base_url="http://localhost:11406")

        with pytest.raises(LlmTimeoutError):
            client.generate_response(prompt="Hello", response_model=SampleResponse)

    def test_health_check_failure(self, respx_mock) -> None:
        """case8: ヘルスチェック失敗"""
        respx_mock.get("http://localhost:11406/health").mock(
            side_effect=httpx.ConnectError("Connection refused")
        )

        with patch("lakda.llm.providers.llamacpp.OpenAILike"):
            client = LlamaCppLlmClient(base_url="http://localhost:11406")

        assert client.health_check() is False


class TestGoogleGenAILlmClientError:
    """Google GenAI APIクライアントの異常系テスト"""

    @patch("lakda.llm.providers.google_genai.GoogleGenAI")
    def test_authentication_error(self, mock_genai_class: MagicMock) -> None:
        """case9: 認証エラー（無効なAPIキー）"""
        mock_llm = MagicMock()
        mock_genai_class.return_value = mock_llm
        mock_structured_llm = MagicMock()
        mock_llm.as_structured_llm.return_value = mock_structured_llm

        class MockUnauthenticated(Exception):
            pass

        error = MockUnauthenticated("Invalid API key")
        error.__class__.__name__ = "AuthenticationError"
        mock_structured_llm.complete.side_effect = error

        client = GoogleGenAILlmClient(api_key="invalid-key")

        with pytest.raises(LlmAuthenticationError):
            client.generate_response(prompt="Hello", response_model=SampleResponse)

    @patch("lakda.llm.providers.google_genai.GoogleGenAI")
    def test_rate_limit_error(self, mock_genai_class: MagicMock) -> None:
        """case10: レートリミットエラー"""
        mock_llm = MagicMock()
        mock_genai_class.return_value = mock_llm
        mock_structured_llm = MagicMock()
        mock_llm.as_structured_llm.return_value = mock_structured_llm

        class MockResourceExhausted(Exception):
            pass

        error = MockResourceExhausted("Quota exceeded")
        error.__class__.__name__ = "RateLimitError"
        mock_structured_llm.complete.side_effect = error

        client = GoogleGenAILlmClient(api_key="test-key")

        with pytest.raises(LlmRateLimitError):
            client.generate_response(prompt="Hello", response_model=SampleResponse)

    @patch("lakda.llm.providers.google_genai.GoogleGenAI")
    def test_response_parse_error(self, mock_genai_class: MagicMock) -> None:
        """case11: レスポンスパースエラー"""
        mock_llm = MagicMock()
        mock_genai_class.return_value = mock_llm
        mock_structured_llm = MagicMock()
        mock_llm.as_structured_llm.return_value = mock_structured_llm
        mock_response = MagicMock()
        mock_response.raw = None
        mock_structured_llm.complete.return_value = mock_response

        client = GoogleGenAILlmClient(api_key="test-key")

        with pytest.raises(LlmResponseParseError):
            client.generate_response(prompt="Hello", response_model=SampleResponse)

    @patch("lakda.llm.providers.google_genai.GoogleGenAI")
    def test_health_check_failure(self, mock_genai_class: MagicMock) -> None:
        """case12: ヘルスチェック失敗"""
        mock_llm = MagicMock()
        mock_genai_class.return_value = mock_llm
        mock_llm.complete.side_effect = Exception("Service unavailable")

        client = GoogleGenAILlmClient(api_key="test-key")

        assert client.health_check() is False


class TestOpenRouterLlmClientError:
    """OpenRouterクライアントの異常系テスト"""

    @patch("lakda.llm.providers.openrouter.OpenRouter")
    def test_authentication_error(self, mock_openrouter_class: MagicMock) -> None:
        """case13: 認証エラー（無効なAPIキー）"""
        mock_llm = MagicMock()
        mock_openrouter_class.return_value = mock_llm
        mock_structured_llm = MagicMock()
        mock_llm.as_structured_llm.return_value = mock_structured_llm

        class MockAuthError(Exception):
            pass

        error = MockAuthError("Invalid API key")
        error.__class__.__name__ = "AuthenticationError"
        mock_structured_llm.complete.side_effect = error

        client = OpenRouterLlmClient(api_key="invalid-key")

        with pytest.raises(LlmAuthenticationError):
            client.generate_response(prompt="Hello", response_model=SampleResponse)

    @patch("lakda.llm.providers.openrouter.OpenRouter")
    def test_rate_limit_error(self, mock_openrouter_class: MagicMock) -> None:
        """case14: レートリミットエラー"""
        mock_llm = MagicMock()
        mock_openrouter_class.return_value = mock_llm
        mock_structured_llm = MagicMock()
        mock_llm.as_structured_llm.return_value = mock_structured_llm

        class MockRateLimitError(Exception):
            pass

        error = MockRateLimitError("Rate limit exceeded")
        error.__class__.__name__ = "RateLimitError"
        mock_structured_llm.complete.side_effect = error

        client = OpenRouterLlmClient(api_key="test-key")

        with pytest.raises(LlmRateLimitError):
            client.generate_response(prompt="Hello", response_model=SampleResponse)

    @patch("lakda.llm.providers.openrouter.OpenRouter")
    def test_response_parse_error(self, mock_openrouter_class: MagicMock) -> None:
        """case16: レスポンスパースエラー"""
        mock_llm = MagicMock()
        mock_openrouter_class.return_value = mock_llm
        mock_structured_llm = MagicMock()
        mock_llm.as_structured_llm.return_value = mock_structured_llm
        mock_response = MagicMock()
        mock_response.raw = None
        mock_structured_llm.complete.return_value = mock_response

        client = OpenRouterLlmClient(api_key="test-key")

        with pytest.raises(LlmResponseParseError):
            client.generate_response(prompt="Hello", response_model=SampleResponse)

    @patch("lakda.llm.providers.openrouter.OpenRouter")
    def test_health_check_failure(self, mock_openrouter_class: MagicMock) -> None:
        """case17: ヘルスチェック失敗"""
        mock_llm = MagicMock()
        mock_openrouter_class.return_value = mock_llm
        mock_llm.complete.side_effect = Exception("Connection failed")

        client = OpenRouterLlmClient(api_key="test-key")

        assert client.health_check() is False
