# API Endpoints

| Method | Endpoint | Description | Feature ID |
|--------|----------|-------------|-------------|
| POST   | /query   | ユーザーの質問に対する回答生成 | FT02 |
| POST   | /documents/upload | ドキュメントのアップロードと処理開始 | FT07 |
| GET    | /documents/{document_id}/status | ドキュメント処理ステータスの取得 | FT07 |
| GET    | /documents | ドキュメント一覧の取得（ドメイン別） | FT07 |
| POST   | /feedback | ユーザーフィードバックの記録 | FT09 |

## Phase 2: CLI Interface (2026-01-02 - 2026-02-02)

Phase 2ではHTTP APIは実装せず、CLIベースで動作します。

### CLI Usage

```bash
# 質問応答
python -m kra.main ask --question "Pythonでエラーが出た" --domain error-handling

# ドキュメント処理
python -m kra.main upload --file path/to/document.pdf --domain error-handling

# フィードバック記録
python -m kra.main feedback --session-id {id} --rating useful
```

---

## Phase 3: REST API (2026-02-02 - 2026-03-31) - 条件付き実装

Phase 3でAPI連携機能(FT11)を実装する場合のエンドポイント設計。

### Base URL
```
http://localhost:8000/api/v1
```

---

### 1. 質問応答

#### `POST /query`

**Request**:
```json
{
  "question": "Pythonでエラーが出た",
  "domain": "error-handling",  // optional
  "options": {
    "interpret": true,          // 質問解釈を実行
    "max_results": 3            // 最大引用元数
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

**Error Response**:
```json
{
  "error": "No documents found in domain",
  "code": "DOMAIN_EMPTY"
}
```

---

### 2. ドキュメント管理

#### `POST /documents/upload`

**Request** (multipart/form-data):
```
file: document.pdf
domain: error-handling
metadata: {"tags": ["python", "exception"]}  // optional
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
  "status": "completed",  // processing, completed, failed
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

### 3. フィードバック

#### `POST /feedback`

**Request**:
```json
{
  "session_id": "uuid-1234",
  "rating": "useful",  // useful, not_useful
  "comment": "解決できました"  // optional
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

### 4. ドメイン管理 (Phase 3 - FT10実装時のみ)

#### `GET /domains`

**Response**:
```json
{
  "domains": [
    {
      "name": "error-handling",
      "path": "data/documents/error-handling",
      "description": "エラーハンドリング関連",
      "document_count": 15,
      "weight": 1.0
    },
    {
      "name": "architecture",
      "path": "data/documents/architecture",
      "description": "アーキテクチャ設計",
      "document_count": 8,
      "weight": 1.2
    }
  ]
}
```

#### `POST /domains`

**Request**:
```json
{
  "name": "api-guides",
  "path": "data/documents/api-guides",
  "description": "API利用ガイド",
  "weight": 1.0,
  "filters": {
    "tags": ["api", "rest"]
  }
}
```

**Response**:
```json
{
  "status": "created",
  "domain": "api-guides"
}
```

---

### 5. システム情報

#### `GET /health`

**Response**:
```json
{
  "status": "healthy",
  "mcp_servers": {
    "mcp-markdown-ragdocs": "connected",
    "markdownify-mcp": "connected"
  },
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

---

## Authentication (Phase 3 - 将来実装)

現在は認証なし。Phase 3後半でAPI公開する場合:

```
Authorization: Bearer {api_key}
```
