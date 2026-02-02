"""LLMクライアント接続テスト

各LLMプロバイダーへの接続をテストします。
APIキーが設定されていない場合はスキップされます。
"""

import os

import pytest
from pydantic import BaseModel

from lakda.llm.anthropic import AnthropicLlmClient
from lakda.llm.gemini import GeminiLlmClient
from lakda.llm.ollama import OllamaLlmClient
from lakda.llm.open_router import OpenRouterLlmClient


class SimpleResponse(BaseModel):
    """テスト用のシンプルなレスポンスモデル"""

    message: str


# 環境変数の存在チェック
has_gemini_key = os.getenv("GEMINI_API_KEY") is not None
has_anthropic_key = os.getenv("ANTHROPIC_API_KEY") is not None
has_openrouter_key = os.getenv("OPENROUTER_API_KEY") is not None


@pytest.mark.llm_api
@pytest.mark.skipif(not has_gemini_key, reason="GEMINI_API_KEY not set")
class TestGeminiClient:
    """Gemini APIクライアントのテスト"""

    def test_health_check(self):
        """ヘルスチェックのテスト"""
        client = GeminiLlmClient(model="gemini-2.5-flash-lite")
        assert client.health_check() is True
        client.close()

    def test_generate_response(self):
        """レスポンス生成のテスト"""
        client = GeminiLlmClient(model="gemini-2.5-flash-lite")
        response = client.generate_response(
            prompt='Return JSON: {"message": "Hello from Gemini"}',
            response_model=SimpleResponse,
        )
        assert response is not None
        assert isinstance(response, SimpleResponse)
        assert response.message is not None
        client.close()


# @pytest.mark.llm_api
# @pytest.mark.skipif(not has_anthropic_key, reason="ANTHROPIC_API_KEY not set")
# class TestAnthropicClient:
#     """Anthropic Claude APIクライアントのテスト"""

#     def test_health_check(self):
#         """ヘルスチェックのテスト"""
#         client = AnthropicLlmClient(model="claude-3-5-haiku-20241022")
#         assert client.health_check() is True

#     def test_generate_response(self):
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

    def test_health_check(self):
        """ヘルスチェックのテスト"""
        client = OpenRouterLlmClient(model="openai/gpt-oss-120b:free")
        assert client.health_check() is True

    def test_generate_response(self):
        """レスポンス生成のテスト"""
        client = OpenRouterLlmClient(model="openai/gpt-oss-120b:free")
        response = client.generate_response(
            prompt='Return only JSON without markdown: {"message": "Hello from OpenRouter"}',
            response_model=SimpleResponse,
        )
        assert response is not None
        assert isinstance(response, SimpleResponse)
        assert response.message is not None


has_ollama_url = os.getenv("OLLAMA_URL") is not None


@pytest.mark.llm_api
@pytest.mark.skipif(not has_ollama_url, reason="OLLAMA_URL not set")
class TestOllamaClient:
    """Ollama APIクライアントのテスト"""

    def test_health_check(self):
        """ヘルスチェックのテスト"""
        client = OllamaLlmClient(model="llama3.1:8b")
        assert client.health_check() is True

    def test_generate_response(self):
        """レスポンス生成のテスト"""
        client = OllamaLlmClient(model="llama3.1:8b")
        response = client.generate_response(
            prompt='Return only JSON: {"message": "Hello from Ollama"}',
            response_model=SimpleResponse,
        )
        assert response is not None
        assert isinstance(response, SimpleResponse)
        assert response.message is not None
