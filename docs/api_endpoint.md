# API Endpoints

## Base URL
```
http://localhost:8000/api
```

## Endpoint Summary

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST   | `/api/ask/interpret` | 質問の解釈と確認（FT06） |
| POST   | `/api/ask/confirm` | 確認済み質問に対する回答生成（FT08+FT09） |
| POST   | `/api/documents/upload` | ドキュメントのアップロードと処理開始 |
| GET    | `/api/documents/{document_id}/status` | ドキュメント処理ステータスの取得 |
| GET    | `/api/documents?domain={domain}` | ドキュメント一覧の取得（ドメイン別） |
| POST   | `/api/feedback` | ユーザーフィードバックの記録 |
| GET    | `/api/health` | システムヘルスチェック |

---

## 1. 相談（質問応答）

質問応答は2ステップで行います：
1. **質問解釈** (`/ask/interpret`): ユーザーの曖昧な質問を解釈し、確認を求める
2. **回答生成** (`/ask/confirm`): 確認済みの質問に対して回答を生成する

このフローにより、ユーザーは解釈された質問を確認・修正してから回答を取得できます（FT06/FT07対応）。

### Step 1: 質問解釈

#### `POST /ask/interpret`

ユーザーの質問を解釈し、明確化された質問候補を返します。

**Request**:
```json
{
  "question": "Pythonでエラーが出た",
  "domain": "error-handling"
}
```

**Response**:
```json
{
  "session_id": "uuid-1234",
  "original_question": "Pythonでエラーが出た",
  "interpreted_question": "Pythonで発生したAttributeErrorの原因と解決方法は？",
  "interpretation_confidence": 0.75,
  "alternative_interpretations": [
    "Pythonで発生したTypeErrorの原因と解決方法は？",
    "Pythonで発生したImportErrorの原因と解決方法は？"
  ]
}
```

| Field | Type | Description |
|-------|------|-------------|
| `session_id` | string | セッションID（Step 2で使用） |
| `original_question` | string | ユーザーの元の質問 |
| `interpreted_question` | string | システムが解釈した質問（推奨） |
| `interpretation_confidence` | number | 解釈の確信度（0.0-1.0） |
| `alternative_interpretations` | string[] | 代替解釈候補（最大3件） |

### Step 2: 回答生成

#### `POST /ask/confirm`

確認済みの質問に対して、ドキュメント検索と回答生成を実行します。

**Request**:
```json
{
  "session_id": "uuid-1234",
  "confirmed_question": "Pythonで発生したAttributeErrorの原因と解決方法は？",
  "options": {
    "max_results": 3
  }
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `session_id` | string | Yes | Step 1で取得したセッションID |
| `confirmed_question` | string | Yes | ユーザーが確認/修正した質問 |
| `options.max_results` | number | No | 参照ソースの最大数（デフォルト: 3） |

**Response**:
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

---

## 2. ドキュメント管理

#### `POST /documents/upload`

**Request** (multipart/form-data):
```
file: document.pdf
domain: error-handling
metadata: {"tags": ["python", "exception"]}
```

**Response**:
```json
{
  "document_id": "doc-5678",
  "status": "processing",
  "message": "Document queued for processing"
}
```

#### `GET /documents/{document_id}/status`

**Response**:
```json
{
  "document_id": "doc-5678",
  "status": "completed",
  "processed_file": "data/documents/error-handling/document.md",
  "metadata": {
    "domain": "error-handling",
    "tags": ["python", "exception"],
    "created": "2026-02-15T10:35:00Z"
  }
}
```

#### `GET /documents?domain={domain}`

**Response**:
```json
{
  "documents": [
    {
      "id": "doc-5678",
      "title": "Python Exception Handling",
      "domain": "error-handling",
      "path": "error-handling/python-exceptions.md",
      "created": "2026-02-15T10:35:00Z"
    }
  ],
  "total": 1
}
```

---

## 3. フィードバック

#### `POST /feedback`

**Request**:
```json
{
  "session_id": "uuid-1234",
  "rating": "useful",
  "comment": "解決できました"
}
```

**Response**:
```json
{
  "status": "recorded",
  "feedback_id": "fb-9012"
}
```

---

## 4. システム情報

#### `GET /health`

**Response**:
```json
{
  "status": "healthy",
  "database": "connected",
  "llm_status": "available"
}
```

---

## Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `DOMAIN_NOT_FOUND` | 404 | 指定されたドメインが存在しない |
| `DOMAIN_EMPTY` | 400 | ドメインにドキュメントが存在しない |
| `DOCUMENT_NOT_FOUND` | 404 | ドキュメントIDが見つからない |
| `SESSION_NOT_FOUND` | 404 | セッションIDが見つからない |
| `SESSION_EXPIRED` | 410 | セッションが期限切れ |
| `PROCESSING_FAILED` | 500 | ドキュメント処理に失敗 |
| `LLM_UNAVAILABLE` | 503 | LLMサービスが利用不可 |
| `INVALID_FORMAT` | 400 | リクエストフォーマットが不正 |
| `RATE_LIMIT_EXCEEDED` | 429 | レート制限超過 |
