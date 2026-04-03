"""LLMクライアントの正常系ユニットテスト

モックを使用して各LLMプロバイダーの正常系をテストします。
"""

from unittest.mock import MagicMock, patch

import pytest
from pydantic import BaseModel

from lakda.llm.client import LlmClientManager
from lakda.llm.exceptions import LlmConnectionError
from lakda.llm.providers.anthropic import AnthropicLlmClient
from lakda.llm.providers.google_genai import GoogleGenAILlmClient
from lakda.llm.providers.llamacpp import LlamaCppLlmClient
from lakda.llm.providers.openrouter import OpenRouterLlmClient


class SampleResponse(BaseModel):
    """テスト用のレスポンスモデル"""

    answer: str
    confidence: float


class TestAnthropicLlmClient:
    """Anthropic Claudeクライアントの正常系テスト"""

    @patch("lakda.llm.providers.anthropic.Anthropic")
    def test_generate_response_success(self, mock_anthropic_class: MagicMock) -> None:
        """case1: Anthropic Claudeからの応答取得"""
        # Arrange
        mock_llm = MagicMock()
        mock_anthropic_class.return_value = mock_llm
        mock_structured_llm = MagicMock()
        mock_llm.as_structured_llm.return_value = mock_structured_llm
        mock_response = MagicMock()
        mock_response.raw = SampleResponse(answer="Hello!", confidence=0.95)
        mock_structured_llm.complete.return_value = mock_response

        client = AnthropicLlmClient(api_key="test-api-key", model="claude-3-5-sonnet-20241022")

        # Act
        result = client.generate_response(prompt="Say hello", response_model=SampleResponse)

        # Assert
        assert result.answer == "Hello!"
        assert result.confidence == 0.95
        mock_llm.as_structured_llm.assert_called_once_with(SampleResponse)
        mock_structured_llm.complete.assert_called_once_with("Say hello")

    @patch("lakda.llm.providers.anthropic.Anthropic")
    def test_health_check_success(self, mock_anthropic_class: MagicMock) -> None:
        """Anthropic Claudeのヘルスチェック成功"""
        mock_llm = MagicMock()
        mock_anthropic_class.return_value = mock_llm
        mock_llm.complete.return_value = MagicMock()

        client = AnthropicLlmClient(api_key="test-api-key")

        assert client.health_check() is True


class TestLlamaCppLlmClient:
    """LlamaCppクライアントの正常系テスト"""

    @pytest.fixture
    def respx_mock(self):
        """respxモックのフィクスチャ"""
        import respx

        with respx.mock:
            yield respx

    @patch("lakda.llm.providers.llamacpp.OpenAILike")
    def test_generate_response_success(self, mock_openai_like_class: MagicMock) -> None:
        """case2: llama.cpp LLMからの応答取得"""
        # Arrange
        mock_llm = MagicMock()
        mock_openai_like_class.return_value = mock_llm
        mock_structured_llm = MagicMock()
        mock_llm.as_structured_llm.return_value = mock_structured_llm
        mock_response = MagicMock()
        mock_response.raw = SampleResponse(answer="Hello from LlamaCpp!", confidence=0.88)
        mock_structured_llm.complete.return_value = mock_response

        client = LlamaCppLlmClient(base_url="http://localhost:11406", model="hf.co/unsloth/Qwen3.5-9B-GGUF:IQ4_NL")

        # Act
        result = client.generate_response(prompt="Say hello", response_model=SampleResponse)

        # Assert
        assert result.answer == "Hello from LlamaCpp!"
        assert result.confidence == 0.88

    def test_health_check_success(self, respx_mock) -> None:
        """llama.cpp LLMサーバーのヘルスチェック成功"""
        import httpx

        respx_mock.get("http://localhost:11406/health").mock(
            return_value=httpx.Response(200, json={"status": "ok"})
        )

        with patch("lakda.llm.providers.llamacpp.OpenAILike"):
            client = LlamaCppLlmClient(base_url="http://localhost:11406")

        assert client.health_check() is True


