"""Ask サービス - 質問応答のオーケストレーション"""

import datetime

from llama_index.core import Settings

from lakda.db import Neo4jGraphStoreManager
from lakda.llm.client import LlmClientManager
from lakda.models.schemas.ask import AnswerResponse, SourceItem
from lakda.services.ask.retrieval import AskRetrieval
from lakda.services.index.store import IndexStore


class AskService:
    """質問を受けて Neo4j PropertyGraphStore を検索し回答を生成するサービス

    使い方:
        manager = LlmClientManager()
        manager.register(provider="llamacpp", model="...")
        manager.register_embedding(provider="llamacpp", model_name="...")

        graph_store_manager = Neo4jGraphStoreManager()
        service = AskService(graph_store_manager, manager)
        response = service.answer(
            session_id="uuid-1234",
            question="AttributeError の原因は？",
            max_results=3,
        )
    """

    def __init__(
        self,
        graph_store_manager: Neo4jGraphStoreManager,
        llm_manager: LlmClientManager,
    ) -> None:
        """AskService を初期化する

        Args:
            graph_store_manager: Neo4j 接続マネージャー
            llm_manager: LLM クライアントマネージャー
        """
        self._store = IndexStore(graph_store_manager)
        self._llm_manager = llm_manager

    def answer(
        self,
        session_id: str,
        question: str,
        max_results: int = 3,
    ) -> AnswerResponse:
        """質問に対して Neo4j を検索し、LLM で回答を生成する

        Args:
            session_id: セッション識別子
            question: 質問テキスト
            max_results: 参照するソースノードの最大数

        Returns:
            AnswerResponse（回答テキスト・ソース情報・タイムスタンプ付き）
        """
        Settings.llm = self._llm_manager.get_llm()
        Settings.embed_model = self._llm_manager.get_embed_model()

        index = self._store.get_index()
        retrieval = AskRetrieval(index)
        response = retrieval.query(question, max_results=max_results)

        sources = []
        for node_with_score in response.source_nodes:
            node = node_with_score.node
            metadata = node.metadata
            sources.append(
                SourceItem(
                    file=metadata.get("doc_id", "unknown"),
                    snippet=node.get_content()[:300],
                    score=node_with_score.score or 0.0,
                )
            )

        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()

        return AnswerResponse(
            session_id=session_id,
            question=question,
            answer=str(response),
            sources=sources,
            timestamp=timestamp,
        )
