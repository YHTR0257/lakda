"""インデックスストア - Neo4j PropertyGraphStore との統合"""

from llama_index.core import PropertyGraphIndex, Settings
from llama_index.graph_stores.neo4j import Neo4jPropertyGraphStore

from lakda.db import Neo4jGraphStoreManager


class IndexStore:
    """Neo4j PropertyGraphStore をバックエンドとした PropertyGraphIndex を管理するクラス

    LlamaIndex の PropertyGraphIndex を Neo4j に永続化します。

    Attributes:
        _manager: Neo4j 接続マネージャー
        _graph_store: Neo4jPropertyGraphStore インスタンス
    """

    def __init__(self, manager: Neo4jGraphStoreManager) -> None:
        """IndexStore を初期化する

        Args:
            manager: Neo4jGraphStoreManager インスタンス
        """
        self._manager = manager

    @property
    def graph_store(self) -> Neo4jPropertyGraphStore:
        """Neo4jPropertyGraphStore インスタンスを返す

        Returns:
            Neo4jPropertyGraphStore インスタンス
        """
        return self._manager.store

    def get_index(self) -> PropertyGraphIndex:
        """既存の Neo4j グラフから PropertyGraphIndex を取得する

        Neo4j に保存済みのグラフデータから検索可能な
        PropertyGraphIndex を構築して返します。

        Returns:
            PropertyGraphIndex インスタンス
        """
        return PropertyGraphIndex.from_existing(
            property_graph_store=self.graph_store,
        )

    def save(self, index: PropertyGraphIndex) -> None:
        """PropertyGraphIndex の内容を Neo4j に永続化する

        LlamaIndex の PropertyGraphIndex は from_documents() 時点で
        Neo4jPropertyGraphStore に自動書き込みされますが、
        明示的な flush が必要な場合にこのメソッドを使用します。

        Args:
            index: 永続化する PropertyGraphIndex
        """
        index.storage_context.persist()
