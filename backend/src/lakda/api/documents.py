"""ドキュメント変換 API エンドポイント"""

import asyncio
import logging
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile, status
from llama_index.core import Settings

from lakda.api.dependencies import get_graph_store_manager, get_llm_manager
from lakda.db import Neo4jGraphStoreManager
from lakda.llm.client import LlmClientManager
from lakda.models.schemas.documents import ConvertResponse, FrontmatterMeta
from lakda.services.documents.cleaner import MarkdownCleaner
from lakda.services.documents.converter import DocumentConverter, FrontmatterConverter
from lakda.services.index.service import IndexService

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/documents",
    tags=["documents"],
)

_doc_converter = DocumentConverter()
_fm_converter = FrontmatterConverter()
_cleaner = MarkdownCleaner()


@router.post("/upload", response_model=ConvertResponse, status_code=status.HTTP_200_OK)
async def upload_document(
    file: UploadFile,
    domain: str = Form("general"),
    tags: list[str] = Form([]),
    title: str | None = Form(None),
    auto_index: bool = Form(False),
    clean: bool = Form(False),
    graph_store_manager: Neo4jGraphStoreManager = Depends(get_graph_store_manager),
    llm_manager: LlmClientManager = Depends(get_llm_manager),
) -> ConvertResponse:
    """ドキュメントをアップロードして Markdown に変換し、Frontmatter を付与する

    対応フォーマット: JSON / PDF / JPEG / PNG

    - 非対応フォーマットは 422 を返す
    - 変換失敗時は 500 と追跡可能なログを出力する
    - clean=True の場合、ルールベース + LLM チャンク整形を実行する
    - auto_index=True の場合、変換後に index API 経由で Neo4j に格納する
    """
    doc_id = str(uuid4())
    filename = file.filename or "unknown"
    logger.info("[documents] upload START doc=%s file=%s", doc_id, filename)

    file_bytes = await file.read()

    # (1) フォーマット判定
    try:
        mime = _doc_converter.detect_format(file_bytes, filename)
    except ValueError as e:
        logger.warning("[documents] unsupported format doc=%s: %s", doc_id, e)
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))

    # (2) Markdown 変換
    try:
        markdown = _doc_converter.convert_to_markdown(file_bytes, mime)
    except RuntimeError as e:
        logger.error("[documents] conversion failed doc=%s: %s", doc_id, e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    # (2.5) Markdown 整形（clean=True の場合）
    if clean:
        llm = llm_manager.get_llm()
        logger.info("[documents] cleaning markdown doc=%s llm=%s", doc_id, llm is not None)
        try:
            markdown = await asyncio.to_thread(_cleaner.clean, markdown, llm)
        except Exception as e:
            logger.warning("[documents] cleaning failed doc=%s (proceeding without clean): %s", doc_id, e)

    # (3) Frontmatter 付与（FT04）
    meta = FrontmatterMeta(
        domain=domain,
        tags=tags,
        title=title or Path(filename).stem,
        created_at=datetime.now(timezone.utc).isoformat(),
        source_file=filename,
    )
    markdown = _fm_converter.add_frontmatter(markdown, meta)

    # (4) auto_index=True の場合、index サービス経由で Neo4j に格納
    indexed = False
    if auto_index:
        try:
            Settings.llm = llm_manager.get_llm()
            Settings.embed_model = llm_manager.get_embed_model()
            service = IndexService(graph_store_manager)
            await asyncio.to_thread(service.index, markdown_text=markdown, doc_id=doc_id)
            indexed = True
            logger.info("[documents] indexed doc=%s", doc_id)
        except Exception as e:
            logger.error("[documents] indexing failed doc=%s: %s", doc_id, e)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    logger.info("[documents] upload DONE doc=%s mime=%s indexed=%s", doc_id, mime, indexed)
    return ConvertResponse(doc_id=doc_id, markdown=markdown, format=mime, indexed=indexed)
