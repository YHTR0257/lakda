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
        # GoogleGenAI() はコンストラクタ内で models.get() を呼びAPIに接続するため、
        # 無効なキー・モデル名の場合にここで例外が発生する。try-except で吸収する。
        # 空文字列キーは GoogleGenAI 内部で env var にフォールバックされるため事前に弾く。
        resolved_key = api_key if api_key is not None else os.getenv("GOOGLE_API_KEY")
        if not resolved_key:
            self._llm = None
            return
        try:
            llm = GoogleGenAI(
                api_key=resolved_key,
                model=model,
                temperature=temperature,
                max_output_tokens=max_output_tokens,
            )
            super().__init__(llm)
        except Exception:
            self._llm = None

    def health_check(self) -> bool:
        """Gemini APIの接続状態を確認する

        Returns:
            接続が正常な場合はTrue、そうでない場合はFalse
        """
        if self._llm is None:
            return False
        try:
            self._llm.complete("ping")
            return True
        except Exception:
            return False
