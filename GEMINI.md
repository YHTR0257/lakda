# Knowledge Retrieval Assistant System (知識検索アシスタントシステム)

## Project Overview

特定のドメインに関する質問に対して、関連情報を検索し、コンテキストを付与した回答を生成する汎用的なRAGシステムです。

## Directory Structure

```
knowledge-retrieval-assistant/
├── backend/                     # FastAPIバックエンド
│   ├── src/kra/                 # コアモジュール
│   │   ├── api/                 # APIエンドポイント
│   │   ├── cli/                 # CLIコマンド
│   │   ├── core/                # ビジネスロジック
│   │   │   ├── search/          # 検索機能
│   │   │   ├── processing/      # Q&A処理
│   │   │   ├── documents/       # ドキュメント処理（markitdown統合）
│   │   │   └── feedback/        # フィードバック機能
│   │   ├── db/                  # データアクセス層
│   │   ├── models/              # データモデル
│   │   └── utils/               # ユーティリティ
│   └── tests/                   # バックエンドユニットテスト
├── frontend/                    # Next.jsフロントエンド
│   ├── src/                     # アプリケーションコード
│   │   ├── app/                 # App Router
│   │   ├── components/          # Reactコンポーネント
│   │   ├── lib/                 # ユーティリティ
│   │   ├── hooks/               # カスタムフック
│   │   ├── types/               # 型定義
│   │   └── store/               # Zustandストア
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

## Key Files

- `docs/project_structure.md`: ディレクトリ構造の詳細
- `docs/project_design.md`: プロジェクト設計
- `docs/architecture.md`: システムアーキテクチャ
- `docs/api_endpoint.md`: APIエンドポイント仕様

## Tech Stack

- **Backend**: FastAPI (Python 3.12, managed by uv)
  - Type Safety: Pydantic v2 (runtime validation + static type hints)
- **Frontend**: Next.js (App Router)
  - Type Safety: TypeScript (strict mode)
- **Package Manager**: uv (Python), npm (Node.js)

## Development Commands

```bash
# 環境セットアップ（uv使用）
uv sync

# バックエンドテスト
cd backend && uv run pytest tests/

# フロントエンドテスト
cd frontend && npm test

# 統合テスト
uv run pytest tests/integration/
```
