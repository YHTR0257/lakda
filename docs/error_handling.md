# Overview

このプロジェクトでのエラーハンドリングの方針と実装について説明します。

## Error Handling Strategy

エラーは発生箇所に応じて適切にハンドリングし、ユーザーに分かりやすいメッセージを返します。

---

## 1. Frontend (入力バリデーション・UI)

### 対象エラー
- ユーザー入力の形式エラー
- API レスポンスエラーの表示
- ネットワークエラー

### Error Flow

```mermaid
flowchart TD
    A[ユーザー入力] --> B{入力バリデーション}
    B -->|空| C[送信ボタン無効化]
    B -->|文字数超過| D[入力制限表示]
    B -->|OK| E[API リクエスト送信]

    E --> F{API レスポンス}
    F -->|2xx| G[回答表示]
    F -->|4xx| H[エラーメッセージ表示]
    F -->|5xx| I[リトライ促進メッセージ]
    F -->|Network Error| J[接続確認メッセージ]
```

### ハンドリング方針
| エラー種別 | 対応 | ユーザーへの表示 |
|-----------|------|-----------------|
| 入力が空 | 送信ボタン無効化 | 「質問を入力してください」 |
| 入力文字数超過 | 入力制限 | 「1000文字以内で入力してください」 |
| API 4xx エラー | エラーメッセージ表示 | API から返却されたメッセージ |
| API 5xx エラー | リトライ促進 | 「サーバーエラーが発生しました」 |
| ネットワークエラー | 接続確認促進 | 「ネットワーク接続を確認してください」 |

---

## 2. Backend API (リクエストバリデーション)

### 対象エラー
- リクエストボディの形式エラー
- 必須パラメータの欠落
- パラメータの型・範囲エラー

### Error Flow

```mermaid
flowchart TD
    A[API リクエスト受信] --> B{Content-Type}
    B -->|Invalid| C[415 Unsupported Media Type]
    B -->|OK| D{Pydantic バリデーション}

    D -->|必須パラメータ欠落| E[400 INVALID_FORMAT]
    D -->|型エラー| F[400 INVALID_FORMAT]
    D -->|サイズ超過| G[413 PAYLOAD_TOO_LARGE]
    D -->|OK| H[ビジネスロジックへ]

    E --> I[エラーレスポンス返却]
    F --> I
    G --> I
    C --> I
```

### ハンドリング方針
| エラー種別 | HTTP Status | Error Code |
|-----------|-------------|------------|
| 必須パラメータ欠落 | 400 | `INVALID_FORMAT` |
| パラメータ型エラー | 400 | `INVALID_FORMAT` |
| リクエストサイズ超過 | 413 | `PAYLOAD_TOO_LARGE` |

---

## 3. Backend Core (ビジネスロジック)

### 対象エラー
- ドキュメント処理エラー
- 検索エラー
- 回答生成エラー

### Error Flow

```mermaid
flowchart TD
    subgraph Document Processing
        A1[ファイル受信] --> B1{ファイル形式チェック}
        B1 -->|非対応| C1[400 INVALID_FORMAT]
        B1 -->|OK| D1[markitdown 変換]
        D1 -->|失敗| E1[500 PROCESSING_FAILED]
        D1 -->|OK| F1[チャンク化・保存]
    end

    subgraph Search
        A2[検索リクエスト] --> B2{ドメイン存在確認}
        B2 -->|存在しない| C2[404 DOMAIN_NOT_FOUND]
        B2 -->|ドキュメントなし| D2[400 DOMAIN_EMPTY]
        B2 -->|OK| E2[LlamaIndex 検索実行]
        E2 -->|結果なし| F2[空の結果を返却]
        E2 -->|OK| G2[検索結果返却]
    end
```

### ハンドリング方針
| エラー種別 | HTTP Status | Error Code |
|-----------|-------------|------------|
| 非対応ファイル形式 | 400 | `INVALID_FORMAT` |
| ドキュメント変換失敗 | 500 | `PROCESSING_FAILED` |
| ドメイン未存在 | 404 | `DOMAIN_NOT_FOUND` |
| ドメインにドキュメントなし | 400 | `DOMAIN_EMPTY` |

---

