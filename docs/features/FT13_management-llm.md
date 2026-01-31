# Overview

- システムで使用するLLMモデルを切り替え・管理する機能を提供します。これにより、異なるドメインやタスクに最適なモデルを選択できます。
- 実装コンポーネント: Backend (`backend/src/lakda/llm/`)
- 機能:
  - 利用可能なLLMモデルの一覧表示
  - モデルの選択・切り替え
  - モデルのステータス監視

# Models Supported

- Anthropic Claude
- Ollama
- OpenRouter
- Gemini-API

# Purpose

- ユーザーがシステムで使用するLLMモデルを柔軟に選択・管理できるようにすることで、特定のタスクやドメインに最適なモデルを利用できるようにします。
- モデルのステータス監視機能により、サービスの可用性を確保します。
- インターフェイスを統一して、それぞれのモデルにおいての用途ごとの適切なパラメータ設定を容易にします。

## Technical Details

### 共通インターフェース

すべてのLLMクライアントは `BaseLlmClient` 抽象クラスを継承し、以下のメソッドを実装します：

```python
from abc import ABC, abstractmethod
from typing import Type, TypeVar
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)

class BaseLlmClient(ABC):
    @abstractmethod
    def generate_response(self, prompt: str, response_model: Type[T]) -> T:
        """プロンプトに基づいてLLMからレスポンスを生成する"""
        pass

    @abstractmethod
    def health_check(self) -> bool:
        """LLMサービスの接続状態を確認する"""
        pass
```

### Anthropic Claude

- 使用パッケージ: `anthropic` Python SDK
- 主なクラス: `AnthropicLlmClient`
- configに使用できるパラメータ:
  - `api_key`: Anthropic APIキー（環境変数 `ANTHROPIC_API_KEY` から取得可能）
  - `model`: 使用するClaudeモデルの名前（例: `claude-3-5-sonnet-20241022`, `claude-3-haiku-20240307`）
  - `temperature`: 応答の多様性を制御する温度パラメータ（0.0〜1.0）
  - `max_tokens`: 生成される応答の最大トークン数（デフォルト: 4096）

### Ollama (docker container)

- 使用パッケージ: `httpx` Python SDK
- 主なクラス: `OllamaLlmClient`
- configに使用できるパラメータ:
  - `base_url`: OllamaサーバーのURL（デフォルト: `http://localhost:11434`）
  - `model`: 使用するOllamaモデルの名前（例: `llama3.2`, `mistral`, `codellama`）
  - `temperature`: 応答の多様性を制御する温度パラメータ（0.0〜1.0）
  - `max_tokens`: 生成される応答の最大トークン数（デフォルト: 2048）
  - `timeout`: リクエストタイムアウト秒数（デフォルト: 120）

### Gemini-API

- 使用パッケージ: `google-genai` Python SDK
- 主なクラス: `GeminiLlmClient`
- configに使用できるパラメータ:
  - `api_key`: Gemini APIキー（環境変数 `GEMINI_API_KEY` から取得可能）
  - `model`: 使用するGeminiモデルの名前（例: `gemini-1.5-pro`, `gemini-1.5-flash`, `gemini-2.0-flash`）
  - `temperature`: 応答の多様性を制御する温度パラメータ（0.0〜2.0）
  - `max_tokens`: 生成される応答の最大トークン数（デフォルト: 8192）
  - `top_p`: nucleus samplingのパラメータ（0.0〜1.0）
  - `top_k`: top-k samplingのパラメータ

### OpenRouter

- 使用パッケージ: `openai` Python SDK（OpenAI互換API）
- 主なクラス: `OpenRouterLlmClient`
- configに使用できるパラメータ:
  - `api_key`: OpenRouter APIキー（環境変数 `OPENROUTER_API_KEY` から取得可能）
  - `base_url`: OpenRouter APIのURL（デフォルト: `https://openrouter.ai/api/v1`）
  - `model`: 使用するモデルの名前（例: `anthropic/claude-3.5-sonnet`, `openai/gpt-4o`, `meta-llama/llama-3.1-70b-instruct`）
  - `temperature`: 応答の多様性を制御する温度パラメータ（0.0〜2.0）
  - `max_tokens`: 生成される応答の最大トークン数
  - `site_url`: OpenRouterダッシュボードでの識別用URL（オプション）
  - `app_name`: OpenRouterダッシュボードでの識別用アプリ名（オプション）

