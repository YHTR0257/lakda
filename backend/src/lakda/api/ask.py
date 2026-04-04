from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse

from lakda.api.dependencies import get_graph_store_manager, get_llm_manager
from lakda.db import Neo4jGraphStoreManager
from lakda.llm.client import LlmClientManager
from lakda.models.schemas.ask import AnswerResponse, ChatRequest, ConfirmRequest
from lakda.services.ask.service import AskService

router = APIRouter(
    prefix="/ask",
    tags=["ask"],
)


@router.post("/confirm", response_model=AnswerResponse, status_code=status.HTTP_200_OK)
async def confirm_question(
    request: ConfirmRequest,
    graph_store_manager: Neo4jGraphStoreManager = Depends(get_graph_store_manager),
    llm_manager: LlmClientManager = Depends(get_llm_manager),
) -> AnswerResponse:
    """質問に対して Neo4j PropertyGraphStore を検索し、LLM で回答を生成する"""
    try:
        service = AskService(graph_store_manager, llm_manager)
        return service.answer(
            session_id=request.session_id,
            question=request.confirmed_question,
            max_results=request.options.max_results or 3,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post("/chat", status_code=status.HTTP_200_OK)
async def chat_question(
    request: ChatRequest,
    graph_store_manager: Neo4jGraphStoreManager = Depends(get_graph_store_manager),
    llm_manager: LlmClientManager = Depends(get_llm_manager),
) -> StreamingResponse:
    """質問に対して SSE ストリーミングで回答を生成する"""
    service = AskService(graph_store_manager, llm_manager)
    return StreamingResponse(
        service.astream_answer(
            session_id=request.session_id,
            question=request.question,
            max_results=request.options.max_results or 3,
        ),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