## 4. Database (Neo4j 接続・クエリ)

### 対象エラー
- 接続エラー
- クエリ実行エラー
- タイムアウト

### Error Flow

```mermaid
flowchart TD
    A[Database 操作] --> B{接続状態}
    B -->|切断| C[再接続試行]
    C -->|成功| D[クエリ実行]
    C -->|失敗| E[503 DATABASE_UNAVAILABLE]

    B -->|接続中| D
    D --> F{クエリ結果}
    F -->|タイムアウト| G[504 DATABASE_TIMEOUT]
    F -->|認証エラー| H[500 DATABASE_AUTH_ERROR]
    F -->|OK| I[結果返却]

    E --> J[ヘルスチェック通知]
    G --> K[リトライ or エラー返却]
```

### ハンドリング方針
| エラー種別 | HTTP Status | Error Code |
|-----------|-------------|------------|
| 接続失敗 | 503 | `DATABASE_UNAVAILABLE` |
| クエリタイムアウト | 504 | `DATABASE_TIMEOUT` |
| 認証エラー | 500 | `DATABASE_AUTH_ERROR` |

---

## 5. LLM (Gemini API / ollama)

### 対象エラー
- API 接続エラー
- レート制限
- モデル応答エラー

### Error Flow

```mermaid
flowchart TD
    A[LLM リクエスト] --> B{プライマリ LLM}
    B -->|接続失敗| C[フォールバック LLM]
    B -->|OK| D{API レスポンス}

    C -->|接続失敗| E[503 LLM_UNAVAILABLE]
    C -->|OK| D

    D -->|レート制限| F[リトライ待機]
    F -->|再試行| B
    F -->|上限超過| G[429 RATE_LIMIT_EXCEEDED]

    D -->|タイムアウト| H[504 LLM_TIMEOUT]
    D -->|コンテンツフィルタ| I[400 CONTENT_FILTERED]
    D -->|OK| J[回答返却]
```

### ハンドリング方針
| エラー種別 | HTTP Status | Error Code |
|-----------|-------------|------------|
| API 接続失敗 | 503 | `LLM_UNAVAILABLE` |
| レート制限 | 429 | `RATE_LIMIT_EXCEEDED` |
| タイムアウト | 504 | `LLM_TIMEOUT` |
| コンテンツフィルタ | 400 | `CONTENT_FILTERED` |

---

## System Error Flow (全体像)

```mermaid
flowchart TD
    A[ユーザー入力] --> B{Frontend<br>バリデーション}
    B -->|NG| C[入力エラー表示]
    B -->|OK| D[API リクエスト]

    D --> E{Backend API<br>バリデーション}
    E -->|NG| F[400 エラー]

    E -->|OK| G{Backend Core<br>ビジネスロジック}
    G -->|NG| H[4xx/5xx エラー]

    G -->|OK| I{Database<br>クエリ}
    I -->|NG| J[503/504 エラー]

    I -->|OK| K{LLM<br>回答生成}
    K -->|NG| L[5xx エラー]
    K -->|OK| M[成功レスポンス]

    F --> N[Frontend エラー表示]
    H --> N
    J --> N
    L --> N
    M --> O[回答表示]
```

---

## Error Codes Summary

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `INVALID_FORMAT` | 400 | リクエストフォーマットが不正 |
| `DOMAIN_NOT_FOUND` | 404 | 指定されたドメインが存在しない |
| `DOMAIN_EMPTY` | 400 | ドメインにドキュメントが存在しない |
| `DOCUMENT_NOT_FOUND` | 404 | ドキュメントIDが見つからない |
| `PROCESSING_FAILED` | 500 | ドキュメント処理に失敗 |
| `DATABASE_UNAVAILABLE` | 503 | データベースに接続できない |
| `DATABASE_TIMEOUT` | 504 | データベースクエリがタイムアウト |
| `LLM_UNAVAILABLE` | 503 | LLMサービスが利用不可 |
| `LLM_TIMEOUT` | 504 | LLM応答がタイムアウト |
| `RATE_LIMIT_EXCEEDED` | 429 | レート制限超過 |
| `CONTENT_FILTERED` | 400 | コンテンツがフィルタリングされた |
