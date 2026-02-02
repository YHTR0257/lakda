"""Anthropic Claude LLMクライアント"""

import os
from typing import Type, TypeVar

import anthropic
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


class AnthropicLlmClient(BaseLlmClient):
    """Anthropic Claude APIクライアント

    Attributes:
        client: Anthropic APIクライアントインスタンス
        model: 使用するClaudeモデル名
        max_tokens: 生成される応答の最大トークン数
        temperature: 応答の多様性を制御する温度パラメータ
    """

    def __init__(
        self,
        api_key: str | None = None,
        model: str = "claude-3-5-sonnet-20241022",
        max_tokens: int = 4096,
        temperature: float = 0.0,
    ) -> None:
        """AnthropicLlmClientを初期化する

        Args:
            api_key: Anthropic APIキー。Noneの場合は環境変数から取得
            model: 使用するClaudeモデル名
            max_tokens: 生成される応答の最大トークン数
            temperature: 応答の多様性を制御する温度パラメータ (0.0-1.0)
        """
        self._api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.client = anthropic.Anthropic(api_key=self._api_key)
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature

    def generate_response(self, prompt: str, response_model: Type[T]) -> T:
        """プロンプトに基づいてClaude APIからレスポンスを生成する

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
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                messages=[{"role": "user", "content": prompt}],
            )
            # TextBlockからテキストを取得
            content_block = response.content[0]
            if hasattr(content_block, "text"):
                response_text = content_block.text
            else:
                raise LlmResponseParseError("レスポンスにテキストが含まれていません")
            return response_model.model_validate_json(response_text)

        except anthropic.AuthenticationError as e:
            raise LlmAuthenticationError(f"認証エラー: {e}") from e
        except anthropic.RateLimitError as e:
            raise LlmRateLimitError(f"レートリミット超過: {e}") from e
        except anthropic.APITimeoutError as e:
            raise LlmTimeoutError(f"タイムアウト: {e}") from e
        except anthropic.APIConnectionError as e:
            raise LlmConnectionError(f"接続エラー: {e}") from e
        except (LlmAuthenticationError, LlmRateLimitError, LlmTimeoutError, LlmConnectionError, LlmResponseParseError):
            raise
        except Exception as e:
            if "ValidationError" in type(e).__name__ or "JSONDecodeError" in type(
                e
            ).__name__:
                raise LlmResponseParseError(f"レスポンスパースエラー: {e}") from e
            raise LlmConnectionError(f"予期しないエラー: {e}") from e

    def health_check(self) -> bool:
        """Anthropic APIの接続状態を確認する

        Returns:
            接続が正常な場合はTrue、そうでない場合はFalse
        """
        try:
            # 簡単なリクエストを送信して接続を確認
            self.client.messages.create(
                model=self.model,
                max_tokens=10,
                messages=[{"role": "user", "content": "ping"}],
            )
            return True
        except Exception:
            return False
