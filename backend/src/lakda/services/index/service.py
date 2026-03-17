"""インデックスサービス - Markdown → Neo4j PropertyGraphStore のオーケストレーション"""

import logging
import re
import time

from llama_index.core import PropertyGraphIndex, Settings

logger = logging.getLogger(__name__)

from lakda.db import Neo4jGraphStoreManager
from lakda.services.index.pipeline import IndexPipeline
from lakda.services.index.store import IndexStore


def _is_xml_prefixed(text: str) -> bool:
    """テキストの冒頭に XML タグがあるかどうかを判定する

    先頭の空白を除いた最初の文字列が '<tag' 形式であれば True を返す。

    Examples:
        >>> _is_xml_prefixed("<document>...")
        True
        >>> _is_xml_prefixed("# Markdown")
        False
    """
    return bool(re.match(r"\s*<[a-zA-Z]", text))


class IndexService:
    """テキストの形式を判定し、適切なインデキシング処理にルーティングするサービス

    現在サポートしている形式:
        - Markdown: LlamaIndex PropertyGraphIndex でエンティティ・関係を抽出し Neo4j に保存
        - XML prefix (冒頭に XML タグ): 未実装 (NotImplementedError)

    使い方:
        Settings.llm = manager.get_llm()
        Settings.embed_model = manager.get_embed_model()

        service = IndexService(graph_store_manager)
        service.index(markdown_text="# タイトル\\n本文...", doc_id="doc-001")
    """

    def __init__(self, graph_store_manager: Neo4jGraphStoreManager) -> None:
        self._store = IndexStore(graph_store_manager)
        self._pipeline = IndexPipeline(self._store.graph_store)

    def index(
        self,
        markdown_text: str,
        doc_id: str | None = None,
        chunk_size: int = 256,
        chunk_overlap: int = 32,
        show_progress: bool = False,
    ) -> PropertyGraphIndex:
        """テキストの形式を判定し、適切な処理にルーティングする

        Args:
            markdown_text: インデキシング対象のテキスト
            doc_id: ドキュメント識別子（None の場合は自動生成）
            chunk_size: チャンクサイズ（トークン数）
            chunk_overlap: チャンクオーバーラップ（トークン数）
            show_progress: 進捗表示フラグ

        Returns:
            Neo4j に保存された PropertyGraphIndex

        Raises:
            NotImplementedError: 冒頭に XML タグがある場合
        """
        if _is_xml_prefixed(markdown_text):
            logger.info("[service] XML-prefixed document detected doc=%s — not yet implemented", doc_id or "(no id)")
            return self._index_xml(markdown_text, doc_id)

        return self._index_markdown(markdown_text, doc_id, chunk_size, chunk_overlap, show_progress)

    def _index_markdown(
        self,
        text: str,
        doc_id: str | None,
        chunk_size: int,
        chunk_overlap: int,
        show_progress: bool,
    ) -> PropertyGraphIndex:
        logger.info("[service] pipeline.run START doc=%s", doc_id or "(no id)")
        t0 = time.perf_counter()
        result = self._pipeline.run(
            markdown_text=text,
            doc_id=doc_id,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            show_progress=show_progress,
        )
        logger.info("[service] pipeline.run DONE elapsed=%.2fs", time.perf_counter() - t0)
        return result

    def _index_xml(self, text: str, doc_id: str | None) -> PropertyGraphIndex:
        # TODO: XML 形式のインデキシングを実装する
        raise NotImplementedError("XML-prefixed documents are not yet supported")

    def get_index(self) -> PropertyGraphIndex:
        """Neo4j に保存済みのインデックスを取得する"""
        return self._store.get_index()
