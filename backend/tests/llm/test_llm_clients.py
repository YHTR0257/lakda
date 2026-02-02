"""LLMクライアントの正常系ユニットテスト

モックを使用して各LLMプロバイダーの正常系をテストします。
"""

from unittest.mock import MagicMock, patch

import pytest
from pydantic import BaseModel

from lakda.llm.anthropic import AnthropicLlmClient
from lakda.llm.gemini import GeminiLlmClient
from lakda.llm.ollama import OllamaLlmClient
from lakda.llm.open_router import OpenRouterLlmClient


class SampleResponse(BaseModel):
    """テスト用のレスポンスモデル"""

    answer: str
    confidence: float


class TestAnthropicLlmClient:
    """Anthropic Claudeクライアントの正常系テスト"""

    @patch("lakda.llm.anthropic.anthropic.Anthropic")
    def test_generate_response_success(self, mock_anthropic_class):
        """case1: Anthropic Claudeからの応答取得"""
        # Arrange
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text='{"answer": "Hello!", "confidence": 0.95}')]
        mock_client.messages.create.return_value = mock_response

        client = AnthropicLlmClient(api_key="test-api-key", model="claude-3-5-sonnet-20241022")

        # Act
        result = client.generate_response(prompt="Say hello", response_model=SampleResponse)

        # Assert
        assert result.answer == "Hello!"
        assert result.confidence == 0.95
        mock_client.messages.create.assert_called_once()

    @patch("lakda.llm.anthropic.anthropic.Anthropic")
    def test_health_check_success(self, mock_anthropic_class):
        """Anthropic Claudeのヘルスチェック成功"""
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client
        mock_client.messages.create.return_value = MagicMock()

        client = AnthropicLlmClient(api_key="test-api-key")

        assert client.health_check() is True


class TestOllamaLlmClient:
    """Ollamaクライアントの正常系テスト"""

    @pytest.fixture
    def respx_mock(self):
        """respxモックのフィクスチャ"""
        import respx

        with respx.mock:
            yield respx

    def test_generate_response_success(self, respx_mock):
        """case2: Ollamaからの応答取得"""
        import httpx

        # Arrange
        respx_mock.post("http://localhost:11434/api/generate").mock(
            return_value=httpx.Response(
                200, json={"response": '{"answer": "Hello from Ollama!", "confidence": 0.88}'}
            )
        )

        client = OllamaLlmClient(base_url="http://localhost:11434", model="llama3.2")

        # Act
        result = client.generate_response(prompt="Say hello", response_model=SampleResponse)

        # Assert
        assert result.answer == "Hello from Ollama!"
        assert result.confidence == 0.88

    def test_health_check_success(self, respx_mock):
        """Ollamaのヘルスチェック成功"""
        import httpx

        respx_mock.get("http://localhost:11434/api/tags").mock(
            return_value=httpx.Response(200, json={"models": []})
        )

        client = OllamaLlmClient(base_url="http://localhost:11434")

        assert client.health_check() is True


class TestGeminiLlmClient:
    """Gemini APIクライアントの正常系テスト"""

    @patch("lakda.llm.gemini.genai.Client")
    def test_generate_response_success(self, mock_genai_client_class):
        """case3: Gemini-APIからの応答取得"""
        # Arrange
        mock_client = MagicMock()
        mock_genai_client_class.return_value = mock_client
        mock_response = MagicMock()
        mock_response.text = '{"answer": "Hello from Gemini!", "confidence": 0.92}'
        mock_client.models.generate_content.return_value = mock_response

        client = GeminiLlmClient(api_key="test-api-key", model="gemini-1.5-pro")

        # Act
        result = client.generate_response(prompt="Say hello", response_model=SampleResponse)

        # Assert
        assert result.answer == "Hello from Gemini!"
        assert result.confidence == 0.92
        mock_client.models.generate_content.assert_called_once()

    @patch("lakda.llm.gemini.genai.Client")
    def test_health_check_success(self, mock_genai_client_class):
        """Gemini APIのヘルスチェック成功"""
        mock_client = MagicMock()
        mock_genai_client_class.return_value = mock_client
        mock_client.models.list.return_value = MagicMock()

        client = GeminiLlmClient(api_key="test-api-key")

        assert client.health_check() is True


class TestOpenRouterLlmClient:
    """OpenRouterクライアントの正常系テスト"""

    @patch("lakda.llm.open_router.OpenAI")
    def test_generate_response_success(self, mock_openai_class):
        """case4: OpenRouterからの応答取得"""
        # Arrange
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(
                message=MagicMock(content='{"answer": "Hello from OpenRouter!", "confidence": 0.90}')
            )
        ]
        mock_client.chat.completions.create.return_value = mock_response

        client = OpenRouterLlmClient(api_key="test-api-key", model="google/gemma-3-27b-it:free")

        # Act
        result = client.generate_response(prompt="Say hello", response_model=SampleResponse)

        # Assert
        assert result.answer == "Hello from OpenRouter!"
        assert result.confidence == 0.90
        mock_client.chat.completions.create.assert_called_once()

    @patch("lakda.llm.open_router.OpenAI")
    def test_health_check_success(self, mock_openai_class):
        """OpenRouterのヘルスチェック成功"""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_client.models.list.return_value = MagicMock()

        client = OpenRouterLlmClient(api_key="test-api-key")

        assert client.health_check() is True
