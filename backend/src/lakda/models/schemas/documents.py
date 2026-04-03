"""ドキュメント変換・メタデータ付与に関する Pydantic スキーマ"""

from pydantic import BaseModel


class FrontmatterMeta(BaseModel):
    """Markdown Frontmatter のメタデータスキーマ

    Attributes:
        domain: 検索ドメイン（Neo4j :Domain ノードに対応）
        tags: タグリスト（Neo4j :Tag ノードに対応）
        title: ドキュメントタイトル（未指定時は source_file のステム）
        created_at: 変換日時（ISO 8601）
        source_file: 元ファイル名（Neo4j :SourceDocument ノードに対応）
    """

    domain: str = "general"
    tags: list[str] = []
    title: str | None = None
    created_at: str
    source_file: str


class ConvertResponse(BaseModel):
    """ドキュメント変換 API のレスポンススキーマ

    Attributes:
        doc_id: 生成されたドキュメント識別子
        markdown: Frontmatter 付き Markdown テキスト
        format: 検出された MIME タイプ
        indexed: auto_index=True でインデキシング済みの場合 True
    """

    doc_id: str
    markdown: str
    format: str
    indexed: bool