class TestGoogleGenAILlmClient:
    """Google GenAI APIクライアントの正常系テスト"""

    @patch("lakda.llm.providers.google_genai.GoogleGenAI")
    def test_generate_response_success(self, mock_genai_class: MagicMock) -> None:
        """case3: Google GenAI-APIからの応答取得"""
        # Arrange
        mock_llm = MagicMock()
        mock_genai_class.return_value = mock_llm
        mock_structured_llm = MagicMock()
        mock_llm.as_structured_llm.return_value = mock_structured_llm
        mock_response = MagicMock()
        mock_response.raw = SampleResponse(answer="Hello from Gemini!", confidence=0.92)
        mock_structured_llm.complete.return_value = mock_response

        client = GoogleGenAILlmClient(api_key="test-api-key", model="gemini-1.5-pro")

        # Act
        result = client.generate_response(prompt="Say hello", response_model=SampleResponse)

        # Assert
        assert result.answer == "Hello from Gemini!"
        assert result.confidence == 0.92
        mock_llm.as_structured_llm.assert_called_once_with(SampleResponse)
        mock_structured_llm.complete.assert_called_once_with("Say hello")

    @patch("lakda.llm.providers.google_genai.GoogleGenAI")
    def test_health_check_success(self, mock_genai_class: MagicMock) -> None:
        """Google GenAI APIのヘルスチェック成功"""
        mock_llm = MagicMock()
        mock_genai_class.return_value = mock_llm
        mock_llm.complete.return_value = MagicMock()

        client = GoogleGenAILlmClient(api_key="test-api-key")

        assert client.health_check() is True


class TestOpenRouterLlmClient:
    """OpenRouterクライアントの正常系テスト"""

    @patch("lakda.llm.providers.openrouter.OpenRouter")
    def test_generate_response_success(self, mock_openrouter_class: MagicMock) -> None:
        """case4: OpenRouterからの応答取得"""
        # Arrange
        mock_llm = MagicMock()
        mock_openrouter_class.return_value = mock_llm
        mock_structured_llm = MagicMock()
        mock_llm.as_structured_llm.return_value = mock_structured_llm
        mock_response = MagicMock()
        mock_response.raw = SampleResponse(answer="Hello from OpenRouter!", confidence=0.90)
        mock_structured_llm.complete.return_value = mock_response

        client = OpenRouterLlmClient(api_key="test-api-key", model="google/gemma-3-27b-it:free")

        # Act
        result = client.generate_response(prompt="Say hello", response_model=SampleResponse)

        # Assert
        assert result.answer == "Hello from OpenRouter!"
        assert result.confidence == 0.90
        mock_llm.as_structured_llm.assert_called_once_with(SampleResponse)
        mock_structured_llm.complete.assert_called_once_with("Say hello")

    @patch("lakda.llm.providers.openrouter.OpenRouter")
    def test_health_check_success(self, mock_openrouter_class: MagicMock) -> None:
        """OpenRouterのヘルスチェック成功"""
        mock_llm = MagicMock()
        mock_openrouter_class.return_value = mock_llm
        mock_llm.complete.return_value = MagicMock()

        client = OpenRouterLlmClient(api_key="test-api-key")

        assert client.health_check() is True


