"""IndexService 統合テスト

実際の Neo4j および llama.cpp サーバーに接続して、
Markdown → Neo4j PropertyGraphStore のフルパイプラインを検証します。

実行方法:
    make test-index          # インデックスサービス統合テストを実行
"""

import os

import pytest
from llama_index.core import PropertyGraphIndex, Settings

from lakda.db import Neo4jGraphStoreManager
from lakda.llm.client import LlmClientManager
from lakda.services.index.pipeline import IndexPipeline
from lakda.services.index.service import IndexService, _is_xml_prefixed
from lakda.services.index.store import IndexStore


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

SAMPLE_MARKDOWN = """
# Python エラーハンドリング

## AttributeError

AttributeError はオブジェクトに存在しない属性にアクセスしたときに発生します。

**原因**: 変数名のタイプミス、未初期化のオブジェクト。
**解決策**: `hasattr()` で属性の存在を事前に確認する。

## TypeError

TypeError は不正な型に対して操作を行ったときに発生します。

**原因**: 文字列と整数の加算など型の不一致。
**解決策**: `isinstance()` で型チェックを行う。
"""


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
# _is_xml_prefixed テスト（外部依存なし）
# ---------------------------------------------------------------------------


class TestIsXmlPrefixed:
    def test_xml_tag_at_start(self):
        assert _is_xml_prefixed("<document>本文</document>") is True

    def test_xml_tag_with_leading_whitespace(self):
        assert _is_xml_prefixed("  <root>...</root>") is True

    def test_xml_tag_with_newline(self):
        assert _is_xml_prefixed("\n<article>...</article>") is True

    def test_markdown_heading(self):
        assert _is_xml_prefixed("# タイトル\n本文") is False

    def test_plain_text(self):
        assert _is_xml_prefixed("普通のテキスト") is False

    def test_closing_tag_is_not_prefix(self):
        assert _is_xml_prefixed("</document>") is False

    def test_empty_string(self):
        assert _is_xml_prefixed("") is False


class TestIndexServiceRouting:
    """IndexService のルーティングロジックのテスト（外部依存なし）"""

    def test_xml_prefixed_raises_not_implemented(self):
        from unittest.mock import MagicMock
        manager = MagicMock()
        service = IndexService(manager)
        with pytest.raises(NotImplementedError):
            service.index("<document>本文</document>", doc_id="doc-xml")

    def test_markdown_routes_to_pipeline(self):
        from unittest.mock import MagicMock, patch
        manager = MagicMock()
        service = IndexService(manager)
        with patch.object(service, "_index_markdown", return_value=MagicMock()) as mock:
            service.index("# Markdown テキスト", doc_id="doc-md")
            mock.assert_called_once()


# ---------------------------------------------------------------------------
# IndexStore テスト
# ---------------------------------------------------------------------------


@pytest.mark.db
@pytest.mark.skipif(not is_neo4j_reachable, reason="Neo4j が到達不可")
class TestIndexStore:
    """IndexStore の単体テスト（Neo4j のみ必要）"""

    def test_graph_store_property(self, graph_store_manager):
        """graph_store プロパティが Neo4jPropertyGraphStore を返すこと"""
        from llama_index.graph_stores.neo4j import Neo4jPropertyGraphStore

        store = IndexStore(graph_store_manager)
        assert isinstance(store.graph_store, Neo4jPropertyGraphStore)

    def test_get_index_returns_property_graph_index(self, graph_store_manager):
        """get_index() が PropertyGraphIndex を返すこと"""
        store = IndexStore(graph_store_manager)
        index = store.get_index()
        assert isinstance(index, PropertyGraphIndex)


# ---------------------------------------------------------------------------
# IndexPipeline テスト
# ---------------------------------------------------------------------------


@pytest.mark.db
@pytest.mark.llm_api
@pytest.mark.skipif(
    not (is_llm_reachable and is_embedding_reachable and is_neo4j_reachable),
    reason="llama.cpp LLM / Embedding または Neo4j が到達不可",
)
class TestIndexPipeline:
    """IndexPipeline の統合テスト（llama.cpp + Neo4j 必要）"""

    def test_run_creates_index(self, graph_store_manager, llm_manager):
        """run() が PropertyGraphIndex を返すこと"""
        _ = llm_manager  # Settings.llm / embed_model のセットアップに使用
        pipeline = IndexPipeline(graph_store_manager.store)
        index = pipeline.run(
            markdown_text=SAMPLE_MARKDOWN,
            doc_id="test-pipeline-001",
        )
        assert isinstance(index, PropertyGraphIndex)

# ---------------------------------------------------------------------------
# IndexService テスト（フルパイプライン）
# ---------------------------------------------------------------------------


@pytest.mark.db
@pytest.mark.llm_api
@pytest.mark.skipif(
    not (is_llm_reachable and is_embedding_reachable and is_neo4j_reachable),
    reason="llama.cpp LLM / Embedding または Neo4j が到達不可",
)
class TestIndexServiceFullPipeline:
    """IndexService のフルパイプライン統合テスト"""

    def test_index_markdown_to_neo4j(self, graph_store_manager, llm_manager):
        """Markdown テキストを Neo4j にインデキシングできること"""
        _ = llm_manager  # Settings.llm / embed_model のセットアップに使用
        service = IndexService(graph_store_manager)
        index = service.index(
            markdown_text=SAMPLE_MARKDOWN,
            doc_id="test-service-001",
        )
        assert isinstance(index, PropertyGraphIndex)

    def test_get_index_after_indexing(self, graph_store_manager, llm_manager):
        """インデキシング後に get_index() でインデックスを取得できること"""
        _ = llm_manager  # Settings.llm / embed_model のセットアップに使用
        service = IndexService(graph_store_manager)
        service.index(
            markdown_text=SAMPLE_MARKDOWN,
            doc_id="test-service-get-001",
        )
        retrieved = service.get_index()
        assert isinstance(retrieved, PropertyGraphIndex)
