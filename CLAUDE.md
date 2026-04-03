# CLAUDE.md

<important>

## Development Process (実行フロー)

全てのプロセス間ではユーザーと認識のすり合わせを行います。ユーザーの承認なしに次のプロセスに進まないこと。
各プロセスの前に、 `/translate` と `/explore` を必ず実行し、ユーザーの指示を正確に理解し、関連ファイルと影響範囲を把握すること。

1. **Design**: アーキテクチャ設計、モジュール分割、インターフェース定義
2. **Explore**: コードベースを探索し、関連ファイルと影響範囲を把握 Skill: `/explore`
3. **Define scope**: 変更のスコープを明確にし、必要なタスクを洗い出す 
4. **Planning**: 仕様策定、タスク分割、スケジュール作成
5. **Implementation**: コーディング、ユニットテスト、統合テスト
6. **Linter, Formatter**: コードスタイルの統一、品質向上
7. **Code Review**: コードの品質、可読性、設計への準拠を確認

## 必須スキル（hookで強制。違反時はユーザーが検知する）

ユーザーのプロンプトを受け取ったら、コード修正やファイル読み込みの**前に**、
以下の2つのスキルをこの順で実行せよ:

1. `/translate` — ユーザーの指示を「論点抽出 → 構造化された問題文 → リポジトリの具体箇所」に翻訳
2. `/explore` — 翻訳結果をもとに関連ファイルと影響範囲を探索・報告

この2つを**スキップしてはならない**。
hookの `<user-prompt-submit-hook>` メッセージでも同じ指示が届く。

```
ユーザーの指示
  → /translate（論点抽出・構造化・具体箇所の特定）
  → ユーザーの確認
  → /explore（関連ファイルの探索・影響範囲の報告）
  → ユーザーの承認
  → 各ステップのタスク実行へ
```

### git 操作の禁止

git コマンド（commit, push, checkout, branch, merge, rebase 等）は実行しない。
git の状態確認（status, log, diff, rev-parse）は許可する。

</important>

## Project Overview

**LAKDA (LLM-Assisted Knowledge Discovery Application)** - A domain-agnostic RAG system that searches local/cloud documents to answer domain-specific questions with context and citations. Uses LlamaIndex for RAG pipeline and Neo4j as PropertyGraphStore (knowledge graph).

## Development Commands

### Environment Setup
```bash
# Python version: 3.12 (managed by uv via .python-version)
cd backend && uv sync    # Install dependencies from pyproject.toml
```

### Running the Application
```bash
cd backend && uv run uvicorn lakda.main:app --reload
```

### Testing
```bash
# ユニットテスト（モック使用）
cd backend && uv run pytest tests/ -m "not llm_api and not db"

# LLM実APIテスト（llama.cpp サーバー必要）
make test-llm-api PROVIDER=llamacpp

# DBテスト（Neo4j サーバー必要）
cd backend && uv run pytest tests/ -m db

# 全テスト
cd backend && uv run pytest tests/
```

## Architecture Overview

### System Architecture

```
User Input
    ↓
API Layer (FastAPI)
    ↓
Service Layer
    ├── ask/       → 質問応答（LlamaIndex PropertyGraphStore からの検索）
    ├── index/     → インデキシング（Markdown → Neo4j PropertyGraphStore）
    └── documents/ → ドキュメント変換（PDF/Word等 → Markdown or jsonL）
    ↓
LLM Layer (LlamaIndex)
    ├── LLM: llama.cpp (OpenAI互換API) / Google GenAI / Anthropic / OpenRouter
    └── Embedding: llama.cpp (OpenAI互換API)
    ↓
Neo4j (PropertyGraphStore)
```

### Service Responsibilities

| Service | 入力 | 出力 | 責務 |
|---------|------|------|------|
| `documents` | PDF / Word / HTML 等 | Markdown or jsonL | フォーマット変換・構造化。MarkItDown等を使用 |
| `index` | Markdown | Neo4j PropertyGraphStore | LlamaIndex でノード・リレーション抽出し Neo4j に保存 |
| `ask` | 質問テキスト | 回答 + ソース | PropertyGraphStore を検索し LLM で回答生成 |

**index サービスの責務境界**:
- `documents` から受け取った Markdown のみを対象とする
- LlamaIndex の `PropertyGraphIndex` を使ってエンティティ・関係を抽出
- Neo4j の `Neo4jPropertyGraphStore` に永続化
- PDFの解析・レイアウト補正などは `documents` サービスの責務

### Module Responsibilities

#### Layer Overview

```
API Layer (api/)
    ↓ リクエスト受付
Service Layer (services/)
    ↓ 実処理
LLM Layer (llm/)
    ↓ モデル接続・プロンプト管理
Neo4j (db/)
```