class TestLlmClientManager:
    """LlmClientManagerのユニットテスト"""

    def _make_mock_llm_client(self, model_name: str = "test-model") -> MagicMock:
        """モックのLlamaIndexLlmClientを生成する"""
        client = MagicMock()
        client.model = model_name
        client.health_check.return_value = True
        client.llm = MagicMock()
        return client

    def _make_mock_embed_client(self, model_name: str = "test-embed") -> MagicMock:
        """モックのembeddingクライアントを生成する"""
        client = MagicMock()
        client.model_name = model_name
        client.embed_model = MagicMock()
        client.health_check.return_value = True
        return client

    def test_register_and_get_llm(self) -> None:
        """チャットLLMの登録と取得"""
        manager = LlmClientManager()
        mock_client = self._make_mock_llm_client("llama3.1:8b")

        manager.register(provider="llamacpp", model="llama3.1:8b", client=mock_client)

        assert manager.get_llm() is mock_client.llm
        assert manager.current_provider == "llamacpp:llama3.1:8b"

    def test_register_embedding_and_get_embed_model(self) -> None:
        """embeddingの登録と取得"""
        manager = LlmClientManager()
        mock_embed = self._make_mock_embed_client("bge-m3")

        manager.register_embedding(provider="llamacpp", model_name="bge-m3", client=mock_embed)

        assert manager.get_embed_model() is mock_embed.embed_model
        assert manager.current_embedding == "llamacpp:bge-m3"

    def test_select_chat_llm(self) -> None:
        """selectでチャットLLMを切り替え"""
        manager = LlmClientManager()
        client1 = self._make_mock_llm_client("model-a")
        client2 = self._make_mock_llm_client("model-b")

        manager.register(provider="llamacpp", model="model-a", client=client1)
        manager.register(provider="llamacpp", model="model-b", client=client2)

        assert manager.current_provider == "llamacpp:model-a"

        manager.select(provider="llamacpp", model="model-b")
        assert manager.current_provider == "llamacpp:model-b"
        assert manager.get_llm() is client2.llm

    def test_select_embedding(self) -> None:
        """selectでembeddingを切り替え"""
        manager = LlmClientManager()
        embed1 = self._make_mock_embed_client("embed-a")
        embed2 = self._make_mock_embed_client("embed-b")

        manager.register_embedding(provider="llamacpp", model_name="embed-a", client=embed1)
        manager.register_embedding(provider="llamacpp", model_name="embed-b", client=embed2)

        manager.select(provider="llamacpp", model="embed-b")
        assert manager.current_embedding == "llamacpp:embed-b"
        assert manager.get_embed_model() is embed2.embed_model

    def test_select_auto_detects_type(self) -> None:
        """同一プロバイダーでチャットとembeddingを使い分け"""
        manager = LlmClientManager()
        chat = self._make_mock_llm_client("llama3.1:8b")
        embed = self._make_mock_embed_client("bge-m3")

        manager.register(provider="llamacpp", model="llama3.1:8b", client=chat)
        manager.register_embedding(provider="llamacpp", model_name="bge-m3", client=embed)

        # チャットLLMを選択
        manager.select(provider="llamacpp", model="llama3.1:8b")
        assert manager.current_provider == "llamacpp:llama3.1:8b"

        # embeddingを選択
        manager.select(provider="llamacpp", model="bge-m3")
        assert manager.current_embedding == "llamacpp:bge-m3"

        # 両方が同時に取得可能
        assert manager.get_llm() is chat.llm
        assert manager.get_embed_model() is embed.embed_model

    def test_select_unregistered_raises_error(self) -> None:
        """未登録モデルのselectでValueError"""
        manager = LlmClientManager()

        with pytest.raises(ValueError, match="登録されていません"):
            manager.select(provider="llamacpp", model="nonexistent")

    def test_get_embed_model_without_registration_raises_error(self) -> None:
        """embedding未登録でget_embed_modelするとLlmConnectionError"""
        manager = LlmClientManager()

        with pytest.raises(LlmConnectionError, match="embeddingクライアントが登録されていません"):
            manager.get_embed_model()

    def test_list_providers_includes_both_types(self) -> None:
        """list_providersがチャットとembedding両方を含む"""
        manager = LlmClientManager()
        chat = self._make_mock_llm_client("llama3.1:8b")
        embed = self._make_mock_embed_client("bge-m3")

        manager.register(provider="llamacpp", model="llama3.1:8b", client=chat)
        manager.register_embedding(provider="llamacpp", model_name="bge-m3", client=embed)

        providers = manager.list_providers()

        assert len(providers) == 2

        llm_entry = next(p for p in providers if p["type"] == "llm")
        assert llm_entry["key"] == "llamacpp:llama3.1:8b"
        assert llm_entry["is_current"] is True

        embed_entry = next(p for p in providers if p["type"] == "embedding")
        assert embed_entry["key"] == "llamacpp:bge-m3"
        assert embed_entry["is_current"] is True

    def test_health_check_with_provider_and_model(self) -> None:
        """provider + model 指定のヘルスチェック"""
        manager = LlmClientManager()
        chat = self._make_mock_llm_client("llama3.1:8b")
        embed = self._make_mock_embed_client("bge-m3")

        manager.register(provider="llamacpp", model="llama3.1:8b", client=chat)
        manager.register_embedding(provider="llamacpp", model_name="bge-m3", client=embed)

        assert manager.health_check(provider="llamacpp", model="llama3.1:8b") is True
        assert manager.health_check(provider="llamacpp", model="bge-m3") is True
        assert manager.health_check(provider="llamacpp", model="nonexistent") is False

    def test_first_registered_is_default(self) -> None:
        """最初に登録されたクライアントがデフォルトになる"""
        manager = LlmClientManager()
        chat = self._make_mock_llm_client("model-a")
        embed = self._make_mock_embed_client("embed-a")

        manager.register(provider="llamacpp", model="model-a", client=chat)
        manager.register_embedding(provider="llamacpp", model_name="embed-a", client=embed)

        assert manager.current_provider == "llamacpp:model-a"
        assert manager.current_embedding == "llamacpp:embed-a"
