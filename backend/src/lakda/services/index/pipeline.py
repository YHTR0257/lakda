"""インデキシングパイプライン - Markdown → PropertyGraphIndex"""

from llama_index.core import Document, PropertyGraphIndex, Settings
from llama_index.core.indices.property_graph import SimpleLLMPathExtractor
from llama_index.graph_stores.neo4j import Neo4jPropertyGraphStore


class IndexPipeline:
    """Markdown テキストを Neo4j PropertyGraphStore にインデキシングするパイプライン

    LlamaIndex の SimpleLLMPathExtractor を使ってエンティティと関係を抽出し、
    Neo4j PropertyGraphStore に保存します。

    入力: Markdown テキスト（str）
    出力: Neo4j に永続化された PropertyGraphIndex

    Attributes:
        _graph_store: インデックスの保存先 Neo4jPropertyGraphStore
    """

    def __init__(self, graph_store: Neo4jPropertyGraphStore) -> None:
        """IndexPipeline を初期化する

        Args:
            graph_store: 保存先の Neo4jPropertyGraphStore
        """
        self._graph_store = graph_store

    def run(
        self,
        markdown_text: str,
        doc_id: str | None = None,
        show_progress: bool = False,
    ) -> PropertyGraphIndex:
        """Markdown テキストからエンティティ・関係を抽出し Neo4j に保存する

        LlamaIndex Settings.llm が事前に設定されている必要があります。

        Args:
            markdown_text: インデキシング対象の Markdown テキスト
            doc_id: ドキュメント識別子（None の場合は自動生成）
            show_progress: 進捗表示フラグ

        Returns:
            Neo4j に保存された PropertyGraphIndex
        """
        metadata = {"doc_id": doc_id} if doc_id else {}
        document = Document(text=markdown_text, metadata=metadata)

        kg_extractor = SimpleLLMPathExtractor(llm=Settings.llm)

        index = PropertyGraphIndex.from_documents(
            documents=[document],
            property_graph_store=self._graph_store,
            kg_extractors=[kg_extractor],
            show_progress=show_progress,
        )

        return index
