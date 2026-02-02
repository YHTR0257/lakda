"""LLMクライアントの基底クラス"""

from abc import ABC, abstractmethod
from typing import Type, TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class BaseLlmClient(ABC):
    """LLMクライアントの抽象基底クラス

    すべてのLLMクライアントはこのクラスを継承し、
    generate_responseとhealth_checkメソッドを実装する必要があります。
    """

    @abstractmethod
    def generate_response(self, prompt: str, response_model: Type[T]) -> T:
        """プロンプトに基づいてLLMからレスポンスを生成する

        Args:
            prompt: LLMに送信する入力プロンプト
            response_model: レスポンスをパースするPydanticモデルクラス

        Returns:
            response_modelのインスタンス

        Raises:
            LlmAuthenticationError: 認証に失敗した場合
            LlmRateLimitError: レートリミットを超過した場合
            LlmConnectionError: 接続に失敗した場合
            LlmTimeoutError: タイムアウトした場合
            LlmResponseParseError: レスポンスのパースに失敗した場合
        """
        pass

    @abstractmethod
    def health_check(self) -> bool:
        """LLMサービスの接続状態を確認する

        Returns:
            接続が正常な場合はTrue、そうでない場合はFalse
        """
        pass
