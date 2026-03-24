"""AskService / AskRetrieval テスト"""

import os
from unittest.mock import MagicMock

import pytest
from llama_index.core import PropertyGraphIndex, Settings

from lakda.db import Neo4jGraphStoreManager
from lakda.llm.client import LlmClientManager
from lakda.models.schemas.ask import AnswerResponse, SourceItem
from lakda.services.ask.retrieval import AskRetrieval
from lakda.services.ask.service import AskService


# ---------------------------------------------------------------------------
# サーバー到達確認
# ---------------------------------------------------------------------------


def _is_llamacpp_reachable(env_var: str, default: str) -> bool:
    url = os.getenv(env_var, default)
    try:
        import httpx

        with httpx.Client(timeout=5) as client:
            return client.get(f"{url}/health").status_code == 200
    except Exception:
        return False


def _is_neo4j_reachable() -> bool:
    manager = Neo4jGraphStoreManager()
    return manager.health_check()


is_llm_reachable = _is_llamacpp_reachable("LLAMACPP_LLM_URL", "http://localhost:11406")
is_embedding_reachable = _is_llamacpp_reachable(
    "LLAMACPP_EMBEDDING_URL", "http://localhost:11407"
)
is_neo4j_reachable = _is_neo4j_reachable()

LLM_MODEL = "hf.co/unsloth/Qwen3.5-9B-GGUF:IQ4_NL"
EMBED_MODEL = "bge-m3"


# ---------------------------------------------------------------------------
# フィクスチャ
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def reset_settings():
    """各テスト後に LlamaIndex Settings をリセット"""
    yield
    Settings.llm = None
    Settings.embed_model = None


@pytest.fixture
def graph_store_manager() -> Neo4jGraphStoreManager:
    return Neo4jGraphStoreManager()


@pytest.fixture
def llm_manager() -> LlmClientManager:
    manager = LlmClientManager()
    manager.register(provider="llamacpp", model=LLM_MODEL)
    manager.register_embedding(provider="llamacpp", model_name=EMBED_MODEL)
    Settings.llm = manager.get_llm()
    Settings.embed_model = manager.get_embed_model()
    return manager


# ---------------------------------------------------------------------------
# AskRetrieval テスト（外部依存なし）
# ---------------------------------------------------------------------------


class TestAskRetrieval:
    def test_query_calls_query_engine(self):
        """query() が index.as_query_engine().query() を呼ぶこと"""
        mock_response = MagicMock()
        mock_response.source_nodes = []
        mock_query_engine = MagicMock()
        mock_query_engine.query.return_value = mock_response
        mock_index = MagicMock(spec=PropertyGraphIndex)
        mock_index.as_query_engine.return_value = mock_query_engine

        retrieval = AskRetrieval(mock_index)
        result = retrieval.query("AttributeError の原因は？")

        mock_index.as_query_engine.assert_called_once_with(
            include_text=True,
            similarity_top_k=3,
        )
        mock_query_engine.query.assert_called_once_with("AttributeError の原因は？")
        assert result is mock_response

    def test_query_passes_similarity_top_k(self):
        """max_results が similarity_top_k に渡されること"""
        mock_query_engine = MagicMock()
        mock_query_engine.query.return_value = MagicMock(source_nodes=[])
        mock_index = MagicMock(spec=PropertyGraphIndex)
        mock_index.as_query_engine.return_value = mock_query_engine

        retrieval = AskRetrieval(mock_index)
        retrieval.query("質問", max_results=7)

        mock_index.as_query_engine.assert_called_once_with(
            include_text=True,
            similarity_top_k=7,
        )


# ---------------------------------------------------------------------------
# AskService テスト（外部依存なし）
# ---------------------------------------------------------------------------


class TestAskService:
    def _make_mock_node(self, doc_id: str, content: str, score: float):
        node = MagicMock()
        node.metadata = {"doc_id": doc_id}
        node.get_content.return_value = content
        node_with_score = MagicMock()
        node_with_score.node = node
        node_with_score.score = score
        return node_with_score

    def test_answer_returns_answer_response(self):
        """answer() が AnswerResponse を返すこと"""
        from unittest.mock import patch

        mock_response = MagicMock()
        mock_response.source_nodes = []
        mock_response.__str__ = lambda self: "回答テキスト"

        mock_retrieval = MagicMock(spec=AskRetrieval)
        mock_retrieval.query.return_value = mock_response

        mock_index = MagicMock(spec=PropertyGraphIndex)
        mock_store = MagicMock()
        mock_store.get_index.return_value = mock_index

        mock_graph_manager = MagicMock(spec=Neo4jGraphStoreManager)
        mock_llm_manager = MagicMock(spec=LlmClientManager)

        service = AskService(mock_graph_manager, mock_llm_manager)
        service._store = mock_store

        with patch("lakda.services.ask.service.Settings") as mock_settings, \
             patch("lakda.services.ask.service.AskRetrieval", return_value=mock_retrieval):
            result = service.answer("session-1", "AttributeError の原因は？")

        assert isinstance(result, AnswerResponse)
        assert result.session_id == "session-1"
        assert result.question == "AttributeError の原因は？"
        assert result.answer == "回答テキスト"
        assert result.sources == []

    def test_answer_maps_source_nodes(self):
        """source_nodes が SourceItem のリストに変換されること"""
        from unittest.mock import patch

        node1 = self._make_mock_node("doc-001", "snippet text here", 0.95)
        node2 = self._make_mock_node("doc-002", "another snippet", 0.80)

        mock_response = MagicMock()
        mock_response.source_nodes = [node1, node2]
        mock_response.__str__ = lambda self: "回答"

        mock_retrieval = MagicMock(spec=AskRetrieval)
        mock_retrieval.query.return_value = mock_response

        mock_store = MagicMock()
        mock_store.get_index.return_value = MagicMock(spec=PropertyGraphIndex)

        mock_graph_manager = MagicMock(spec=Neo4jGraphStoreManager)
        mock_llm_manager = MagicMock(spec=LlmClientManager)

        service = AskService(mock_graph_manager, mock_llm_manager)
        service._store = mock_store

        with patch("lakda.services.ask.service.Settings"), \
             patch("lakda.services.ask.service.AskRetrieval", return_value=mock_retrieval):
            result = service.answer("session-2", "質問テキスト")

        assert len(result.sources) == 2
        assert result.sources[0].file == "doc-001"
        assert result.sources[0].snippet == "snippet text here"
        assert result.sources[0].score == 0.95
        assert result.sources[1].file == "doc-002"
        assert result.sources[1].score == 0.80


# ---------------------------------------------------------------------------
# AskService 統合テスト（Neo4j + llama.cpp 必要）
# ---------------------------------------------------------------------------


@pytest.mark.db
@pytest.mark.llm_api
@pytest.mark.skipif(
    not (is_llm_reachable and is_embedding_reachable and is_neo4j_reachable),
    reason="llama.cpp LLM / Embedding または Neo4j が到達不可",
)
class TestAskServiceIntegration:
    def test_answer_returns_text(self, graph_store_manager, llm_manager):
        """answer() が回答テキストを含む AnswerResponse を返すこと"""
        service = AskService(graph_store_manager, llm_manager)
        result = service.answer(
            session_id="integration-test-001",
            question="AttributeError の原因は？",
            max_results=3,
        )
        assert isinstance(result, AnswerResponse)
        assert len(result.answer) > 0
        assert result.session_id == "integration-test-001"
