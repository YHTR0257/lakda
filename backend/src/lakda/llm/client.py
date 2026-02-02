"""LLMクライアントファクトリー・マネージャー"""

from enum import Enum
from typing import Type, TypeVar

from pydantic import BaseModel

from lakda.llm.base import BaseLlmClient
from lakda.llm.exceptions import LlmConnectionError

T = TypeVar("T", bound=BaseModel)


class LlmProvider(str, Enum):
    """サポートされているLLMプロバイダー"""

    ANTHROPIC = "anthropic"
    OLLAMA = "ollama"
    GEMINI = "gemini"
    OPENROUTER = "openrouter"


class LlmClientFactory:
    """LLMクライアントのファクトリークラス

    プロバイダー名に基づいて適切なLLMクライアントを生成します。
    """

    @staticmethod
    def create(provider: LlmProvider | str, **kwargs) -> BaseLlmClient:
        """指定されたプロバイダーのLLMクライアントを生成する

        Args:
            provider: LLMプロバイダー名
            **kwargs: クライアント固有の設定パラメータ

        Returns:
            BaseLlmClientのインスタンス

        Raises:
            ValueError: サポートされていないプロバイダーの場合
        """
        if isinstance(provider, str):
            provider = LlmProvider(provider.lower())

        if provider == LlmProvider.ANTHROPIC:
            from lakda.llm.anthropic import AnthropicLlmClient

            return AnthropicLlmClient(**kwargs)

        elif provider == LlmProvider.OLLAMA:
            from lakda.llm.ollama import OllamaLlmClient

            return OllamaLlmClient(**kwargs)

        elif provider == LlmProvider.GEMINI:
            from lakda.llm.gemini import GeminiLlmClient

            return GeminiLlmClient(**kwargs)

        elif provider == LlmProvider.OPENROUTER:
            from lakda.llm.open_router import OpenRouterLlmClient

            return OpenRouterLlmClient(**kwargs)

        else:
            raise ValueError(f"サポートされていないプロバイダー: {provider}")


class LlmClientManager:
    """複数のLLMクライアントを管理するマネージャークラス

    複数のLLMプロバイダーを登録し、切り替えて使用することができます。
    """

    def __init__(self) -> None:
        """LlmClientManagerを初期化する"""
        self._clients: dict[str, BaseLlmClient] = {}
        self._current_provider: str | None = None

    def register(
        self, provider: LlmProvider | str, client: BaseLlmClient | None = None, **kwargs
    ) -> None:
        """LLMクライアントを登録する

        Args:
            provider: LLMプロバイダー名
            client: 既存のクライアントインスタンス（Noneの場合は自動生成）
            **kwargs: クライアント生成時の設定パラメータ
        """
        provider_key = (
            provider.value if isinstance(provider, LlmProvider) else provider.lower()
        )

        if client is None:
            client = LlmClientFactory.create(provider, **kwargs)

        self._clients[provider_key] = client

        # 最初に登録されたクライアントをデフォルトとして設定
        if self._current_provider is None:
            self._current_provider = provider_key

    def select(self, provider: LlmProvider | str) -> None:
        """使用するLLMプロバイダーを選択する

        Args:
            provider: 選択するLLMプロバイダー名

        Raises:
            ValueError: 登録されていないプロバイダーの場合
        """
        provider_key = (
            provider.value if isinstance(provider, LlmProvider) else provider.lower()
        )

        if provider_key not in self._clients:
            raise ValueError(f"プロバイダー '{provider_key}' は登録されていません")

        self._current_provider = provider_key

    def get_current_client(self) -> BaseLlmClient:
        """現在選択されているLLMクライアントを取得する

        Returns:
            現在選択されているBaseLlmClientのインスタンス

        Raises:
            LlmConnectionError: クライアントが登録されていない場合
        """
        if self._current_provider is None or self._current_provider not in self._clients:
            raise LlmConnectionError("LLMクライアントが登録されていません")

        return self._clients[self._current_provider]

    def generate_response(self, prompt: str, response_model: Type[T]) -> T:
        """現在選択されているクライアントでレスポンスを生成する

        Args:
            prompt: LLMに送信する入力プロンプト
            response_model: レスポンスをパースするPydanticモデルクラス

        Returns:
            response_modelのインスタンス
        """
        client = self.get_current_client()
        return client.generate_response(prompt, response_model)

    def health_check(self, provider: LlmProvider | str | None = None) -> bool:
        """指定されたプロバイダー（またはカレント）のヘルスチェックを実行する

        Args:
            provider: チェックするプロバイダー名（Noneの場合は現在のプロバイダー）

        Returns:
            接続が正常な場合はTrue、そうでない場合はFalse
        """
        if provider is None:
            client = self.get_current_client()
        else:
            provider_key = (
                provider.value if isinstance(provider, LlmProvider) else provider.lower()
            )
            if provider_key not in self._clients:
                return False
            client = self._clients[provider_key]

        return client.health_check()

    def list_providers(self) -> list[dict]:
        """登録されているプロバイダーの一覧を取得する

        Returns:
            プロバイダー情報のリスト
        """
        providers = []
        for provider_key, client in self._clients.items():
            providers.append(
                {
                    "provider": provider_key,
                    "model": getattr(client, "model", "unknown"),
                    "is_current": provider_key == self._current_provider,
                    "available": client.health_check(),
                }
            )
        return providers

    @property
    def current_provider(self) -> str | None:
        """現在選択されているプロバイダー名を取得する"""
        return self._current_provider
