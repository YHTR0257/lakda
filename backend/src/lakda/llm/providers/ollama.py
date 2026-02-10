"""Ollama LLMクライアント（LlamaIndex版）"""

import os

import httpx
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.llms.ollama import Ollama

from lakda.llm.base import LlamaIndexLlmClient


class OllamaLlmClient(LlamaIndexLlmClient):
    """Ollama APIクライアント

    ローカルまたはDockerコンテナで動作するOllamaサーバーと通信します。

    Attributes:
        base_url: OllamaサーバーのベースURL
        model: 使用するOllamaモデル名
        request_timeout: リクエストタイムアウト秒数
        temperature: 応答の多様性を制御する温度パラメータ
    """

    def __init__(
        self,
        base_url: str | None = None,
        model: str = "llama3.2",
        request_timeout: float = 120.0,
        temperature: float = 0.0,
        json_mode: bool = True,
    ) -> None:
        """OllamaLlmClientを初期化する

        Args:
            base_url: OllamaサーバーのベースURL。Noneの場合は環境変数から取得
            model: 使用するOllamaモデル名
            request_timeout: リクエストタイムアウト秒数
            temperature: 応答の多様性を制御する温度パラメータ (0.0-1.0)
            json_mode: JSONモードを有効にするかどうか
        """
        self._base_url = base_url or os.getenv("OLLAMA_URL", "http://localhost:11434")
        llm = Ollama(
            base_url=self._base_url,
            model=model,
            request_timeout=request_timeout,
            temperature=temperature,
            json_mode=json_mode,
        )
        super().__init__(llm)

    def health_check(self) -> bool:
        """Ollama APIの接続状態を確認する

        Returns:
            接続が正常な場合はTrue、そうでない場合はFalse
        """
        try:
            with httpx.Client(timeout=10) as client:
                resp = client.get(f"{self._base_url}/api/tags")
                return resp.status_code == 200
        except Exception:
            return False


class OllamaEmbeddingClient:
    """Ollama 埋め込みモデルクライアント

    OllamaEmbedding (LlamaIndex) のラッパーです。
    Settings.embed_model に設定して使用します。

    Attributes:
        base_url: OllamaサーバーのベースURL
        model_name: 使用する埋め込みモデル名
    """

    def __init__(
        self,
        base_url: str | None = None,
        model_name: str = "bge-m3",
        request_timeout: float = 120.0,
    ) -> None:
        """OllamaEmbeddingClientを初期化する

        Args:
            base_url: OllamaサーバーのベースURL。Noneの場合は環境変数から取得
            model_name: 使用する埋め込みモデル名
            request_timeout: リクエストタイムアウト秒数
        """
        self._base_url = base_url or os.getenv("OLLAMA_URL", "http://localhost:11434")
        self._embed_model = OllamaEmbedding(
            model_name=model_name,
            base_url=self._base_url,
            request_timeout=request_timeout,
        )

    @property
    def embed_model(self) -> OllamaEmbedding:
        """LlamaIndex OllamaEmbedding インスタンスを取得する

        Returns:
            OllamaEmbeddingインスタンス
        """
        return self._embed_model

    @property
    def model_name(self) -> str:
        """使用中のモデル名を取得する"""
        return self._embed_model.model_name

    def health_check(self) -> bool:
        """Ollama APIの接続状態を確認する

        Returns:
            接続が正常な場合はTrue、そうでない場合はFalse
        """
        try:
            with httpx.Client(timeout=10) as client:
                resp = client.get(f"{self._base_url}/api/tags")
                return resp.status_code == 200
        except Exception:
            return False
