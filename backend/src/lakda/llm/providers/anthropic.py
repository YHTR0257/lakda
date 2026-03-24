"""Anthropic Claude LLMクライアント（LlamaIndex版）"""

import os

from llama_index.llms.anthropic import Anthropic

from lakda.llm.base import LlamaIndexLlmClient


class AnthropicLlmClient(LlamaIndexLlmClient):
    """Anthropic Claude APIクライアント

    Attributes:
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
        llm = Anthropic(
            api_key=api_key or os.getenv("ANTHROPIC_API_KEY"),
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        super().__init__(llm)

    def health_check(self) -> bool:
        """Anthropic APIの接続状態を確認する

        Returns:
            接続が正常な場合はTrue、そうでない場合はFalse
        """
        try:
            self._llm.complete("ping")
            return True
        except Exception:
            return False
