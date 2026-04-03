"""インデックスサービス - Markdown → Neo4j PropertyGraphStore のオーケストレーション"""

import logging
import re
import time
from datetime import datetime, timezone
from typing import cast, List

from llama_index.core import PropertyGraphIndex, Settings
from llama_index.core.graph_stores.types import EntityNode, LabelledNode

logger = logging.getLogger(__name__)

from lakda.db import Neo4jGraphStoreManager
from lakda.models.schemas.documents import FrontmatterMeta
from lakda.services.documents.converter import FrontmatterConverter
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
        # (1) Frontmatter パース
        converter = FrontmatterConverter()
        meta, _ = converter.parse_frontmatter(text)

        # (2) metadata 構築（doc_id + Frontmatter フィールド）
        metadata: dict = {"doc_id": doc_id} if doc_id else {}
        if meta:
            metadata.update({
                "domain": meta.domain,
                "tags": meta.tags,
                "source_file": meta.source_file,
                "created_at": meta.created_at,
            })

        # (3) パイプライン実行
        logger.info("[service] pipeline.run START doc=%s", doc_id or "(no id)")
        t0 = time.perf_counter()
        result = self._pipeline.run(
            markdown_text=text,
            metadata=metadata,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            show_progress=show_progress,
        )
        logger.info("[service] pipeline.run DONE elapsed=%.2fs", time.perf_counter() - t0)

        # (4) 後処理 Cypher でメタデータノード作成
        if meta:
            self._merge_metadata_nodes(meta)

        return result

    def _merge_metadata_nodes(self, meta: FrontmatterMeta) -> None:
        """Frontmatter メタデータを LlamaIndex 経由で Neo4j ノードとして upsert する

        LlamaIndex の upsert_nodes() を使うことで、グラフストアの実装に依存せず
        :Domain / :Tag / :SourceDocument ノードを冪等に作成する。

        Args:
            meta: パース済み Frontmatter メタデータ
        """
        now = datetime.now(timezone.utc).isoformat()

        nodes: list[EntityNode] = [
            EntityNode(
                label="Domain",
                name=meta.domain,
            ),
            EntityNode(
                label="SourceDocument",
                name=meta.source_file,
                properties={
                    "created_at": meta.created_at,
                    "updated_at": now,
                },
            ),
            *[EntityNode(label="Tag", name=tag) for tag in meta.tags],
        ]

        self._store.graph_store.upsert_nodes(cast(List[LabelledNode], nodes))
        logger.info(
            "[service] upsert_nodes :Domain=%s :SourceDocument=%s :Tag=%s",
            meta.domain,
            meta.source_file,
            meta.tags,
        )

    def _index_xml(self, text: str, doc_id: str | None) -> PropertyGraphIndex:
        # TODO: XML 形式のインデキシングを実装する
        raise NotImplementedError("XML-prefixed documents are not yet supported")

    def get_index(self) -> PropertyGraphIndex:
        """Neo4j に保存済みのインデックスを取得する"""
        return self._store.get_index()