# Testing

- 各LLMクライアントクラスに対してユニットテストを実装し、API呼び出しのモックを使用して応答の検証を行います。
- テストフレームワーク: `pytest`
- モックライブラリ: `pytest-mock`, `respx`（httpx用）
- テストケース:
  - 正常系: 各モデルからの期待される応答の取得
  - 異常系: APIエラーやタイムアウト時の例外処理の検証

## 正常系

`backend/tests/llm/test_llm_clients.py`

```python
import pytest
from unittest.mock import patch, MagicMock
from pydantic import BaseModel

from lakda.llm.anthropic import AnthropicLlmClient
from lakda.llm.ollama import OllamaLlmClient
from lakda.llm.gemini import GeminiLlmClient
from lakda.llm.open_router import OpenRouterLlmClient


class SampleResponse(BaseModel):
    """テスト用のレスポンスモデル"""
    answer: str
    confidence: float


class TestAnthropicLlmClient:
    """Anthropic Claudeクライアントの正常系テスト"""

    @patch("lakda.llm.anthropic.anthropic.Anthropic")
    def test_generate_response_success(self, mock_anthropic_class):
        """case1: Anthropic Claudeからの応答取得"""
        # Arrange
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text='{"answer": "Hello!", "confidence": 0.95}')]
        mock_client.messages.create.return_value = mock_response

        client = AnthropicLlmClient(api_key="test-api-key", model="claude-3-5-sonnet-20241022")

        # Act
        result = client.generate_response(
            prompt="Say hello",
            response_model=SampleResponse
        )

        # Assert
        assert result.answer == "Hello!"
        assert result.confidence == 0.95
        mock_client.messages.create.assert_called_once()

    @patch("lakda.llm.anthropic.anthropic.Anthropic")
    def test_health_check_success(self, mock_anthropic_class):
        """Anthropic Claudeのヘルスチェック成功"""
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client
        mock_client.models.list.return_value = MagicMock()

        client = AnthropicLlmClient(api_key="test-api-key")

        assert client.health_check() is True


class TestOllamaLlmClient:
    """Ollamaクライアントの正常系テスト"""

    def test_generate_response_success(self, respx_mock):
        """case2: Ollamaからの応答取得"""
        import httpx

        # Arrange
        respx_mock.post("http://localhost:11434/api/generate").mock(
            return_value=httpx.Response(
                200,
                json={"response": '{"answer": "Hello from Ollama!", "confidence": 0.88}'}
            )
        )

        client = OllamaLlmClient(base_url="http://localhost:11434", model="llama3.2")

        # Act
        result = client.generate_response(
            prompt="Say hello",
            response_model=SampleResponse
        )

        # Assert
        assert result.answer == "Hello from Ollama!"
        assert result.confidence == 0.88

    def test_health_check_success(self, respx_mock):
        """Ollamaのヘルスチェック成功"""
        import httpx

        respx_mock.get("http://localhost:11434/api/tags").mock(
            return_value=httpx.Response(200, json={"models": []})
        )

        client = OllamaLlmClient(base_url="http://localhost:11434")

        assert client.health_check() is True


class TestGeminiLlmClient:
    """Gemini APIクライアントの正常系テスト"""

    @patch("lakda.llm.gemini.genai.Client")
    def test_generate_response_success(self, mock_genai_client_class):
        """case3: Gemini-APIからの応答取得"""
        # Arrange
        mock_client = MagicMock()
        mock_genai_client_class.return_value = mock_client
        mock_response = MagicMock()
        mock_response.text = '{"answer": "Hello from Gemini!", "confidence": 0.92}'
        mock_client.models.generate_content.return_value = mock_response

        client = GeminiLlmClient(api_key="test-api-key", model="gemini-1.5-pro")

        # Act
        result = client.generate_response(
            prompt="Say hello",
            response_model=SampleResponse
        )

        # Assert
        assert result.answer == "Hello from Gemini!"
        assert result.confidence == 0.92
        mock_client.models.generate_content.assert_called_once()

    @patch("lakda.llm.gemini.genai.Client")
    def test_health_check_success(self, mock_genai_client_class):
        """Gemini APIのヘルスチェック成功"""
        mock_client = MagicMock()
        mock_genai_client_class.return_value = mock_client
        mock_client.models.list.return_value = MagicMock()

        client = GeminiLlmClient(api_key="test-api-key")

        assert client.health_check() is True


class TestOpenRouterLlmClient:
    """OpenRouterクライアントの正常系テスト"""

    @patch("lakda.llm.open_router.OpenAI")
    def test_generate_response_success(self, mock_openai_class):
        """case4: OpenRouterからの応答取得"""
        # Arrange
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content='{"answer": "Hello from OpenRouter!", "confidence": 0.90}'))
        ]
        mock_client.chat.completions.create.return_value = mock_response

        client = OpenRouterLlmClient(api_key="test-api-key", model="anthropic/claude-3.5-sonnet")

        # Act
        result = client.generate_response(
            prompt="Say hello",
            response_model=SampleResponse
        )

        # Assert
        assert result.answer == "Hello from OpenRouter!"
        assert result.confidence == 0.90
        mock_client.chat.completions.create.assert_called_once()

    @patch("lakda.llm.open_router.OpenAI")
    def test_health_check_success(self, mock_openai_class):
        """OpenRouterのヘルスチェック成功"""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_client.models.list.return_value = MagicMock()

        client = OpenRouterLlmClient(api_key="test-api-key")

        assert client.health_check() is True
```

