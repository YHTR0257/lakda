import asyncio
import logging
import time
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

from fastapi import APIRouter, Depends, HTTPException, status
from llama_index.core import Settings

from lakda.api.dependencies import get_graph_store_manager, get_llm_manager
from lakda.db import Neo4jGraphStoreManager
from lakda.llm.client import LlmClientManager
from lakda.models.schemas.index import GraphStatsResponse, IndexMarkdownRequest, IndexResponse, LlmHealthResponse, NodeLabelCount, RelTypeCount
from lakda.services.index.service import IndexService

router = APIRouter(
    prefix="/index",
    tags=["index"],
)


@router.get("/health", response_model=LlmHealthResponse, status_code=status.HTTP_200_OK)
async def check_llm_health(
    llm_manager: LlmClientManager = Depends(get_llm_manager),
) -> LlmHealthResponse:
    """LLM および Embedding サーバーの接続状態を確認する"""
    llm_ok = await asyncio.to_thread(llm_manager.health_check)
    embedding_ok = await asyncio.to_thread(llm_manager.health_check_embedding)
    return LlmHealthResponse(llm=llm_ok, embedding=embedding_ok, ok=llm_ok and embedding_ok)


@router.get("/stats", response_model=GraphStatsResponse, status_code=status.HTTP_200_OK)
async def get_graph_stats(
    graph_store_manager: Neo4jGraphStoreManager = Depends(get_graph_store_manager),
) -> GraphStatsResponse:
    """Neo4j グラフの統計情報（ノード数・関係数・ラベル内訳）を返す"""
    try:
        node_count, rel_count, nodes_by_label, rels_by_type, sample_nodes = await asyncio.gather(
            asyncio.to_thread(graph_store_manager.query, "MATCH (n) RETURN count(n) AS count"),
            asyncio.to_thread(graph_store_manager.query, "MATCH ()-[r]->() RETURN count(r) AS count"),
            asyncio.to_thread(graph_store_manager.query,
                "MATCH (n) UNWIND labels(n) AS label RETURN label, count(*) AS count ORDER BY count DESC"),
            asyncio.to_thread(graph_store_manager.query,
                "MATCH ()-[r]->() RETURN type(r) AS type, count(*) AS count ORDER BY count DESC"),
            asyncio.to_thread(graph_store_manager.query,
                "MATCH (n) RETURN labels(n) AS labels, properties(n) AS props LIMIT 10"),
        )
        return GraphStatsResponse(
            node_count=node_count[0]["count"],
            rel_count=rel_count[0]["count"],
            nodes_by_label=[NodeLabelCount(**r) for r in nodes_by_label],
            rels_by_type=[RelTypeCount(**r) for r in rels_by_type],
            sample_nodes=[{"labels": r["labels"], **r["props"]} for r in sample_nodes],
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post("/markdown", response_model=IndexResponse, status_code=status.HTTP_200_OK)
async def index_markdown(
    request: IndexMarkdownRequest,
    graph_store_manager: Neo4jGraphStoreManager = Depends(get_graph_store_manager),
    llm_manager: LlmClientManager = Depends(get_llm_manager),
) -> IndexResponse:
    """Markdown テキストを Neo4j PropertyGraphStore にインデキシングする"""
    doc_label = request.doc_id or "(no id)"
    logger.info("[index] START doc=%s text_len=%d", doc_label, len(request.markdown_text))
    t0 = time.perf_counter()
    try:
        Settings.llm = llm_manager.get_llm()
        Settings.embed_model = llm_manager.get_embed_model()
        logger.info("[index] LLM/Embed settings applied (%.2fs)", time.perf_counter() - t0)

        service = IndexService(graph_store_manager)
        await asyncio.to_thread(
            service.index,
            markdown_text=request.markdown_text,
            doc_id=request.doc_id,
            chunk_size=request.chunk_size,
            chunk_overlap=request.chunk_overlap,
        )
        elapsed = time.perf_counter() - t0
        logger.info("[index] DONE doc=%s elapsed=%.2fs", doc_label, elapsed)
        return IndexResponse(
            doc_id=request.doc_id,
            status="success",
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
    except Exception as e:
        logger.error("[index] FAILED doc=%s elapsed=%.2fs error=%s", doc_label, time.perf_counter() - t0, e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
