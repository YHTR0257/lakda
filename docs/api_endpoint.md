# API Endpoints

## Base URL
```
http://localhost:8000/api
```

## Endpoint Summary

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST   | /ask     | ユーザーの質問に対する回答生成 |
| POST   | /documents/upload | ドキュメントのアップロードと処理開始 |
| GET    | /documents/{document_id}/status | ドキュメント処理ステータスの取得 |
| GET    | /documents | ドキュメント一覧の取得（ドメイン別） |
| POST   | /feedback | ユーザーフィードバックの記録 |
| GET    | /health | システムヘルスチェック |

---

## 1. 相談（質問応答）

#### `POST /ask`

**Request**:
```json
{
  "question": "Pythonでエラーが出た",
  "domain": "error-handling",
  "options": {
    "interpret": true,
    "max_results": 3
  }
}
```

**Response**:
```json
{
  "session_id": "uuid-1234",
  "interpreted_question": "Pythonで発生したAttributeErrorの原因と解決方法は？",
  "answer": "AttributeErrorは...",
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
| `PROCESSING_FAILED` | 500 | ドキュメント処理に失敗 |
| `LLM_UNAVAILABLE` | 503 | LLMサービスが利用不可 |
| `INVALID_FORMAT` | 400 | リクエストフォーマットが不正 |
| `RATE_LIMIT_EXCEEDED` | 429 | レート制限超過 |
