"""Gemini API LLMクライアント"""

import os
from typing import Type, TypeVar

from google import genai
from google.genai import types as genai_types
from pydantic import BaseModel

from lakda.llm.base import BaseLlmClient
from lakda.llm.exceptions import (
    LlmAuthenticationError,
    LlmConnectionError,
    LlmRateLimitError,
    LlmResponseParseError,
)

T = TypeVar("T", bound=BaseModel)


class GeminiLlmClient(BaseLlmClient):
    """Gemini API クライアント

    Attributes:
        client: Gemini APIクライアントインスタンス
        model: 使用するGeminiモデル名
        temperature: 応答の多様性を制御する温度パラメータ
        max_tokens: 生成される応答の最大トークン数
        top_p: nucleus samplingのパラメータ
        top_k: top-k samplingのパラメータ
    """

    def __init__(
        self,
        api_key: str | None = None,
        model: str = "gemini-2.5-flash-lite",
        temperature: float = 0.0,
        max_tokens: int = 8192,
        top_p: float = 0.95,
        top_k: int = 20,
    ) -> None:
        """GeminiLlmClientを初期化する

        Args:
            api_key: Gemini APIキー。Noneの場合は環境変数から取得
            model: 使用するGeminiモデル名
            temperature: 応答の多様性を制御する温度パラメータ (0.0-2.0)
            max_tokens: 生成される応答の最大トークン数
            top_p: nucleus samplingのパラメータ (0.0-1.0)
            top_k: top-k samplingのパラメータ
        """
        self._api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=self._api_key)
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.top_p = top_p
        self.top_k = top_k

    def generate_response(self, prompt: str, response_model: Type[T]) -> T:
        """プロンプトに基づいてGemini APIからレスポンスを生成する

        Args:
            prompt: LLMに送信する入力プロンプト
            response_model: レスポンスをパースするPydanticモデルクラス

        Returns:
            response_modelのインスタンス

        Raises:
            LlmAuthenticationError: APIキーが無効な場合
            LlmRateLimitError: レートリミットを超過した場合
            LlmConnectionError: 接続に失敗した場合
            LlmResponseParseError: レスポンスのパースに失敗した場合
        """
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=genai_types.Part.from_text(text=prompt),
                config=genai_types.GenerateContentConfig(
                    temperature=self.temperature,
                    top_p=self.top_p,
                    top_k=self.top_k,
                    max_output_tokens=self.max_tokens,
                    response_mime_type="application/json",
                ),
            )
            response_text = response.text
            if response_text is None:
                raise LlmResponseParseError("レスポンスにテキストが含まれていません")
            return response_model.model_validate_json(response_text)

        except Exception as e:
            error_name = type(e).__name__
            error_str = str(e).lower()

            # 認証エラー
            if "unauthenticated" in error_name.lower() or "unauthenticated" in error_str:
                raise LlmAuthenticationError(f"認証エラー: {e}") from e

            # レートリミット
            if "resourceexhausted" in error_name.lower() or "quota" in error_str:
                raise LlmRateLimitError(f"レートリミット超過: {e}") from e

            # パースエラー
            if "ValidationError" in error_name or "JSONDecodeError" in error_name:
                raise LlmResponseParseError(f"レスポンスパースエラー: {e}") from e

            # LLMエラーは再送出
            if "Llm" in error_name:
                raise

            raise LlmConnectionError(f"予期しないエラー: {e}") from e

    def health_check(self) -> bool:
        """Gemini APIの接続状態を確認する

        Returns:
            接続が正常な場合はTrue、そうでない場合はFalse
        """
        try:
            # モデル一覧を取得して接続を確認
            list(self.client.models.list())
            return True
        except Exception:
            return False

    def close(self) -> None:
        """Geminiクライアントをクローズする"""
        if hasattr(self.client, "close"):
            self.client.close()
