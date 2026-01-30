# MCPサーバーセットアップガイド (Phase 2)

## 概要

**使用するMCPサーバー**:
- **MCP-Markdown-RAG** (Zackriya-Solutions): Markdownドキュメントのセマンティック検索 (Python + uv) - MCPサーバーとして使用

**フロー**:
- 質問応答: `main.py` → `Gemini CLI` → `MCP-Markdown-RAG`

**インストール先**:
- MCP-Markdown-RAG: `~/dev/mcp-servers/` (プロジェクト外)

## 前提条件

**必要なソフトウェア**:
- Python 3.10+ (uvで管理)
- uv: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Node.js 18+: `brew install node` (Gemini CLI用)

**確認コマンド**:
```zsh
python3 --version  # 3.10+
uv --version
node --version     # v18+ (Gemini CLI用)
```

## セットアップ手順

### 1. 基本環境構築

```zsh
# 自動セットアップ (推奨)
bash scripts/setup.sh

# または手動セットアップ
uv sync  # pyproject.tomlからMarkItDownを含む全依存関係をインストール
mkdir -p data/{uploads,feedback,documents/{error-handling,architecture,api-guides,business-logic},logs}
cp config/example/*.example config/  # .exampleを削除してリネーム
```

### 2. Gemini CLIのインストール

```zsh
npm install -g @google/gemini-cli
which gemini  # パスを確認

# zshの場合、パスが通らない場合は以下を ~/.zshrc に追加
# export PATH="$HOME/.npm-global/bin:$PATH"
```

### 3. MCP-Markdown-RAGのセットアップ

**インストール先**: `~/dev/mcp-servers/` (プロジェクト外に配置)

#### 3-1. MCP-Markdown-RAGのインストール

```zsh
# MCPサーバー用ディレクトリを作成
mkdir -p ~/dev/mcp-servers
cd ~/dev/mcp-servers

# MCP-Markdown-RAGをクローン
git clone https://github.com/Zackriya-Solutions/MCP-Markdown-RAG.git
cd MCP-Markdown-RAG

# uv で依存関係をインストール
uv sync
```

**注意**: 初回実行時に埋め込みモデル(約50MB)をダウンロードするため時間がかかります。

#### 3-2. シンボリックリンクの作成 (重要)

MCP-Markdown-RAG/server.py:59の制約を回避するため、シンボリックリンクを作成します:

```zsh
cd ~/dev/mcp-servers/MCP-Markdown-RAG
ln -s ~/dev/github/YHTR0257/lakda/data/documents documents

# 確認
ls -l documents  # シンボリックリンクが作成されていることを確認
```

**理由**: `server.py:59`の`target_path = os.path.join(current_working_directory, directory)`がMCPサーバーの実行ディレクトリを基準にするため、外部レポジトリを改変せずにドキュメントを参照可能にします。

#### 3-3. インストール確認

```zsh
# MCP-Markdown-RAGの確認
ls ~/dev/mcp-servers/MCP-Markdown-RAG/pyproject.toml

# シンボリックリンクの確認
ls -l ~/dev/mcp-servers/MCP-Markdown-RAG/documents
```

## 設定ファイル

### MCPサーバー設定 (`config/mcp_config.json`)

MCP-Markdown-RAGの設定:

```json
{
  "mcpServers": {
    "markdown-rag": {
      "command": "uv",
      "args": [
        "--directory",
        "/Users/YOUR_USERNAME/dev/mcp-servers/MCP-Markdown-RAG",
        "run",
        "mcp-markdown-rag"
      ]
    }
  }
}
```

**重要**: `YOUR_USERNAME` を実際のユーザー名に置き換えてください。`echo $HOME` で確認できます。

## ドメイン管理

Phase 2は**ディレクトリ構造ベース**の暗黙的管理:

```
data/documents/
├── error-handling/     # エラーハンドリング
├── architecture/       # アーキテクチャ設計
├── api-guides/         # API利用ガイド
└── business-logic/     # ビジネスロジック
```

**特定ドメインのみ検索**: `config/config.toml` で `paths` を設定

## 検証

```zsh
# Python環境
uv run lakda --help

# Gemini CLI
gemini --version
gemini login  # Web認証 (Phase 2で必須)
```

## トラブルシューティング

| 問題 | 解決方法 |
|------|---------|
| Gemini CLIが見つからない | `npm install -g @google/gemini-cli`<br/>`which gemini` でパス確認 |
| MCP-Markdown-RAGの埋め込みモデルダウンロード失敗 | インターネット接続確認<br/>初回実行時に自動ダウンロード(約50MB) |
| シンボリックリンクが作成できない | パスを確認: `ls ~/dev/github/YHTR0257/lakda/data/documents`<br/>権限を確認: `ls -l ~/dev/mcp-servers/MCP-Markdown-RAG/` |
| MarkItDownライブラリのインポートエラー | `uv sync` で依存関係を再同期<br/>pyproject.tomlにmarkitdownが含まれていることを確認 |

## 次のステップ

1. **MCP-Markdown-RAGのインストールとシンボリックリンク作成**: 上記の手順3を実行
2. **Gemini CLIログイン**: `gemini login` でWeb認証
3. **設定ファイルの作成**: `config/mcp_config.json` と `config/config.toml` を設定
4. **サンプルドキュメント配置**: `data/documents/{domain}/` にMarkdownファイルを配置
5. **インデックス作成**: `gemini chat --mcp config/mcp_config.json -c "Index documents in ./documents"`
6. **動作確認**: `uv run python -m lakda.main` でアプリケーション起動確認

## リソース

**使用中の技術**:
- [MCP-Markdown-RAG](https://github.com/Zackriya-Solutions/MCP-Markdown-RAG) - Markdownセマンティック検索 (MCPサーバー)

**関連ドキュメント**:
- [Model Context Protocol公式](https://modelcontextprotocol.io/)
- [MCP公式サーバーリスト](https://github.com/modelcontextprotocol/servers)
- [Gemini CLIドキュメント](https://ai.google.dev/gemini-api/docs/cli)
- [uv Documentation](https://docs.astral.sh/uv/)

## Phase 2評価基準

MCP-Markdown-RAGの使用で以下を評価:

1. **シンボリックリンク方式**: 本番運用で問題ないか、絶対パス対応が必要か
2. **ドメイン検索精度**: ディレクトリ構造ベースの暗黙的ドメイン管理で十分か (目標: Top 3含有率 >80%)
3. **設定柔軟性**: config.toml の設定項目で要件を満たせるか
4. **必要な拡張機能**: Frontmatterフィルタリング、ドメイン重み付けの必要性

## Phase 3への移行 (条件付き)

Phase 2評価結果に応じて実装を検討:
- **Option A**: MCP-Markdown-RAGを継続使用 (要件を満たす場合)
- **Option C**: MCP-Markdown-RAGをフォーク (server.py:59を1行修正、絶対パス対応のみ必要な場合)
- **Option B**: カスタムRAG実装 (markdownファイル + sentence-transformers + FAISS、大幅カスタマイズが必要な場合、2-3週間)
- 明示的ドメイン管理 (`config/domains.yml`)
- Gemini API統合
