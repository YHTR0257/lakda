"""LLMクライアントの異常系ユニットテスト

モックを使用して各LLMプロバイダーの異常系をテストします。
"""

from unittest.mock import MagicMock, patch

import httpx
import pytest
from pydantic import BaseModel

from lakda.llm.anthropic import AnthropicLlmClient
from lakda.llm.exceptions import (
    LlmAuthenticationError,
    LlmConnectionError,
    LlmRateLimitError,
    LlmResponseParseError,
    LlmTimeoutError,
)
from lakda.llm.gemini import GeminiLlmClient
from lakda.llm.ollama import OllamaLlmClient
from lakda.llm.open_router import OpenRouterLlmClient


class SampleResponse(BaseModel):
    answer: str
    confidence: float


class TestAnthropicLlmClientError:
    """Anthropic Claudeクライアントの異常系テスト"""

    @patch("lakda.llm.anthropic.anthropic.Anthropic")
    def test_authentication_error(self, mock_anthropic_class):
        """case1: 認証エラー（無効なAPIキー）"""
        import anthropic

        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client
        mock_client.messages.create.side_effect = anthropic.AuthenticationError(
            message="Invalid API key", response=MagicMock(status_code=401), body={}
        )

        client = AnthropicLlmClient(api_key="invalid-key")

        with pytest.raises(LlmAuthenticationError):
            client.generate_response(prompt="Hello", response_model=SampleResponse)

    @patch("lakda.llm.anthropic.anthropic.Anthropic")
    def test_rate_limit_error(self, mock_anthropic_class):
        """case2: レートリミットエラー"""
        import anthropic

        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client
        mock_client.messages.create.side_effect = anthropic.RateLimitError(
            message="Rate limit exceeded", response=MagicMock(status_code=429), body={}
        )

        client = AnthropicLlmClient(api_key="test-key")

        with pytest.raises(LlmRateLimitError):
            client.generate_response(prompt="Hello", response_model=SampleResponse)

    @patch("lakda.llm.anthropic.anthropic.Anthropic")
    def test_response_parse_error(self, mock_anthropic_class):
        """case3: レスポンスパースエラー（不正なJSON）"""
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="This is not valid JSON")]
        mock_client.messages.create.return_value = mock_response

        client = AnthropicLlmClient(api_key="test-key")

        with pytest.raises(LlmResponseParseError):
            client.generate_response(prompt="Hello", response_model=SampleResponse)

    @patch("lakda.llm.anthropic.anthropic.Anthropic")
    def test_health_check_failure(self, mock_anthropic_class):
        """case4: ヘルスチェック失敗"""
        import anthropic

        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client
        mock_request = httpx.Request("POST", "https://api.anthropic.com/v1/messages")
        mock_client.messages.create.side_effect = anthropic.APIConnectionError(
            message="Connection failed", request=mock_request
        )

        client = AnthropicLlmClient(api_key="test-key")

        assert client.health_check() is False


class TestOllamaLlmClientError:
    """Ollamaクライアントの異常系テスト"""

    @pytest.fixture
    def respx_mock(self):
        """respxモックのフィクスチャ"""
        import respx

        with respx.mock:
            yield respx

    def test_connection_error(self, respx_mock):
        """case5: 接続エラー（サーバー未起動）"""
        respx_mock.post("http://localhost:11434/api/generate").mock(
            side_effect=httpx.ConnectError("Connection refused")
        )

        client = OllamaLlmClient(base_url="http://localhost:11434")

        with pytest.raises(LlmConnectionError) as exc_info:
            client.generate_response(prompt="Hello", response_model=SampleResponse)

        assert "Connection refused" in str(exc_info.value)

    def test_timeout_error(self, respx_mock):
        """case6: タイムアウトエラー"""
        respx_mock.post("http://localhost:11434/api/generate").mock(
            side_effect=httpx.TimeoutException("Request timed out")
        )

        client = OllamaLlmClient(base_url="http://localhost:11434", timeout=10)

        with pytest.raises(LlmTimeoutError):
            client.generate_response(prompt="Hello", response_model=SampleResponse)

    def test_model_not_found_error(self, respx_mock):
        """case7: モデル未インストールエラー"""
        respx_mock.post("http://localhost:11434/api/generate").mock(
            return_value=httpx.Response(
                404, json={"error": "model 'nonexistent-model' not found"}
            )
        )

        client = OllamaLlmClient(base_url="http://localhost:11434", model="nonexistent-model")

        with pytest.raises(LlmConnectionError) as exc_info:
            client.generate_response(prompt="Hello", response_model=SampleResponse)

        assert "not found" in str(exc_info.value)

    def test_health_check_failure(self, respx_mock):
        """case8: ヘルスチェック失敗"""
        respx_mock.get("http://localhost:11434/api/tags").mock(
            side_effect=httpx.ConnectError("Connection refused")
        )

        client = OllamaLlmClient(base_url="http://localhost:11434")

        assert client.health_check() is False


