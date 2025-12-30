# Features

## Phase 2 Features (2026-01-02 - 2026-02-02)

### FT01: 質問入力
- **説明**: ユーザーがドメイン固有の質問を入力
- **実装**: CLI (`src/kra/cli/input.py`)
- **入力**: テキスト形式の質問、オプションでドメイン指定
- **出力**: 質問文字列

### FT02: ドキュメントアップロード
- **説明**: PDF/Word/Markdownファイルをシステムに取り込む
- **実装**: `data/uploads/`に直接配置
- **対応フォーマット**: PDF, DOCX, MD
- **出力**: `data/uploads/`に保存

### FT03: ドキュメント処理
- **説明**: アップロードされたファイルをMarkdownに変換
- **実装**: markdownify-mcpを使用 (`src/kra/data/processor.py`)
- **処理フロー**: PDF/Word → Markdown → `data/documents/{domain}/`
- **正規化**: ヘッダー構造、コードブロック、リンクの標準化

### FT04: ドメインメタデータ付与
- **説明**: ドキュメントにFrontmatter追加（ドメイン分類、タグ）
- **実装**: LLMによる自動生成またはマニュアル編集 (`src/kra/data/metadata.py`)
- **Frontmatter例**:
```yaml
---
domain: error-handling
tags: [python, exception, debugging]
title: "Python Exception Handling Guide"
created: 2026-01-15
---
```

### FT05: 質問解釈
- **説明**: 曖昧な質問を具体化
- **実装**: Gemini CLIにプロンプトテンプレート渡し (`src/kra/processing/interpreter.py`)
- **例**:
  - 入力: "エラーが出た"
  - 出力: "Pythonで発生したAttributeErrorの原因と解決方法は？"

### FT06: ドメイン別検索
- **説明**: 関連ドキュメントをハイブリッド検索（BM25 + Semantic）
- **実装**: Gemini CLIが内部でmcp-markdown-ragdocs呼び出し
- **検索範囲**: `config/config.toml`で指定
- **パラメータ**: `semantic_weight`, `keyword_weight`

### FT07: 回答生成
- **説明**: 検索結果から引用元付き回答を生成
- **実装**: Gemini CLI (`src/kra/processing/generator.py`経由)
- **出力形式**:
  - 回答本文
  - 引用元（ファイル名、行番号）
  - 信頼度スコア（オプション）

### FT08: 回答出力
- **説明**: 生成された回答をユーザーに表示
- **実装**: CLI出力 (`src/kra/cli/output.py`)
- **表示内容**: 回答、引用元リスト、フィードバックプロンプト

### FT09: フィードバック記録
- **説明**: ユーザーの回答評価（有用/無用）を記録
- **実装**: ローカルファイル保存 (`src/kra/utils/feedback.py`)
- **保存先**: `data/feedback/`
- **フォーマット**: JSON（質問、回答、評価、タイムスタンプ）

---

## Phase 3 Features (2026-02-02 - 2026-03-31) - 条件付き実装

### FT10: ドメイン設定管理
- **説明**: ドメインと検索対象を明示的に管理
- **実装条件**: カスタムMCPサーバー実装時のみ
- **設定ファイル**: `config/domains.yml`
- **機能**: ドメインごとの重み付け、タグフィルタリング

### FT11: 外部API連携
- **説明**: Gemini API、Glean API、Local LLM連携
- **実装**: `src/kra/api/gateway.py`
- **機能**: APIラッパー、レート制限、リトライ処理

### FT12: オーケストレーター
- **説明**: 複数エージェント（解釈・検索・生成）の統合管理
- **実装**: LangGraph/LangChain (`src/kra/orchestrator/orchestrator.py`)
- **機能**: タスク分配、エージェント間通信、結果統合

### FT13: エージェント実装
- **説明**: 専門タスク担当エージェント
- **実装**: `src/kra/orchestrator/agents/`
- **エージェント種類**:
  - Interpreter Agent: 質問解釈
  - Retrieval Agent: 情報検索
  - Generator Agent: 回答生成

---

## Feature Dependencies

```
FT01 (質問入力)
  ↓
FT05 (質問解釈) → Gemini CLI
  ↓
FT06 (検索) → mcp-markdown-ragdocs
  ↓
FT07 (回答生成) → Gemini CLI
  ↓
FT08 (回答出力)
  ↓
FT09 (フィードバック記録)
```

```
FT02 (アップロード)
  ↓
FT03 (変換) → markdownify-mcp
  ↓
FT04 (メタデータ) → LLM
  ↓
data/documents/{domain}/
```
