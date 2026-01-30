# Knowledge Retrieval Assistant

ユーザーからの質問に対して高品質な回答を生成し、関連するドキュメントを検索・提示するRAGシステムです。

## Tech Stack

- **Backend**: FastAPI (Python 3.12, managed by uv)
  - Type Safety: Pydantic v2 (runtime validation + static type hints)
- **Frontend**: Next.js (App Router)
  - Type Safety: TypeScript (strict mode)
- **Database**: Neo4j
- **State Management**: Zustand
- **Document Processing**: markitdown
- **Package Manager**: uv (Python), npm (Node.js)

## Project Structure

```
knowledge-retrieval-assistant/
├── backend/                     # FastAPIバックエンド
│   ├── src/kra/                 # コアモジュール
│   │   ├── api/                 # APIエンドポイント
│   │   ├── cli/                 # CLIコマンド
│   │   ├── core/                # ビジネスロジック
│   │   ├── db/                  # データアクセス層
│   │   ├── models/              # データモデル
│   │   └── utils/               # ユーティリティ
│   └── tests/                   # バックエンドユニットテスト
├── frontend/                    # Next.jsフロントエンド
│   ├── src/                     # アプリケーションコード
│   └── tests/                   # フロントエンドユニットテスト
├── data/                        # データ保存
│   ├── raw/                     # 元ドキュメント
│   ├── processed/               # 処理済みデータ
│   ├── feedback/                # フィードバックデータ
│   └── logs/                    # ログ
├── tests/                       # 統合テスト・E2Eテスト
├── scripts/                     # 補助スクリプト
├── envs/                        # 環境設定・Docker
└── docs/                        # ドキュメント
```

## Features

| Feature ID | Description | Status |
|------------|-------------|--------|
| FT01 | 質問入力インターフェース | Implemented |
| FT02 | ドキュメントアップロード | Implemented |
| FT03 | ドキュメント変換（markitdown） | Implemented |
| FT04 | メタデータ生成 | In Progress |
| FT05 | 質問解釈 | Planned |
| FT06 | ドキュメント検索 | Planned |
| FT07 | 回答生成 | Planned |
| FT08 | 回答表示 | Planned |
| FT09 | フィードバック蓄積 | Planned |

## Getting Started

### Prerequisites

- Python 3.12
- Node.js 18+
- uv (Python package manager)

### Installation

```bash
# Python依存関係のインストール
uv sync

# フロントエンド依存関係のインストール
cd frontend && npm install
```

### Running Tests

```bash
# バックエンドユニットテスト（uv使用）
cd backend && uv run pytest tests/

# フロントエンドユニットテスト
cd frontend && npm test

# 統合テスト
uv run pytest tests/integration/
```

## Documentation

- [Project Structure](docs/project_structure.md) - ディレクトリ構造の詳細
- [Architecture](docs/architecture.md) - システムアーキテクチャ
- [Project Design](docs/project_design.md) - プロジェクト設計
- [API Endpoints](docs/api_endpoint.md) - APIエンドポイント仕様
- [Error Handling](docs/error_handling.md) - エラーハンドリング
- [Features](docs/features/) - 機能詳細ドキュメント
