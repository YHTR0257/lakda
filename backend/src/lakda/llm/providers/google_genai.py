"""Google GenAI (Gemini) LLMクライアント（LlamaIndex版）"""

import os

from llama_index.llms.google_genai import GoogleGenAI

from lakda.llm.base import LlamaIndexLlmClient


class GoogleGenAILlmClient(LlamaIndexLlmClient):
    """Google GenAI (Gemini) APIクライアント

    Attributes:
        model: 使用するGeminiモデル名
        temperature: 応答の多様性を制御する温度パラメータ
        max_output_tokens: 生成される応答の最大トークン数
    """

    def __init__(
        self,
        api_key: str | None = None,
        model: str = "gemini-2.5-flash-lite",
        temperature: float = 0.0,
        max_output_tokens: int = 8192,
    ) -> None:
        """GoogleGenAILlmClientを初期化する

        Args:
            api_key: Google API キー。Noneの場合は環境変数から取得
            model: 使用するGeminiモデル名
            temperature: 応答の多様性を制御する温度パラメータ (0.0-2.0)
            max_output_tokens: 生成される応答の最大トークン数
        """
        # 環境変数名: GOOGLE_API_KEY（LlamaIndexデフォルト）
        llm = GoogleGenAI(
            api_key=api_key or os.getenv("GOOGLE_API_KEY"),
            model=model,
            temperature=temperature,
            max_output_tokens=max_output_tokens,
        )
        super().__init__(llm)

    def health_check(self) -> bool:
        """Gemini APIの接続状態を確認する

        Returns:
            接続が正常な場合はTrue、そうでない場合はFalse
        """
        try:
            self._llm.complete("ping")
            return True
        except Exception:
            return False
