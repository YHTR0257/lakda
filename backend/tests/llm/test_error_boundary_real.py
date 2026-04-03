"""LLMクライアント エラー境界 実APIテスト

設定ミス（存在しないモデル名、空のAPIキー）が実APIで
LlmError サブクラスに変換されることを確認するテスト。

モックテスト（test_llm_clients_error.py）と異なり、実際のSDKが投げる例外が
map_llm_exceptions デコレータによって正しく変換されるかを検証する。
"""

import os

import pytest
from pydantic import BaseModel

from lakda.llm.exceptions import LlmError
from lakda.llm.providers.anthropic import AnthropicLlmClient
from lakda.llm.providers.google_genai import GoogleGenAILlmClient
from lakda.llm.providers.llamacpp import LlamaCppLlmClient
from lakda.llm.providers.openrouter import OpenRouterLlmClient


class SimpleResponse(BaseModel):
    """テスト用のシンプルなレスポンスモデル"""

    message: str


# 環境変数の存在チェック
has_google_key = os.getenv("GOOGLE_API_KEY") is not None
has_anthropic_key = os.getenv("ANTHROPIC_API_KEY") is not None
has_openrouter_key = os.getenv("OPENROUTER_API_KEY") is not None


def _is_llamacpp_reachable() -> bool:
    """llama.cpp LLMサーバーに接続可能か確認する"""
    url = os.getenv("LLAMACPP_LLM_URL")
    if not url:
        return False
    try:
        import httpx

        with httpx.Client(timeout=5) as client:
            resp = client.get(f"{url}/health")
            return resp.status_code == 200
    except Exception:
        return False


is_llamacpp_reachable = _is_llamacpp_reachable()


@pytest.mark.llm_api
class TestInvalidModelRealApi:
    """存在しないモデル名を指定した場合に LlmError が raise されることを確認するテスト

    各プロバイダーのSDKが返すエラーが map_llm_exceptions デコレータによって
    LlmError サブクラスに変換されることを実APIで検証する。
    """

    @pytest.mark.skipif(not has_google_key, reason="GOOGLE_API_KEY not set")
    def test_google_invalid_model(self) -> None:
        """Google GenAI: 存在しないモデル名で generate_response() が LlmError を raise する"""
        client = GoogleGenAILlmClient(model="gemini-nonexistent-model-xxx-9999")
        with pytest.raises(LlmError):
            client.generate_response(
                prompt='Return JSON: {"message": "test"}',
                response_model=SimpleResponse,
            )

    @pytest.mark.skipif(not has_anthropic_key, reason="ANTHROPIC_API_KEY not set")
    def test_anthropic_invalid_model(self) -> None:
        """Anthropic: 存在しないモデル名で generate_response() が LlmError を raise する"""
        client = AnthropicLlmClient(model="claude-nonexistent-model-xxx")
        with pytest.raises(LlmError):
            client.generate_response(
                prompt='Return only JSON without markdown: {"message": "test"}',
                response_model=SimpleResponse,
            )

    @pytest.mark.skipif(not has_openrouter_key, reason="OPENROUTER_API_KEY not set")
    def test_openrouter_invalid_model(self) -> None:
        """OpenRouter: 存在しないモデル名で generate_response() が LlmError を raise する"""
        client = OpenRouterLlmClient(model="nonexistent/model-xxx:free")
        with pytest.raises(LlmError):
            client.generate_response(
                prompt='Return only JSON without markdown: {"message": "test"}',
                response_model=SimpleResponse,
            )

    @pytest.mark.skipif(not is_llamacpp_reachable, reason="llama.cpp server is not reachable")
    @pytest.mark.xfail(
        strict=False,
        reason="llama.cpp は OpenAI 互換 API のため、無効なモデル名でもロード中のモデルで成功レスポンスを返す場合がある",
    )
    def test_llamacpp_invalid_model(self) -> None:
        """llama.cpp: 存在しないモデル名で generate_response() が何らかのエラーを raise する

        llama.cpp は OpenAI 互換 API であり、存在しないモデル名でも接続自体は成功する場合がある。
        サーバーの実装によって挙動が異なるため、LlmError または Exception を期待する。
        """
        client = LlamaCppLlmClient(model="nonexistent-model-xxx-9999")
        with pytest.raises(Exception):
            client.generate_response(
                prompt='Return only JSON: {"message": "test"}',
                response_model=SimpleResponse,
            )


@pytest.mark.llm_api
class TestEmptyApiKeyRealApi:
    """空文字列のAPIキーを渡した場合の動作確認テスト

    環境変数が空文字列として設定されていた場合（設定ミス）に
    health_check() が安全に False を返し、generate_response() が LlmError を raise することを確認する。
    実サーバーやAPIキーは不要（失敗することを期待する）。
    """

    def test_google_empty_api_key_health_check(self) -> None:
        """Google GenAI: 空のAPIキーで health_check() が False を返す（例外が漏れない）"""
        client = GoogleGenAILlmClient(api_key="")
        assert client.health_check() is False

    def test_anthropic_empty_api_key_health_check(self) -> None:
        """Anthropic: 空のAPIキーで health_check() が False を返す（例外が漏れない）"""
        client = AnthropicLlmClient(api_key="")
        assert client.health_check() is False

    def test_openrouter_empty_api_key_health_check(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """OpenRouter: 空のAPIキーで health_check() が False を返す（例外が漏れない）

        OpenRouterLlmClient.health_check() は os.getenv() を直接参照するため
        monkeypatch で環境変数を上書きしてテストする。
        """
        monkeypatch.setenv("OPENROUTER_API_KEY", "")
        client = OpenRouterLlmClient(api_key="")
        assert client.health_check() is False

    def test_google_empty_api_key_generate(self) -> None:
        """Google GenAI: 空のAPIキーで generate_response() が LlmError を raise する"""
        client = GoogleGenAILlmClient(api_key="")
        with pytest.raises(LlmError):
            client.generate_response(
                prompt='Return JSON: {"message": "test"}',
                response_model=SimpleResponse,
            )
