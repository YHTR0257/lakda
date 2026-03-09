"""llama.cpp サーバー LLM/埋め込みクライアント（OpenAI互換API版）"""

import os

import httpx
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai_like import OpenAILike

from lakda.llm.base import LlamaIndexLlmClient


class LlamaCppLlmClient(LlamaIndexLlmClient):
    """llama.cpp LLMクライアント（OpenAI互換API）

    OpenAI互換APIを提供するllama.cppサーバーと通信します。

    Attributes:
        base_url: llama.cppサーバーのベースURL
        model: 使用するモデル名
        request_timeout: リクエストタイムアウト秒数
        temperature: 応答の多様性を制御する温度パラメータ
    """

    def __init__(
        self,
        base_url: str | None = None,
        model: str = "hf.co/unsloth/Qwen3.5-9B-GGUF:IQ4_NL",
        request_timeout: float = 120.0,
        temperature: float = 0.0,
        json_mode: bool = True,
    ) -> None:
        """LlamaCppLlmClientを初期化する

        Args:
            base_url: llama.cppサーバーのベースURL。Noneの場合は環境変数から取得
            model: 使用するモデル名
            request_timeout: リクエストタイムアウト秒数
            temperature: 応答の多様性を制御する温度パラメータ (0.0-1.0)
            json_mode: JSONモードを有効にするかどうか
        """
        self._base_url = base_url or os.getenv("LLAMACPP_LLM_URL", "http://localhost:11406")
        llm = OpenAILike(
            api_base=f"{self._base_url}/v1",
            api_key="sk-no-key-required",
            model=model,
            timeout=request_timeout,
            temperature=temperature,
            is_chat_model=True,
            is_function_calling_model=False,
        )
        super().__init__(llm)

    def health_check(self) -> bool:
        """llama.cpp サーバーの接続状態を確認する

        Returns:
            接続が正常な場合はTrue、そうでない場合はFalse
        """
        try:
            with httpx.Client(timeout=10) as client:
                resp = client.get(f"{self._base_url}/health")
                return resp.status_code == 200
        except Exception:
            return False


class LlamaCppEmbeddingClient:
    """llama.cpp 埋め込みモデルクライアント（OpenAI互換API）

    OpenAI互換APIを提供するllama.cppサーバーの埋め込みエンドポイントと通信します。
    Settings.embed_model に設定して使用します。

    Attributes:
        base_url: llama.cppサーバーのベースURL
        model_name: 使用する埋め込みモデル名
    """

    def __init__(
        self,
        base_url: str | None = None,
        model_name: str = "bge-m3",
        request_timeout: float = 120.0,
    ) -> None:
        """LlamaCppEmbeddingClientを初期化する

        Args:
            base_url: llama.cppサーバーのベースURL。Noneの場合は環境変数から取得
            model_name: 使用する埋め込みモデル名
            request_timeout: リクエストタイムアウト秒数
        """
        self._base_url = base_url or os.getenv("LLAMACPP_EMBEDDING_URL", "http://localhost:11407")
        self._model_name = model_name
        self._embed_model = OpenAIEmbedding(
            api_base=f"{self._base_url}/v1",
            api_key="sk-no-key-required",
            model_name=model_name,
            timeout=request_timeout,
        )

    @property
    def embed_model(self) -> OpenAIEmbedding:
        """LlamaIndex OpenAIEmbedding インスタンスを取得する

        Returns:
            OpenAIEmbeddingインスタンス
        """
        return self._embed_model

    @property
    def model_name(self) -> str:
        """使用中のモデル名を取得する"""
        return self._model_name

    def health_check(self) -> bool:
        """llama.cpp 埋め込みサーバーの接続状態を確認する

        Returns:
            接続が正常な場合はTrue、そうでない場合はFalse
        """
        try:
            with httpx.Client(timeout=10) as client:
                resp = client.get(f"{self._base_url}/health")
                return resp.status_code == 200
        except Exception:
            return False
