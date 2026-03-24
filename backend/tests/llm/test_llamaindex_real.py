"""LlamaIndex 実API統合テスト

実際のLLM/embeddingサーバーに接続して、LlamaIndexのRAGパイプライン全体を検証します。
通常のテスト実行では除外されます。

実行方法:
    make test-llm-api              # すべての実APIテストを実行
    make test-llm-api-llamacpp     # llama.cpp サーバーのテストのみ
    make test-llm-api-google       # Google GenAI のテストのみ
"""

import os

import pytest
from llama_index.core import Document, Settings, VectorStoreIndex
from llama_index.core.embeddings import MockEmbedding

from lakda.llm.client import LlmClientManager
from lakda.llm.providers.google_genai import GoogleGenAILlmClient
from lakda.llm.providers.llamacpp import LlamaCppEmbeddingClient, LlamaCppLlmClient


# ---------------------------------------------------------------------------
# サーバー到達確認
# ---------------------------------------------------------------------------


def _is_llamacpp_llm_reachable() -> bool:
    url = os.getenv("LLAMACPP_LLM_URL")
    if not url:
        return False
    try:
        import httpx

        with httpx.Client(timeout=5) as client:
            return client.get(f"{url}/health").status_code == 200
    except Exception:
        return False


def _is_llamacpp_embedding_reachable() -> bool:
    url = os.getenv("LLAMACPP_EMBEDDING_URL")
    if not url:
        return False
    try:
        import httpx

        with httpx.Client(timeout=5) as client:
            return client.get(f"{url}/health").status_code == 200
    except Exception:
        return False


is_llamacpp_llm_reachable = _is_llamacpp_llm_reachable()
is_llamacpp_embedding_reachable = _is_llamacpp_embedding_reachable()
has_google_key = os.getenv("GOOGLE_API_KEY") is not None


# ---------------------------------------------------------------------------
# フィクスチャ
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def reset_settings():
    """各テスト後に Settings をリセット"""
    yield
    Settings.llm = None
    Settings.embed_model = None


# ---------------------------------------------------------------------------
# llama.cpp: LLM + Embedding フルパイプライン
# ---------------------------------------------------------------------------


@pytest.mark.llm_api
@pytest.mark.skipif(
    not (is_llamacpp_llm_reachable and is_llamacpp_embedding_reachable),
    reason="LLAMACPP_LLM_URL / LLAMACPP_EMBEDDING_URL が到達不可",
)
class TestLlamaCppLlamaIndexReal:
    """llama.cpp サーバーを使った LlamaIndex 実統合テスト"""

    LLM_MODEL = "hf.co/unsloth/Qwen3.5-9B-GGUF:IQ4_NL"
    EMBED_MODEL = "bge-m3"

    def test_settings_assignment(self) -> None:
        """実クライアントを Settings に設定できる"""
        llm_client = LlamaCppLlmClient(model=self.LLM_MODEL)
        embed_client = LlamaCppEmbeddingClient(model_name=self.EMBED_MODEL)

        Settings.llm = llm_client.llm
        Settings.embed_model = embed_client.embed_model

        assert Settings.llm is not None
        assert Settings.embed_model is not None

    def test_index_documents(self) -> None:
        """実 embedding でドキュメントをインデクシングできる"""
        embed_client = LlamaCppEmbeddingClient(model_name=self.EMBED_MODEL)
        Settings.embed_model = embed_client.embed_model

        docs = [
            Document(text="Python はプログラミング言語です。"),
            Document(text="LlamaIndex は LLM アプリ向けデータフレームワークです。"),
        ]
        index = VectorStoreIndex.from_documents(docs)

        assert index is not None

    def test_query_engine_full_pipeline(self) -> None:
        """実 LLM + 実 embedding でクエリエンジンが応答を返す"""
        llm_client = LlamaCppLlmClient(model=self.LLM_MODEL)
        embed_client = LlamaCppEmbeddingClient(model_name=self.EMBED_MODEL)

        Settings.llm = llm_client.llm
        Settings.embed_model = embed_client.embed_model

        docs = [Document(text="LAKDA は RAG ベースのナレッジ検索アプリケーションです。")]
        index = VectorStoreIndex.from_documents(docs)
        engine = index.as_query_engine()

        response = engine.query("LAKDA とは何ですか？")

        assert response is not None
        assert str(response).strip() != ""

    def test_manager_registers_and_queries(self) -> None:
        """LlmClientManager 経由で登録し、クエリを実行できる"""
        manager = LlmClientManager()
        manager.register(provider="llamacpp", model=self.LLM_MODEL)
        manager.register_embedding(provider="llamacpp", model_name=self.EMBED_MODEL)

        Settings.llm = manager.get_llm()
        Settings.embed_model = manager.get_embed_model()

        docs = [Document(text="llama.cpp は CPU で LLM を実行するためのフレームワークです。")]
        index = VectorStoreIndex.from_documents(docs)
        engine = index.as_query_engine()

        response = engine.query("llama.cpp とは何ですか？")

        assert response is not None
        assert str(response).strip() != ""


# ---------------------------------------------------------------------------
# Google GenAI: LLM のみ（embedding は MockEmbedding）
# ---------------------------------------------------------------------------


@pytest.mark.llm_api
@pytest.mark.skipif(not has_google_key, reason="GOOGLE_API_KEY が設定されていません")
class TestGoogleGenAILlamaIndexReal:
    """Google GenAI LLM を使った LlamaIndex 実統合テスト

    embedding は MockEmbedding を使用します（Google 側に embedding サーバー不要）。
    """

    GOOGLE_MODEL = "gemini-2.5-flash-lite"

    def test_settings_llm_assignment(self) -> None:
        """GoogleGenAILlmClient を Settings.llm に設定できる"""
        client = GoogleGenAILlmClient(model=self.GOOGLE_MODEL)
        Settings.llm = client.llm

        assert Settings.llm is not None

    def test_query_engine_with_mock_embedding(self) -> None:
        """Google GenAI LLM + MockEmbedding でクエリエンジンが応答を返す"""
        client = GoogleGenAILlmClient(model=self.GOOGLE_MODEL)
        Settings.llm = client.llm
        Settings.embed_model = MockEmbedding(embed_dim=384)

        docs = [Document(text="LAKDA は RAG ベースのナレッジ検索アプリケーションです。")]
        index = VectorStoreIndex.from_documents(docs)
        engine = index.as_query_engine()

        response = engine.query("LAKDA とは何ですか？")

        assert response is not None
        assert str(response).strip() != ""
