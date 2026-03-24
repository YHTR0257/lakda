"""LLMクライアント接続テスト

各LLMプロバイダーへの接続をテストします。
APIキーが設定されていない場合はスキップされます。
"""

import os

import pytest
from pydantic import BaseModel

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


@pytest.mark.llm_api
@pytest.mark.skipif(not has_google_key, reason="GOOGLE_API_KEY not set")
class TestGoogleGenAIClient:
    """Google GenAI APIクライアントのテスト"""

    def test_health_check(self) -> None:
        """ヘルスチェックのテスト"""
        client = GoogleGenAILlmClient(model="gemini-2.5-flash-lite")
        assert client.health_check() is True

    def test_generate_response(self) -> None:
        """レスポンス生成のテスト"""
        client = GoogleGenAILlmClient(model="gemini-2.5-flash-lite")
        response = client.generate_response(
            prompt='Return JSON: {"message": "Hello from Gemini"}',
            response_model=SimpleResponse,
        )
        assert response is not None
        assert isinstance(response, SimpleResponse)
        assert response.message is not None


# @pytest.mark.llm_api
# @pytest.mark.skipif(not has_anthropic_key, reason="ANTHROPIC_API_KEY not set")
# class TestAnthropicClient:
#     """Anthropic Claude APIクライアントのテスト"""

#     def test_health_check(self) -> None:
#         """ヘルスチェックのテスト"""
#         client = AnthropicLlmClient(model="claude-3-5-haiku-20241022")
#         assert client.health_check() is True

#     def test_generate_response(self) -> None:
#         """レスポンス生成のテスト"""
#         client = AnthropicLlmClient(model="claude-3-5-haiku-20241022")
#         response = client.generate_response(
#             prompt='Return only JSON without markdown: {"message": "Hello from Claude"}',
#             response_model=SimpleResponse,
#         )
#         assert response is not None
#         assert isinstance(response, SimpleResponse)
#         assert response.message is not None


@pytest.mark.llm_api
@pytest.mark.skipif(not has_openrouter_key, reason="OPENROUTER_API_KEY not set")
class TestOpenRouterClient:
    """OpenRouter APIクライアントのテスト"""

    def test_health_check(self) -> None:
        """ヘルスチェックのテスト"""
        client = OpenRouterLlmClient(model="openai/gpt-oss-120b:free")
        assert client.health_check() is True

    def test_generate_response(self) -> None:
        """レスポンス生成のテスト"""
        client = OpenRouterLlmClient(model="openai/gpt-oss-120b:free")
        response = client.generate_response(
            prompt='Return only JSON without markdown: {"message": "Hello from OpenRouter"}',
            response_model=SimpleResponse,
        )
        assert response is not None
        assert isinstance(response, SimpleResponse)
        assert response.message is not None


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
@pytest.mark.skipif(not is_llamacpp_reachable, reason="llama.cpp server is not reachable")
class TestLlamaCppClient:
    """llama.cpp APIクライアントのテスト"""

    def test_health_check(self) -> None:
        """ヘルスチェックのテスト"""
        client = LlamaCppLlmClient(model="hf.co/unsloth/Qwen3.5-9B-GGUF:IQ4_NL")
        assert client.health_check() is True

    def test_generate_response(self) -> None:
        """レスポンス生成のテスト"""
        client = LlamaCppLlmClient(model="hf.co/unsloth/Qwen3.5-9B-GGUF:IQ4_NL")
        response = client.generate_response(
            prompt='Return only JSON: {"message": "Hello from llama.cpp"}',
            response_model=SimpleResponse,
        )
        assert response is not None
        assert isinstance(response, SimpleResponse)
        assert response.message is not None