#### Module Details

| Layer | Module | Role |
|-------|--------|------|
| Entry | `src/lakda/main.py` | FastAPI アプリ初期化・ルーター登録 |
| API | `src/lakda/api/ask.py` | 質問応答エンドポイント |
| API | `src/lakda/api/documents.py` | ドキュメント変換エンドポイント |
| API | `src/lakda/api/feedback.py` | フィードバックエンドポイント |
| API | `src/lakda/api/dependencies.py` | FastAPI 依存性注入 |
| Service | `src/lakda/services/ask/service.py` | 質問応答ビジネスロジック |
| Service | `src/lakda/services/ask/retrieval.py` | Neo4j PropertyGraphStore からの検索 |
| Service | `src/lakda/services/index/service.py` | インデキシング オーケストレーション |
| Service | `src/lakda/services/index/store.py` | Neo4j PropertyGraphStore への保存 |
| Service | `src/lakda/services/index/pipeline.py` | LlamaIndex ingestion pipeline |
| Service | `src/lakda/services/documents/converter.py` | 各種ドキュメント → Markdown/jsonL 変換 |
| LLM | `src/lakda/llm/client.py` | LlmClientFactory / LlmClientManager |
| LLM | `src/lakda/llm/base.py` | LlamaIndexLlmClient 基底クラス |
| LLM | `src/lakda/llm/providers/llamacpp.py` | llama.cpp LLM + Embedding クライアント |
| LLM | `src/lakda/llm/providers/google_genai.py` | Google GenAI LLM クライアント |
| LLM | `src/lakda/llm/providers/anthropic.py` | Anthropic LLM クライアント |
| LLM | `src/lakda/llm/providers/openrouter.py` | OpenRouter LLM クライアント |
| DB | `src/lakda/db/` | Neo4j 接続管理 |
| Models | `src/lakda/models/schemas/ask.py` | Pydantic スキーマ (AskRequest, AnswerResponse 等) |

### Data Storage Structure

```
data/
├── raw/                    # 元ドキュメント（PDF, Word等）
│   ├── papers/
│   ├── notes/
│   └── datasets/
└── processed/              # documents サービスの変換済みファイル（Markdown/jsonL）
    ├── papers/
    ├── notes/
    └── datasets/
```

Neo4j はインデックスデータの永続化ストアとして使用（`data/` には保存しない）。

<important>

## Technology Stack

- **Python**: 3.12 (managed via uv)
- **Web Framework**: FastAPI
- **RAG Framework**: LlamaIndex
- **Graph DB**: Neo4j (PropertyGraphStore)
- **LLM (local)**: llama.cpp (OpenAI互換API経由)
- **LLM (cloud)**: Google GenAI / Anthropic / OpenRouter
- **Embedding**: llama.cpp (OpenAI互換API経由、モデル: bge-m3)
- **Type Safety**: Pydantic v2
- **Dependency Management**: uv (pyproject.toml + uv.lock)

</important>

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `LLAMACPP_LLM_URL` | llama.cpp LLM サーバー URL | `http://localhost:11406` |
| `LLAMACPP_EMBEDDING_URL` | llama.cpp Embedding サーバー URL | `http://localhost:11407` |
| `GOOGLE_API_KEY` | Google GenAI API キー | - |
| `DATABASE_URL_BOLT` | Neo4j Bolt URL | `bolt://localhost:7687` |
| `NEO4J_USER` | Neo4j ユーザー名 | `neo4j` |
| `NEO4J_PASSWORD` | Neo4j パスワード | `password` |

## Implementation Status

| Component | Status |
|-----------|--------|
| LLM layer (llama.cpp, Google GenAI, Anthropic, OpenRouter) | ✅ 実装済み・テスト済み |
| LlamaIndex VectorStoreIndex 統合 | ✅ テスト済み (test_llamaindex_real.py) |
| Neo4j 接続 | ✅ テスト済み (test_connect_db.py) |
| FastAPI 基本構造 (main, ask, documents, feedback) | ✅ スケルトン実装済み |
| `services/index/` | ❌ 未実装 |
| `services/documents/` | ❌ 未実装 |
| `services/ask/` (retrieval, service) | ❌ スケルトンのみ |
| Neo4j PropertyGraphStore 統合 | ❌ 未実装 |

## Project Goals & Success Criteria

| Goal | Target | Measurement |
|------|--------|-------------|
| Reduce domain knowledge access time | 80% reduction | Time from question to relevant information |
| Resolve ambiguous questions | 50% reduction in retries | Number of follow-up questions needed |
| Multi-domain knowledge sharing | 3+ domains operational | System supports multiple knowledge bases |
