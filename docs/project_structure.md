# Overview

- プロジェクトのディレクトリ構造と各ディレクトリ・ファイルの役割について説明します。

## Directory Structure

```
knowledge-retrieval-assistant/   # プロジェクトルート
├── backend/                         # backendサーバーコード
├── frontend/                        # フロントエンドコード
├── docs/                            # ドキュメント
│   ├── features/                    # 各機能の詳細ドキュメント
│   ├── architecture.md              # システムアーキテクチャドキュメント
│   ├── project_structure.md         # プロジェクト構造ドキュメント
│   ├── project_design.md            # プロジェクト設計ドキュメント
│   ├── api_endpoint.md              # APIエンドポイントドキュメント
│   └── error_handling.md            # エラーハンドリングドキュメント
├── data/                            # データ保存ディレクトリ
│   ├── raw/                         # 元ドキュメント
│   │    ├── papers/                     # 論文
│   │    ├── notes/                      # ノート
│   │    └── datasets/                   # データセット
│   ├── processed/                   # チャンク化・埋め込み済み
│   │    ├── chunks/                     # チャンクデータ
│   │    └── metadata/                   # メタデータ
│   ├── feedback/                    # フィードバックデータ
│   └── logs/                        # アプリケーションログ（オプション）
├── envs/                            # 環境設定ファイル
│   ├── docker/                      # Dockerfile群
│   │    ├── backend.Dockerfile          # backend用Dockerfile
│   │    ├── docker-compose.override.yml # 開発用Docker Compose設定
│   │    └── frontend.Dockerfile         # frontend用Dockerfile
│   ├── config/                      # プロジェクトの設定ファイル
│   └── docker-compose.yml           # Docker Compose設定ファイル
├── scripts/                         # 補助スクリプト
│   ├── setup/                       # 環境構築スクリプト
│   │    ├── init_db.sh                  # DB初期化
│   │    └── seed_data.py                # 初期データ投入
│   ├── maintenance/                 # メンテナンス
│   │    ├── backup.sh                   # バックアップ
│   │    └── reindex.py                  # 再インデックス
│   └── dev/                         # 開発補助
│        └── generate_test_data.py       # テストデータ生成
├── tests/                           # 統合テスト
│   ├── integration/                 # 統合テスト
│   │    ├── test_api_flow.py            # API全体フローテスト
│   │    ├── test_search_pipeline.py     # 検索パイプラインテスト
│   │    └── test_upload_pipeline.py     # アップロードパイプラインテスト
│   ├── e2e/                         # E2Eテスト
│   │    └── ...
│   └── conftest.py                  # 共通フィクスチャ
├── .gitignore                       # Git無視ファイル設定
├── .env.example                     # 環境変数テンプレート
├── .env                             # 環境変数ファイル（.gitignore対象）
├── docker-compose.yml               # Docker Compose設定
└── README.md                        # プロジェクト概要README
```

### Backend Directory

バックエンドのディレクトリ構造は以下の通りです。FastAPIアプリケーションとして機能します。

```
backend/
├── src/                             # アプリケーションコード
│   └── kra/                         # コアモジュール
│       ├── __init__.py              # kraパッケージ初期化
│       ├── main.py                  # アプリケーションエントリーポイント
│       ├── api/                     # APIレイヤー（routes/を省略）
│       │    ├── __init__.py
│       │    ├── dependencies.py         # 依存性注入
│       │    ├── search.py               # 検索エンドポイント
│       │    ├── upload.py               # アップロードエンドポイント
│       │    └── feedback.py             # フィードバックエンドポイント
│       ├── cli/                     # CLI関連コード
│       │    ├── __init__.py
│       │    └── commands.py             # CLIコマンド定義
│       ├── core/                    # ビジネスロジック
│       │    ├── __init__.py
│       │    ├── search/                 # 検索機能
│       │    │    ├── __init__.py
│       │    │    ├── service.py             # 検索サービス
│       │    │    └── retrieval.py           # ドキュメント検索
│       │    ├── processing/             # Q&A処理
│       │    │    ├── __init__.py
│       │    │    ├── generator.py           # 回答生成
│       │    │    └── interpreter.py         # 質問解釈
│       │    ├── documents/              # ドキュメント処理（インジェスト）
│       │    │    ├── __init__.py
│       │    │    ├── converter.py           # markitdown統合（PDF/Word→Markdown変換）
│       │    │    ├── metadata.py            # メタデータ・Frontmatter生成
│       │    │    └── indexer.py             # インデックス登録
│       │    └── feedback/               # フィードバック機能
│       │         ├── __init__.py
│       │         └── service.py             # フィードバックサービス
│       ├── db/                      # データアクセス層
│       │    ├── __init__.py
│       │    ├── repositories/           # リポジトリパターン
│       │    │    └── neo4j.py               # Neo4j関連
│       │    └── migrations/             # DBマイグレーション
│       ├── models/                  # データモデル定義
│       │    ├── __init__.py
│       │    ├── schemas/                # リクエスト/レスポンススキーマ
│       │    │    ├── __init__.py
│       │    │    ├── search.py              # 検索関連スキーマ
│       │    │    └── feedback.py            # フィードバック関連スキーマ
│       │    └── entities/               # DBエンティティ
│       │         ├── __init__.py
│       │         └── document.py            # ドキュメントエンティティ
│       └── utils/                   # ユーティリティ関数
│            ├── __init__.py
│            ├── config.py               # 設定管理
│            └── mcp_client.py           # MCPクライアント
│
└── tests/                           # バックエンドユニットテスト
     ├── __init__.py
     ├── conftest.py                     # テストフィクスチャ
     ├── api/                            # APIレイヤーテスト
     │    ├── test_search.py
     │    ├── test_upload.py
     │    └── test_feedback.py
     ├── core/                           # ビジネスロジックテスト
     │    ├── search/
     │    │    ├── test_service.py
     │    │    └── test_retrieval.py
     │    ├── processing/
     │    │    ├── test_generator.py
     │    │    └── test_interpreter.py
     │    ├── documents/
     │    │    ├── test_converter.py
     │    │    ├── test_metadata.py
     │    │    └── test_indexer.py
     │    └── feedback/
     │         └── test_service.py
     ├── db/                             # データアクセス層テスト
     │    └── repositories/
     │         └── test_document_repo.py
     └── utils/                          # ユーティリティテスト
          ├── test_config.py
          └── test_mcp_client.py
```