## 異常系

`backend/tests/llm/test_llm_clients_error.py`

```python
import pytest
from unittest.mock import patch, MagicMock
import httpx
from pydantic import BaseModel

from lakda.llm.anthropic import AnthropicLlmClient
from lakda.llm.ollama import OllamaLlmClient
from lakda.llm.gemini import GeminiLlmClient
from lakda.llm.open_router import OpenRouterLlmClient
from lakda.llm.exceptions import (
    LlmConnectionError,
    LlmAuthenticationError,
    LlmRateLimitError,
    LlmTimeoutError,
    LlmResponseParseError,
)


class SampleResponse(BaseModel):
    answer: str
    confidence: float


class TestAnthropicLlmClientError:
    """Anthropic Claudeクライアントの異常系テスト"""

    @patch("lakda.llm.anthropic.anthropic.Anthropic")
    def test_authentication_error(self, mock_anthropic_class):
        """case1: 認証エラー（無効なAPIキー）"""
        import anthropic
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client
        mock_client.messages.create.side_effect = anthropic.AuthenticationError(
            message="Invalid API key",
            response=MagicMock(status_code=401),
            body={}
        )

        client = AnthropicLlmClient(api_key="invalid-key")

        with pytest.raises(LlmAuthenticationError) as exc_info:
            client.generate_response(prompt="Hello", response_model=SampleResponse)

        assert "Invalid API key" in str(exc_info.value)

    @patch("lakda.llm.anthropic.anthropic.Anthropic")
    def test_rate_limit_error(self, mock_anthropic_class):
        """case2: レートリミットエラー"""
        import anthropic
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client
        mock_client.messages.create.side_effect = anthropic.RateLimitError(
            message="Rate limit exceeded",
            response=MagicMock(status_code=429),
            body={}
        )

        client = AnthropicLlmClient(api_key="test-key")

        with pytest.raises(LlmRateLimitError):
            client.generate_response(prompt="Hello", response_model=SampleResponse)

    @patch("lakda.llm.anthropic.anthropic.Anthropic")
    def test_response_parse_error(self, mock_anthropic_class):
        """case3: レスポンスパースエラー（不正なJSON）"""
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="This is not valid JSON")]
        mock_client.messages.create.return_value = mock_response

        client = AnthropicLlmClient(api_key="test-key")

        with pytest.raises(LlmResponseParseError):
            client.generate_response(prompt="Hello", response_model=SampleResponse)

    @patch("lakda.llm.anthropic.anthropic.Anthropic")
    def test_health_check_failure(self, mock_anthropic_class):
        """case4: ヘルスチェック失敗"""
        import anthropic
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client
        mock_client.models.list.side_effect = anthropic.APIConnectionError(
            message="Connection failed"
        )

        client = AnthropicLlmClient(api_key="test-key")

        assert client.health_check() is False


class TestOllamaLlmClientError:
    """Ollamaクライアントの異常系テスト"""

    def test_connection_error(self, respx_mock):
        """case5: 接続エラー（サーバー未起動）"""
        respx_mock.post("http://localhost:11434/api/generate").mock(
            side_effect=httpx.ConnectError("Connection refused")
        )

        client = OllamaLlmClient(base_url="http://localhost:11434")

        with pytest.raises(LlmConnectionError) as exc_info:
            client.generate_response(prompt="Hello", response_model=SampleResponse)

        assert "Connection refused" in str(exc_info.value)

    def test_timeout_error(self, respx_mock):
        """case6: タイムアウトエラー"""
        respx_mock.post("http://localhost:11434/api/generate").mock(
            side_effect=httpx.TimeoutException("Request timed out")
        )

        client = OllamaLlmClient(base_url="http://localhost:11434", timeout=10)

        with pytest.raises(LlmTimeoutError):
            client.generate_response(prompt="Hello", response_model=SampleResponse)

    def test_model_not_found_error(self, respx_mock):
        """case7: モデル未インストールエラー"""
        respx_mock.post("http://localhost:11434/api/generate").mock(
            return_value=httpx.Response(
                404,
                json={"error": "model 'nonexistent-model' not found"}
            )
        )

        client = OllamaLlmClient(base_url="http://localhost:11434", model="nonexistent-model")

        with pytest.raises(LlmConnectionError) as exc_info:
            client.generate_response(prompt="Hello", response_model=SampleResponse)

        assert "not found" in str(exc_info.value)

    def test_health_check_failure(self, respx_mock):
        """case8: ヘルスチェック失敗"""
        respx_mock.get("http://localhost:11434/api/tags").mock(
            side_effect=httpx.ConnectError("Connection refused")
        )

        client = OllamaLlmClient(base_url="http://localhost:11434")

        assert client.health_check() is False


class TestGeminiLlmClientError:
    """Gemini APIクライアントの異常系テスト"""

    @patch("lakda.llm.gemini.genai.Client")
    def test_authentication_error(self, mock_genai_client_class):
        """case9: 認証エラー（無効なAPIキー）"""
        from google.api_core.exceptions import Unauthenticated
        mock_client = MagicMock()
        mock_genai_client_class.return_value = mock_client
        mock_client.models.generate_content.side_effect = Unauthenticated("Invalid API key")

        client = GeminiLlmClient(api_key="invalid-key")

        with pytest.raises(LlmAuthenticationError):
            client.generate_response(prompt="Hello", response_model=SampleResponse)

    @patch("lakda.llm.gemini.genai.Client")
    def test_rate_limit_error(self, mock_genai_client_class):
        """case10: レートリミットエラー"""
        from google.api_core.exceptions import ResourceExhausted
        mock_client = MagicMock()
        mock_genai_client_class.return_value = mock_client
        mock_client.models.generate_content.side_effect = ResourceExhausted("Quota exceeded")

        client = GeminiLlmClient(api_key="test-key")

        with pytest.raises(LlmRateLimitError):
            client.generate_response(prompt="Hello", response_model=SampleResponse)

    @patch("lakda.llm.gemini.genai.Client")
    def test_response_parse_error(self, mock_genai_client_class):
        """case11: レスポンスパースエラー"""
        mock_client = MagicMock()
        mock_genai_client_class.return_value = mock_client
        mock_response = MagicMock()
        mock_response.text = "Invalid JSON response"
        mock_client.models.generate_content.return_value = mock_response

        client = GeminiLlmClient(api_key="test-key")

        with pytest.raises(LlmResponseParseError):
            client.generate_response(prompt="Hello", response_model=SampleResponse)

    @patch("lakda.llm.gemini.genai.Client")
    def test_health_check_failure(self, mock_genai_client_class):
        """case12: ヘルスチェック失敗"""
        from google.api_core.exceptions import GoogleAPIError
        mock_client = MagicMock()
        mock_genai_client_class.return_value = mock_client
        mock_client.models.list.side_effect = GoogleAPIError("Service unavailable")

        client = GeminiLlmClient(api_key="test-key")

        assert client.health_check() is False


class TestOpenRouterLlmClientError:
    """OpenRouterクライアントの異常系テスト"""

    @patch("lakda.llm.open_router.OpenAI")
    def test_authentication_error(self, mock_openai_class):
        """case13: 認証エラー（無効なAPIキー）"""
        from openai import AuthenticationError
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_client.chat.completions.create.side_effect = AuthenticationError(
            message="Invalid API key",
            response=MagicMock(status_code=401),
            body={}
        )

        client = OpenRouterLlmClient(api_key="invalid-key")

        with pytest.raises(LlmAuthenticationError):
            client.generate_response(prompt="Hello", response_model=SampleResponse)

    @patch("lakda.llm.open_router.OpenAI")
    def test_rate_limit_error(self, mock_openai_class):
        """case14: レートリミットエラー"""
        from openai import RateLimitError
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_client.chat.completions.create.side_effect = RateLimitError(
            message="Rate limit exceeded",
            response=MagicMock(status_code=429),
            body={}
        )

        client = OpenRouterLlmClient(api_key="test-key")

        with pytest.raises(LlmRateLimitError):
            client.generate_response(prompt="Hello", response_model=SampleResponse)

    @patch("lakda.llm.open_router.OpenAI")
    def test_model_not_available_error(self, mock_openai_class):
        """case15: モデル利用不可エラー"""
        from openai import NotFoundError
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_client.chat.completions.create.side_effect = NotFoundError(
            message="Model not found",
            response=MagicMock(status_code=404),
            body={}
        )

        client = OpenRouterLlmClient(api_key="test-key", model="nonexistent/model")

        with pytest.raises(LlmConnectionError):
            client.generate_response(prompt="Hello", response_model=SampleResponse)

    @patch("lakda.llm.open_router.OpenAI")
    def test_response_parse_error(self, mock_openai_class):
        """case16: レスポンスパースエラー"""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content="Not valid JSON"))
        ]
        mock_client.chat.completions.create.return_value = mock_response

        client = OpenRouterLlmClient(api_key="test-key")

        with pytest.raises(LlmResponseParseError):
            client.generate_response(prompt="Hello", response_model=SampleResponse)

    @patch("lakda.llm.open_router.OpenAI")
    def test_health_check_failure(self, mock_openai_class):
        """case17: ヘルスチェック失敗"""
        from openai import APIConnectionError
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_client.models.list.side_effect = APIConnectionError(
            message="Connection failed"
        )

        client = OpenRouterLlmClient(api_key="test-key")

        assert client.health_check() is False
```

