"""OpenRouter LLMクライアント（LlamaIndex版）"""

import os

from llama_index.llms.openrouter import OpenRouter

from lakda.llm.base import LlamaIndexLlmClient


class OpenRouterLlmClient(LlamaIndexLlmClient):
    """OpenRouter APIクライアント

    Attributes:
        model: 使用するモデル名
        temperature: 応答の多様性を制御する温度パラメータ
        max_tokens: 生成される応答の最大トークン数
    """

    def __init__(
        self,
        api_key: str | None = None,
        model: str = "google/gemma-3-27b-it:free",
        temperature: float = 0.0,
        max_tokens: int = 4096,
    ) -> None:
        """OpenRouterLlmClientを初期化する

        Args:
            api_key: OpenRouter APIキー。Noneの場合は環境変数から取得
            model: 使用するモデル名（例: google/gemma-3-27b-it:free）
            temperature: 応答の多様性を制御する温度パラメータ (0.0-2.0)
            max_tokens: 生成される応答の最大トークン数
        """
        llm = OpenRouter(
            api_key=api_key or os.getenv("OPENROUTER_API_KEY"),
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        super().__init__(llm)

    def health_check(self) -> bool:
        """OpenRouter APIの接続状態を確認する

        Returns:
            接続が正常な場合はTrue、そうでない場合はFalse
        """
        try:
            self._llm.complete("ping")
            return True
        except Exception:
            return False
