# Feature Design: FT08 - Llama Index Searching

## 1. 機能概要 (Overview)

本機能は、ユーザーが専用の質問入力画面（`SC07`）を通じてシステムに質問を入力した際に、BackendでLlamaIndexを用いてNeo4j PropertyGraphStoreを検索し、その結果を基に回答生成を行うまでを対象とします。

- **Feature ID**: FT08
- **Feature Name**: Llama Index Searching
- **Goal**: BackendがLlamaIndexを用いてNeo4j PropertyGraphStoreを検索し、回答を生成できることを確認する。

## 2. 担当コンポーネント (Components)

- **Backend**: APIエンドポイントを提供し、Frontendからのリクエストを受信します。
- **LLM**: LlamaIndexの検索・回答生成のLLM供給部分として機能します。
- **Neo4j**: PropertyGraphStoreとして検索対象のナレッジグラフを保持します。

## 3. UI/UX設計 (UI/UX Design)

### 3.1. 画面構成

本機能はBackendでの処理であり、FrontendのUIには直接的な変更はありません。ただし、回答生成結果が`SC07: 質問入力画面`に表示されることを前提としています。

## 4. データフロー (Data Flow)

```
Frontend
    ↓ POST /ask/confirm
Backend: api/ask.py
    ↓
services/ask/service.py
    ↓
services/ask/retrieval.py
    ↓ LlamaIndex PropertyGraphIndex.as_query_engine()
Neo4j PropertyGraphStore
    ↓ 検索結果（ノード・リレーション）
services/ask/service.py
    ↓ LLM で回答生成（LlmClientManager 経由）
Frontend ← AnswerResponse (JSON)
```

1. **[Backend]**: `POST /ask/confirm` エンドポイントでリクエストを受信します。
2. **[Backend]**: `ConfirmRequest` スキーマでリクエストをバリデーションします。
3. **[Backend - retrieval]**: LlamaIndex `PropertyGraphIndex` を使って Neo4j PropertyGraphStore を検索します。
4. **[Backend - service]**: 検索結果を基に、LLM（`LlmClientManager` 経由）で回答を生成します。
5. **[Backend → Frontend]**: `200 OK` ステータスと共に `AnswerResponse` を返します。

## 5. API仕様 (API Specification)

- **メソッド**: `POST`
- **エンドポイント**: `/ask/confirm`
- **ヘッダー**:
  - `Content-Type: application/json`

### 5.1. リクエストボディ

```json
{
  "session_id": "uuid-1234",
  "confirmed_question": "Pythonで発生したAttributeErrorの原因と解決方法は？",
  "options": {
    "max_results": 3
  }
}
```

| フィールド            | 型     | 必須 | 説明                                       |
| --------------------- | ------ | ---- | ------------------------------------------ |
| `session_id`          | string | Yes  | 質問解釈ステップで発行されたセッションID。 |
| `confirmed_question`  | string | Yes  | ユーザーが入力した質問の文字列。           |
| `options.max_results` | number | No   | 参照ソースの最大数（デフォルト: 3）。      |

スキーマ実装: `src/lakda/models/schemas/ask.py` の `ConfirmRequest`

### 5.2. レスポンス

#### 成功時 (200 OK)

```json
{
  "session_id": "uuid-1234",
  "question": "Pythonで発生したAttributeErrorの原因と解決方法は？",
  "answer": "AttributeErrorは、オブジェクトに存在しない属性にアクセスしようとした場合に発生します。\n\n**主な原因**:\n1. 変数名のタイプミス\n2. 未初期化のオブジェクト\n3. モジュールのインポート漏れ\n\n**解決方法**:\n- `hasattr()`で属性の存在を確認する\n- `getattr()`でデフォルト値を指定する",
  "sources": [
    {
      "file": "error-handling/python-exceptions.md",
      "line": 42,
      "snippet": "AttributeErrorは属性が存在しない場合に発生します",
      "score": 0.92
    }
  ],
  "timestamp": "2026-02-15T10:30:00Z"
}
```

| フィールド   | 型     | 説明                                       |
| ------------ | ------ | ------------------------------------------ |
| `session_id` | string | 質問解釈ステップで発行されたセッションID。 |
| `question`   | string | ユーザーが入力した質問の文字列。           |
| `answer`     | string | 生成された回答の本文。                     |
| `sources`    | array  | 回答の根拠となった引用元情報のリスト。     |

スキーマ実装: `src/lakda/models/schemas/ask.py` の `AnswerResponse`

#### 失敗時 (400 Bad Request / 500 Internal Server Error)

```json
{
  "detail": "Error message explaining the issue."
}
```

## 6. 実装状況 (Implementation Status)

| コンポーネント | 状況 | 場所 |
|---------------|------|------|
| `POST /ask/confirm` エンドポイント | ✅ スケルトン実装済み | `src/lakda/api/ask.py` |
| `ConfirmRequest` / `AnswerResponse` スキーマ | ✅ 実装済み | `src/lakda/models/schemas/ask.py` |
| `LlmClientManager` (llama.cpp, Google GenAI 等) | ✅ 実装済み・テスト済み | `src/lakda/llm/` |
| LlamaIndex `VectorStoreIndex` 統合 | ✅ テスト済み | `tests/llm/test_llamaindex_real.py` |
| `services/ask/retrieval.py` (PropertyGraphStore 検索) | ❌ 未実装 | `src/lakda/services/ask/retrieval.py` |
| `services/ask/service.py` (回答生成) | ❌ スケルトンのみ | `src/lakda/services/ask/service.py` |
| Neo4j PropertyGraphStore 統合 | ❌ 未実装 | `src/lakda/db/` |

**前提条件**: `services/index/` (FT07相当) で Markdown が Neo4j PropertyGraphStore にインデキシング済みであること。

## 7. 成功基準 (Acceptance Criteria)

- [ ] LlamaIndex `PropertyGraphIndex` を使用して、Neo4j PropertyGraphStore の検索が正常に行われること。
- [ ] 検索結果を基に、LLMで回答が生成されること。
- [ ] 正常なリクエストに対して、`200 OK` ステータスと共に正しいJSONレスポンスが返されること。
- [ ] 異常なリクエストに対して、適切なエラーステータスとエラーメッセージが返されること。
