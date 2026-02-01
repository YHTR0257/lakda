"""OpenRouter LLMクライアント"""

import os
from typing import Type, TypeVar

from openai import OpenAI
from pydantic import BaseModel

from lakda.llm.base import BaseLlmClient
from lakda.llm.exceptions import (
    LlmAuthenticationError,
    LlmConnectionError,
    LlmRateLimitError,
    LlmResponseParseError,
    LlmTimeoutError,
)

T = TypeVar("T", bound=BaseModel)


class OpenRouterLlmClient(BaseLlmClient):
    """OpenRouter APIクライアント

    OpenAI互換APIを使用してOpenRouterにアクセスします。

    Attributes:
        client: OpenAI互換クライアントインスタンス
        model: 使用するモデル名
        temperature: 応答の多様性を制御する温度パラメータ
        max_tokens: 生成される応答の最大トークン数
    """

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str = "https://openrouter.ai/api/v1",
        model: str = "google/gemma-3-27b-it:free",
        temperature: float = 0.0,
        max_tokens: int = 4096,
        site_url: str | None = None,
        app_name: str | None = None,
    ) -> None:
        """OpenRouterLlmClientを初期化する

        Args:
            api_key: OpenRouter APIキー。Noneの場合は環境変数から取得
            base_url: OpenRouter APIのベースURL
            model: 使用するモデル名（例: google/gemma-3-27b-it:free）
            temperature: 応答の多様性を制御する温度パラメータ (0.0-2.0)
            max_tokens: 生成される応答の最大トークン数
            site_url: OpenRouterダッシュボードでの識別用URL
            app_name: OpenRouterダッシュボードでの識別用アプリ名
        """
        self._api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

        # 追加のヘッダーを設定
        default_headers = {}
        if site_url:
            default_headers["HTTP-Referer"] = site_url
        if app_name:
            default_headers["X-Title"] = app_name

        self.client = OpenAI(
            api_key=self._api_key,
            base_url=base_url,
            default_headers=default_headers if default_headers else None,
        )

    def generate_response(self, prompt: str, response_model: Type[T]) -> T:
        """プロンプトに基づいてOpenRouter APIからレスポンスを生成する

        Args:
            prompt: LLMに送信する入力プロンプト
            response_model: レスポンスをパースするPydanticモデルクラス

        Returns:
            response_modelのインスタンス

        Raises:
            LlmAuthenticationError: APIキーが無効な場合
            LlmRateLimitError: レートリミットを超過した場合
            LlmConnectionError: 接続に失敗した場合
            LlmTimeoutError: タイムアウトした場合
            LlmResponseParseError: レスポンスのパースに失敗した場合
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                response_format={"type": "json_object"},
            )
            response_text = response.choices[0].message.content
            if response_text is None:
                raise LlmResponseParseError("レスポンスにテキストが含まれていません")
            return response_model.model_validate_json(response_text)

        except Exception as e:
            error_name = type(e).__name__

            # OpenAI SDKの例外を処理
            if "AuthenticationError" in error_name:
                raise LlmAuthenticationError(f"認証エラー: {e}") from e
            if "RateLimitError" in error_name:
                raise LlmRateLimitError(f"レートリミット超過: {e}") from e
            if "APITimeoutError" in error_name:
                raise LlmTimeoutError(f"タイムアウト: {e}") from e
            if "APIConnectionError" in error_name:
                raise LlmConnectionError(f"接続エラー: {e}") from e
            if "NotFoundError" in error_name:
                raise LlmConnectionError(f"モデルが見つかりません: {e}") from e

            # パースエラー
            if "ValidationError" in error_name or "JSONDecodeError" in error_name:
                raise LlmResponseParseError(f"レスポンスパースエラー: {e}") from e

            # LLMエラーは再送出
            if "Llm" in error_name:
                raise

            raise LlmConnectionError(f"予期しないエラー: {e}") from e

    def health_check(self) -> bool:
        """OpenRouter APIの接続状態を確認する

        Returns:
            接続が正常な場合はTrue、そうでない場合はFalse
        """
        try:
            # モデル一覧を取得して接続を確認
            self.client.models.list()
            return True
        except Exception:
            return False
