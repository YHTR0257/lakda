# Feature Design: FT08 - Llama Index Searching

## 1. 機能概要 (Overview)

本機能は、ユーザーが専用の質問入力画面（`SC07`）を通じてシステムに質問を入力した際に、BackendでLlamaIndexを用いて関連ドキュメントを検索し、その結果を基に簡単な回答生成を行うまでを対象とします。

- **Feature ID**: FT08
- **Feature Name**: Llama Index Searching
- **Goal**: BackendがLlamaIndexを用いて関連ドキュメントを検索し、回答を生成できることを確認する。

## 2. 担当コンポーネント (Components)

- **Backend**: APIエンドポイントを提供し、Frontendからのリクエストを受信します。
- **LLM**: LlamaIndexの検索機能のLLM供給部分として機能します。

## 3. UI/UX設計 (UI/UX Design)

### 3.1. 画面構成

本機能は、backendでの処理であり、FrontendのUIには直接的な変更はありません。ただし、回答生成結果が`SC07: 質問入力画面`に表示されることを前提としています。

## 4. データフロー (Data Flow)

1.  **[Backend]**: `POST /api/ask/confirm`エンドポイントでリクエストを受信します。
2.  **[Backend]**: リクエストボディから質問文字列を抽出します。
3.  **[Backend]**: LlamaIndexを使用して、関連ドキュメントを検索します。
4.  **[Backend]**: 検索結果を基に、簡単な回答を生成します。
5.  **[Backend -> Frontend]**: `200 OK`ステータスと共に、回答データを含むJSONを返します。

## 5. API仕様 (API Specification)

- **メソッド**: `POST`
- **エンドポイント**: `/api/ask/confirm`
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

### 5.2. レスポンス (同期的な回答)

#### 成功時 (200 OK)

FT09で生成された回答と引用元を返します。

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

#### 失敗時 (400 Bad Request / 500 Internal Server Error)

```json
{
  "detail": "Error message explaining the issue."
}
```

## 6. 成功基準 (Acceptance Criteria)

- [ ] `LlamaIndex`を使用して、関連ドキュメントの検索が正常に行われること。
- [ ] 検索結果を基に、簡単な回答が生成されること。
- [ ] 正常なリクエストに対して、`200 OK`ステータスと共に正しいJSONレスポンスが返されること。
- [ ] 異常なリクエストに対して、適切なエラーステータスとエラーメッセージが返されること。