## テスト実行

```bash
# 全LLMクライアントテストの実行
cd backend && uv run pytest tests/llm/ -v

# 正常系テストのみ実行
cd backend && uv run pytest tests/llm/test_llm_clients.py -v

# 異常系テストのみ実行
cd backend && uv run pytest tests/llm/test_llm_clients_error.py -v

# カバレッジレポート付きで実行
cd backend && uv run pytest tests/llm/ --cov=lakda.llm --cov-report=html
```

# API Endpoints

## GET /api/llm/models

利用可能なLLMモデルの一覧を取得します。

**Response:**
```json
{
  "models": [
    {
      "provider": "anthropic",
      "name": "claude-3-5-sonnet-20241022",
      "available": true
    },
    {
      "provider": "ollama",
      "name": "llama3.2",
      "available": true
    },
    {
      "provider": "gemini",
      "name": "gemini-1.5-pro",
      "available": true
    },
    {
      "provider": "openrouter",
      "name": "anthropic/claude-3.5-sonnet",
      "available": true
    }
  ]
}
```

## POST /api/llm/select

使用するLLMモデルを選択します。

**Request:**
```json
{
  "provider": "anthropic",
  "model": "claude-3-5-sonnet-20241022"
}
```

**Response:**
```json
{
  "status": "success",
  "selected_model": {
    "provider": "anthropic",
    "model": "claude-3-5-sonnet-20241022"
  }
}
```

## GET /api/llm/health

現在選択されているLLMモデルのヘルスチェックを実行します。

**Response:**
```json
{
  "provider": "anthropic",
  "model": "claude-3-5-sonnet-20241022",
  "status": "healthy",
  "latency_ms": 123
}
```

# Exception Classes

`backend/src/lakda/llm/exceptions.py`

```python
class LlmError(Exception):
    """LLM関連エラーの基底クラス"""
    pass


class LlmConnectionError(LlmError):
    """LLMサービスへの接続エラー"""
    pass


class LlmAuthenticationError(LlmError):
    """認証エラー（無効なAPIキー等）"""
    pass


class LlmRateLimitError(LlmError):
    """レートリミット超過エラー"""
    pass


class LlmTimeoutError(LlmError):
    """タイムアウトエラー"""
    pass


class LlmResponseParseError(LlmError):
    """レスポンスのパースエラー"""
    pass
```

# 注意点

- pydanticを使用して、各LLMクライアントの設定パラメータのバリデーションを行います。
- APIキーやエンドポイントURLなどの機密情報は環境変数から取得し、コードベースにハードコーディングしないように注意します。