### Frontend Directory

フロントエンドのディレクトリ構造は以下の通りです。Next.js App Routerを使用します。

```
frontend/
├── src/                             # フロントエンドアプリケーションコード
│   ├── app/                         # App Router関連コード
│   │    ├── layout.tsx                  # ルートレイアウト
│   │    ├── page.tsx                    # ホームページ
│   │    ├── globals.css                 # グローバルスタイル
│   │    ├── search/                     # 検索ページ
│   │    │    └── page.tsx
│   │    └── upload/                     # アップロードページ
│   │         └── page.tsx
│   │
│   ├── components/                  # Reactコンポーネント
│   │    ├── ui/                         # 共通UIコンポーネント
│   │    │    ├── Button.tsx
│   │    │    ├── Input.tsx
│   │    │    ├── Card.tsx
│   │    │    └── ...
│   │    ├── layout/                     # レイアウトコンポーネント
│   │    │    ├── Header.tsx
│   │    │    ├── Sidebar.tsx
│   │    │    └── Footer.tsx
│   │    ├── search/                     # 検索関連コンポーネント
│   │    │    ├── SearchBar.tsx
│   │    │    ├── SearchResults.tsx
│   │    │    └── ResultCard.tsx
│   │    └── upload/                     # アップロード関連コンポーネント
│   │         ├── FileUploader.tsx
│   │         └── UploadStatus.tsx
│   │
│   ├── lib/                         # ユーティリティ・API
│   │    ├── api.ts                      # API呼び出し関数
│   │    └── utils.ts                    # ユーティリティ関数
│   │
│   ├── hooks/                       # カスタムフック
│   │    ├── useSearch.ts                # 検索フック
│   │    ├── useUpload.ts                # アップロードフック
│   │    └── useDebounce.ts              # デバウンスフック
│   │
│   ├── types/                       # 型定義
│   │    ├── api.ts                      # API関連型
│   │    ├── document.ts                 # ドキュメント関連型
│   │    └── search.ts                   # 検索関連型
│   │
│   └── store/                       # Zustandストア
│        ├── searchStore.ts              # 検索状態管理
│        └── uiStore.ts                  # UI状態管理
│
├── tests/                           # フロントエンドユニットテスト
│   ├── components/                  # コンポーネントテスト
│   │    ├── ui/
│   │    │    ├── Button.test.tsx
│   │    │    └── Input.test.tsx
│   │    ├── search/
│   │    │    ├── SearchBar.test.tsx
│   │    │    └── SearchResults.test.tsx
│   │    └── upload/
│   │         └── FileUploader.test.tsx
│   ├── hooks/                       # フックテスト
│   │    ├── useSearch.test.ts
│   │    └── useUpload.test.ts
│   ├── lib/                         # ユーティリティテスト
│   │    └── api.test.ts
│   └── store/                       # ストアテスト
│        └── searchStore.test.ts
│
├── public/                          # 静的ファイル
│    ├── images/                         # 画像ファイル
│    └── favicon.ico                     # ファビコン
│
# ---- 設定ファイル群 ----
├── .eslintrc.json                   # ESLint設定
├── .prettierrc                      # Prettier設定
├── jest.config.js                   # Jestテスト設定
├── next.config.js                   # Next.js設定
├── package.json                     # 依存関係・スクリプト
├── postcss.config.js                # PostCSS設定（Tailwind用）
├── tailwind.config.ts               # Tailwind CSS設定
└── tsconfig.json                    # TypeScript設定
```

## Test Strategy

### テスト配置方針

| テスト種別 | 配置場所 | 説明 |
|-----------|---------|------|
| バックエンドユニットテスト | `backend/tests/` | 各モジュールに対応したディレクトリ構造 |
| フロントエンドユニットテスト | `frontend/tests/` | コンポーネント・フック・ストアのテスト |
| 統合テスト | `tests/integration/` | バックエンド-フロントエンド間の連携テスト |
| E2Eテスト | `tests/e2e/` | ユーザーシナリオベースのテスト |

### テスト実行コマンド

```bash
# バックエンドユニットテスト
cd backend && pytest tests/

# フロントエンドユニットテスト
cd frontend && npm test

# 統合テスト
pytest tests/integration/

# E2Eテスト
pytest tests/e2e/
```
