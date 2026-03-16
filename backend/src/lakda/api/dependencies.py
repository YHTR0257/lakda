import os

from lakda.db import Neo4jGraphStoreManager
from lakda.llm.client import LlmClientManager

_graph_store_manager = Neo4jGraphStoreManager()

_llm_manager: LlmClientManager | None = None


def _build_llm_manager() -> LlmClientManager:
    manager = LlmClientManager()
    llm_model = os.getenv("LLAMACPP_LLM_MODEL", "hf.co/unsloth/Qwen3.5-9B-GGUF:IQ4_NL")
    embed_model = os.getenv("LLAMACPP_EMBEDDING_MODEL", "bge-m3")
    manager.register(provider="llamacpp", model=llm_model)
    manager.register_embedding(provider="llamacpp", model_name=embed_model)
    return manager


def get_graph_store_manager() -> Neo4jGraphStoreManager:
    """Neo4jGraphStoreManager を返す依存性注入関数"""
    return _graph_store_manager


def get_llm_manager() -> LlmClientManager:
    """LlmClientManager を返す依存性注入関数（シングルトン）"""
    global _llm_manager
    if _llm_manager is None:
        _llm_manager = _build_llm_manager()
    return _llm_manager
