"""Ollama LLMクライアント"""

import os
from typing import Type, TypeVar

import httpx
from pydantic import BaseModel

from lakda.llm.base import BaseLlmClient
from lakda.llm.exceptions import (
    LlmConnectionError,
    LlmResponseParseError,
    LlmTimeoutError,
)

T = TypeVar("T", bound=BaseModel)


class OllamaLlmClient(BaseLlmClient):
    """Ollama APIクライアント

    ローカルまたはDockerコンテナで動作するOllamaサーバーと通信します。

    Attributes:
        base_url: OllamaサーバーのベースURL
        model: 使用するOllamaモデル名
        timeout: リクエストタイムアウト秒数
        temperature: 応答の多様性を制御する温度パラメータ
    """

    def __init__(
        self,
        base_url: str | None = None,
        model: str = "llama3.2",
        timeout: int = 120,
        temperature: float = 0.0,
        max_tokens: int = 2048,
    ) -> None:
        """OllamaLlmClientを初期化する

        Args:
            base_url: OllamaサーバーのベースURL。Noneの場合は環境変数から取得
            model: 使用するOllamaモデル名
            timeout: リクエストタイムアウト秒数
            temperature: 応答の多様性を制御する温度パラメータ (0.0-1.0)
            max_tokens: 生成される応答の最大トークン数
        """
        _base_url = base_url or os.getenv("OLLAMA_URL", "http://localhost:11434")
        self.base_url = _base_url.rstrip("/")
        self.model = model
        self.timeout = timeout
        self.temperature = temperature
        self.max_tokens = max_tokens
        self._client = httpx.Client(timeout=timeout)

    def generate_response(self, prompt: str, response_model: Type[T]) -> T:
        """プロンプトに基づいてOllama APIからレスポンスを生成する

        Args:
            prompt: LLMに送信する入力プロンプト
            response_model: レスポンスをパースするPydanticモデルクラス

        Returns:
            response_modelのインスタンス

        Raises:
            LlmConnectionError: 接続に失敗した場合
            LlmTimeoutError: タイムアウトした場合
            LlmResponseParseError: レスポンスのパースに失敗した場合
        """
        try:
            response = self._client.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "format": "json",
                    "options": {
                        "temperature": self.temperature,
                        "num_predict": self.max_tokens,
                    },
                },
            )

            if response.status_code == 404:
                error_data = response.json()
                raise LlmConnectionError(
                    f"モデルが見つかりません: {error_data.get('error', 'unknown')}"
                )

            response.raise_for_status()
            data = response.json()
            response_text = data.get("response", "")
            return response_model.model_validate_json(response_text)

        except httpx.ConnectError as e:
            raise LlmConnectionError(f"接続エラー: {e}") from e
        except httpx.TimeoutException as e:
            raise LlmTimeoutError(f"タイムアウト: {e}") from e
        except httpx.HTTPStatusError as e:
            raise LlmConnectionError(f"HTTPエラー: {e}") from e
        except (LlmConnectionError, LlmTimeoutError, LlmResponseParseError):
            raise
        except Exception as e:
            if "ValidationError" in type(e).__name__ or "JSONDecodeError" in type(
                e
            ).__name__:
                raise LlmResponseParseError(f"レスポンスパースエラー: {e}") from e
            raise LlmConnectionError(f"予期しないエラー: {e}") from e

    def health_check(self) -> bool:
        """Ollama APIの接続状態を確認する

        Returns:
            接続が正常な場合はTrue、そうでない場合はFalse
        """
        try:
            response = self._client.get(f"{self.base_url}/api/tags")
            return response.status_code == 200
        except Exception:
            return False

    def __del__(self) -> None:
        """クライアントをクリーンアップする"""
        if hasattr(self, "_client"):
            self._client.close()
