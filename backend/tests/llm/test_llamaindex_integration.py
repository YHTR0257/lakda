"""LlamaIndex統合ユニットテスト

LlmClientManager が LlamaIndex の Settings / VectorStoreIndex / QueryEngine と
正しく統合できることをモックで確認します。
"""

from unittest.mock import patch

import pytest
from llama_index.core import Document, Settings, VectorStoreIndex
from llama_index.core.embeddings import BaseEmbedding, MockEmbedding
from llama_index.core.llms import LLM
from llama_index.core.llms.mock import MockLLM

from lakda.llm.client import LlmClientManager
from lakda.llm.providers.llamacpp import LlamaCppEmbeddingClient, LlamaCppLlmClient


@pytest.fixture(autouse=True)
def reset_settings():
    """各テスト後に Settings をリセットしてテスト間の干渉を防ぐ"""
    yield
    Settings.llm = None
    Settings.embed_model = None


class TestLlamaCppClientLlamaIndexTypes:
    """LlamaCppClient が LlamaIndex の型インターフェースを満たすことを確認"""

    @patch("lakda.llm.providers.llamacpp.OpenAILike")
    def test_llm_client_exposes_llamaindex_llm(self, mock_openai_like_cls) -> None:
        """LlamaCppLlmClient.llm が LlamaIndex LLM インスタンスを返す"""
        mock_llm = MockLLM()
        mock_openai_like_cls.return_value = mock_llm

        client = LlamaCppLlmClient(base_url="http://localhost:11406")

        assert client.llm is mock_llm
        assert isinstance(client.llm, LLM)

    @patch("lakda.llm.providers.llamacpp.OpenAIEmbedding")
    def test_embedding_client_exposes_llamaindex_embed_model(self, mock_embed_cls) -> None:
        """LlamaCppEmbeddingClient.embed_model が LlamaIndex BaseEmbedding インスタンスを返す"""
        mock_embed = MockEmbedding(embed_dim=384)
        mock_embed_cls.return_value = mock_embed

        client = LlamaCppEmbeddingClient(base_url="http://localhost:11407")

        assert client.embed_model is mock_embed
        assert isinstance(client.embed_model, BaseEmbedding)


class TestSettingsIntegration:
    """LlmClientManager から LlamaIndex Settings への統合テスト"""

    @patch("lakda.llm.providers.llamacpp.OpenAILike")
    def test_get_llm_can_be_set_to_settings(self, mock_openai_like_cls) -> None:
        """manager.get_llm() を Settings.llm に設定できる"""
        mock_openai_like_cls.return_value = MockLLM()

        manager = LlmClientManager()
        manager.register(provider="llamacpp", model="test-model")

        Settings.llm = manager.get_llm()

        assert Settings.llm is manager.get_llm()
        assert isinstance(Settings.llm, LLM)

    @patch("lakda.llm.providers.llamacpp.OpenAIEmbedding")
    def test_get_embed_model_can_be_set_to_settings(self, mock_embed_cls) -> None:
        """manager.get_embed_model() を Settings.embed_model に設定できる"""
        mock_embed_cls.return_value = MockEmbedding(embed_dim=384)

        manager = LlmClientManager()
        manager.register_embedding(provider="llamacpp", model_name="bge-m3")

        Settings.embed_model = manager.get_embed_model()

        assert Settings.embed_model is manager.get_embed_model()
        assert isinstance(Settings.embed_model, BaseEmbedding)

    @patch("lakda.llm.providers.llamacpp.OpenAIEmbedding")
    @patch("lakda.llm.providers.llamacpp.OpenAILike")
    def test_settings_reflect_registered_clients(self, mock_llm_cls, mock_embed_cls) -> None:
        """LLM と embedding を両方登録して Settings に反映できる"""
        mock_llm_cls.return_value = MockLLM()
        mock_embed_cls.return_value = MockEmbedding(embed_dim=384)

        manager = LlmClientManager()
        manager.register(provider="llamacpp", model="test-model")
        manager.register_embedding(provider="llamacpp", model_name="bge-m3")

        Settings.llm = manager.get_llm()
        Settings.embed_model = manager.get_embed_model()

        assert Settings.llm is not None
        assert Settings.embed_model is not None


class TestVectorStoreIndexIntegration:
    """VectorStoreIndex / QueryEngine との統合テスト"""

    def test_index_documents_with_mock_embedding(self) -> None:
        """MockEmbedding でドキュメントをインデクシングできる"""
        Settings.embed_model = MockEmbedding(embed_dim=384)

        docs = [
            Document(text="Python is a programming language."),
            Document(text="LlamaIndex is a data framework for LLM applications."),
        ]
        index = VectorStoreIndex.from_documents(docs)

        assert index is not None

    def test_query_engine_returns_response(self) -> None:
        """MockLLM + MockEmbedding でクエリエンジンが応答を返す"""
        Settings.llm = MockLLM()
        Settings.embed_model = MockEmbedding(embed_dim=384)

        docs = [Document(text="Python is a programming language.")]
        index = VectorStoreIndex.from_documents(docs)
        engine = index.as_query_engine()

        response = engine.query("What is Python?")

        assert response is not None
        assert str(response) != ""

    @patch("lakda.llm.providers.llamacpp.OpenAILike")
    @patch("lakda.llm.providers.llamacpp.OpenAIEmbedding")
    def test_llamacpp_client_llm_assigned_to_settings_indexes_documents(
        self, mock_embed_cls, mock_llm_cls
    ) -> None:
        """LlamaCppClient の LLM / embedding を Settings に設定してインデクシングできる"""
        mock_llm_cls.return_value = MockLLM()
        mock_embed_cls.return_value = MockEmbedding(embed_dim=384)

        manager = LlmClientManager()
        manager.register(provider="llamacpp", model="hf.co/unsloth/Qwen3.5-9B-GGUF:IQ4_NL")
        manager.register_embedding(provider="llamacpp", model_name="bge-m3")

        Settings.llm = manager.get_llm()
        Settings.embed_model = manager.get_embed_model()

        docs = [Document(text="LAKDA is a RAG application.")]
        index = VectorStoreIndex.from_documents(docs)
        engine = index.as_query_engine()

        response = engine.query("What is LAKDA?")

        assert response is not None
