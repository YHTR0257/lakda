"""インデックスサービス - Markdown → Neo4j PropertyGraphStore のオーケストレーション"""

from llama_index.core import PropertyGraphIndex, Settings

from lakda.db import Neo4jGraphStoreManager
from lakda.llm.client import LlmClientManager
from lakda.services.index.pipeline import IndexPipeline
from lakda.services.index.store import IndexStore


class IndexService:
    """Markdown テキストを Neo4j PropertyGraphStore にインデキシングするサービス

    pipeline（エンティティ・関係の抽出）と store（Neo4j への永続化）を
    オーケストレーションします。

    使い方:
        manager = LlmClientManager()
        manager.register(provider="llamacpp", model="...")
        manager.register_embedding(provider="llamacpp", model_name="...")

        Settings.llm = manager.get_llm()
        Settings.embed_model = manager.get_embed_model()

        graph_store_manager = Neo4jGraphStoreManager()
        service = IndexService(graph_store_manager)
        service.index(markdown_text="# タイトル\\n本文...", doc_id="doc-001")
    """

    def __init__(self, graph_store_manager: Neo4jGraphStoreManager) -> None:
        """IndexService を初期化する

        Args:
            graph_store_manager: Neo4j 接続マネージャー
        """
        self._store = IndexStore(graph_store_manager)
        self._pipeline = IndexPipeline(self._store.graph_store)

    def index(
        self,
        markdown_text: str,
        doc_id: str | None = None,
        show_progress: bool = False,
    ) -> PropertyGraphIndex:
        """Markdown テキストをインデキシングして Neo4j に保存する

        LlamaIndex Settings.llm および Settings.embed_model が
        事前に設定されている必要があります。

        Args:
            markdown_text: インデキシング対象の Markdown テキスト
            doc_id: ドキュメント識別子（None の場合は自動生成）
            show_progress: 進捗表示フラグ

        Returns:
            Neo4j に保存された PropertyGraphIndex
        """
        return self._pipeline.run(
            markdown_text=markdown_text,
            doc_id=doc_id,
            show_progress=show_progress,
        )

    def get_index(self) -> PropertyGraphIndex:
        """Neo4j に保存済みのインデックスを取得する

        Returns:
            PropertyGraphIndex インスタンス
        """
        return self._store.get_index()