class TestGeminiLlmClientError:
    """Gemini APIクライアントの異常系テスト"""

    @patch("lakda.llm.gemini.genai.Client")
    def test_authentication_error(self, mock_genai_client_class):
        """case9: 認証エラー（無効なAPIキー）"""

        class MockUnauthenticated(Exception):
            pass

        mock_client = MagicMock()
        mock_genai_client_class.return_value = mock_client
        error = MockUnauthenticated("Invalid API key")
        error.__class__.__name__ = "Unauthenticated"
        mock_client.models.generate_content.side_effect = error

        client = GeminiLlmClient(api_key="invalid-key")

        with pytest.raises(LlmAuthenticationError):
            client.generate_response(prompt="Hello", response_model=SampleResponse)

    @patch("lakda.llm.gemini.genai.Client")
    def test_rate_limit_error(self, mock_genai_client_class):
        """case10: レートリミットエラー"""

        class MockResourceExhausted(Exception):
            pass

        mock_client = MagicMock()
        mock_genai_client_class.return_value = mock_client
        error = MockResourceExhausted("Quota exceeded")
        error.__class__.__name__ = "ResourceExhausted"
        mock_client.models.generate_content.side_effect = error

        client = GeminiLlmClient(api_key="test-key")

        with pytest.raises(LlmRateLimitError):
            client.generate_response(prompt="Hello", response_model=SampleResponse)

    @patch("lakda.llm.gemini.genai.Client")
    def test_response_parse_error(self, mock_genai_client_class):
        """case11: レスポンスパースエラー"""
        mock_client = MagicMock()
        mock_genai_client_class.return_value = mock_client
        mock_response = MagicMock()
        mock_response.text = "Invalid JSON response"
        mock_client.models.generate_content.return_value = mock_response

        client = GeminiLlmClient(api_key="test-key")

        with pytest.raises(LlmResponseParseError):
            client.generate_response(prompt="Hello", response_model=SampleResponse)

    @patch("lakda.llm.gemini.genai.Client")
    def test_health_check_failure(self, mock_genai_client_class):
        """case12: ヘルスチェック失敗"""
        mock_client = MagicMock()
        mock_genai_client_class.return_value = mock_client
        mock_client.models.list.side_effect = Exception("Service unavailable")

        client = GeminiLlmClient(api_key="test-key")

        assert client.health_check() is False


class TestOpenRouterLlmClientError:
    """OpenRouterクライアントの異常系テスト"""

    @patch("lakda.llm.open_router.OpenAI")
    def test_authentication_error(self, mock_openai_class):
        """case13: 認証エラー（無効なAPIキー）"""
        from openai import AuthenticationError

        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_client.chat.completions.create.side_effect = AuthenticationError(
            message="Invalid API key", response=MagicMock(status_code=401), body={}
        )

        client = OpenRouterLlmClient(api_key="invalid-key")

        with pytest.raises(LlmAuthenticationError):
            client.generate_response(prompt="Hello", response_model=SampleResponse)

    @patch("lakda.llm.open_router.OpenAI")
    def test_rate_limit_error(self, mock_openai_class):
        """case14: レートリミットエラー"""
        from openai import RateLimitError

        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_client.chat.completions.create.side_effect = RateLimitError(
            message="Rate limit exceeded", response=MagicMock(status_code=429), body={}
        )

        client = OpenRouterLlmClient(api_key="test-key")

        with pytest.raises(LlmRateLimitError):
            client.generate_response(prompt="Hello", response_model=SampleResponse)

    @patch("lakda.llm.open_router.OpenAI")
    def test_model_not_available_error(self, mock_openai_class):
        """case15: モデル利用不可エラー"""
        from openai import NotFoundError

        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_client.chat.completions.create.side_effect = NotFoundError(
            message="Model not found", response=MagicMock(status_code=404), body={}
        )

        client = OpenRouterLlmClient(api_key="test-key", model="nonexistent/model")

        with pytest.raises(LlmConnectionError):
            client.generate_response(prompt="Hello", response_model=SampleResponse)

    @patch("lakda.llm.open_router.OpenAI")
    def test_response_parse_error(self, mock_openai_class):
        """case16: レスポンスパースエラー"""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="Not valid JSON"))]
        mock_client.chat.completions.create.return_value = mock_response

        client = OpenRouterLlmClient(api_key="test-key")

        with pytest.raises(LlmResponseParseError):
            client.generate_response(prompt="Hello", response_model=SampleResponse)

    @patch("lakda.llm.open_router.OpenAI")
    def test_health_check_failure(self, mock_openai_class):
        """case17: ヘルスチェック失敗"""
        from openai import APIConnectionError

        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_request = httpx.Request("GET", "https://openrouter.ai/api/v1/models")
        mock_client.models.list.side_effect = APIConnectionError(
            message="Connection failed", request=mock_request
        )

        client = OpenRouterLlmClient(api_key="test-key")

        assert client.health_check() is False
