# FT09_feedback-accumulation

## Overview

**Feature Number**: FT09
**Feature Name**: フィードバック蓄積 (Feedback Accumulation)
**Module**: feedback.py
**Category**: User Experience Enhancement
**Status**: Phase 2 Implementation

## Description
質問-回答-検索結果のセットに対するユーザー評価を記録し、将来的なシステム改善の基盤データとする機能です。Phase 2では**フィードバック収集とJSONLファイル管理**のみに注力します。

### Objectives
- 回答品質の定量評価（5段階評価 + 自由記述）
- JSONLファイルへの効率的な保存
- Phase 3でのデータ活用の基盤構築

## Technology Stack

- **言語**: Python 3.10+ (標準ライブラリのみ)
- **保存形式**: JSONL (JSON Lines)
- **依存**: なし（json, datetime, uuid, pathlibのみ使用）

### Why JSONL?
- 1レコード = 1行、ファイル末尾への追記のみ
- 機械学習ツールとの互換性（Pandas/DuckDB等）
- YAMLより10倍以上高速なパース

## Module Structure

```
src/kra/feedback.py              # フィードバック収集・保存
data/feedback/                   # データ保存先
  ├── 2026-01.jsonl             # 月次ファイル
  └── 2026-02.jsonl
```

## Data Schema

```python
# フィードバックレコード型定義
{
    "timestamp": str,            # ISO 8601形式 (例: "2026-01-04T15:30:00Z")
    "session_id": str,           # セッション識別子 (UUID4)
    "question": str,             # ユーザー質問
    "answer": str,               # 生成された回答
    "sources": [                 # 参照ドキュメント
        {
            "path": str,         # ファイルパス
            "relevance_score": float  # 0.0-1.0
        }
    ],
    "rating": int,               # 1-5評価
    "feedback_text": str | None, # 自由記述（任意）
    "domain": str                # 検索対象ドメイン
}
```

### JSONL Example
```jsonl
{"timestamp": "2026-01-04T15:30:00Z", "session_id": "a1b2c3d4", "question": "エラーE404の対処法は？", "answer": "以下を参照...", "sources": [{"path": "data/documents/error-handling/http-errors.md", "relevance_score": 0.89}], "rating": 5, "feedback_text": "完璧でした", "domain": "error-handling"}
{"timestamp": "2026-01-04T15:35:00Z", "session_id": "e5f6g7h8", "question": "OAuth2.0の実装は？", "answer": "推奨フロー...", "sources": [{"path": "data/documents/architecture/auth.md", "relevance_score": 0.92}], "rating": 3, "feedback_text": "コード例がほしい", "domain": "architecture"}
```

## Implementation Plan

### Step 1: Core Functions (src/kra/feedback.py)

```python
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict
import json
import uuid

def save_feedback(
    question: str,
    answer: str,
    sources: List[Dict[str, any]],
    rating: int,
    domain: str,
    feedback_text: Optional[str] = None
) -> None:
    """
    フィードバックをJSONLファイルに追記

    Args:
        question: ユーザー質問
        answer: 生成された回答
        sources: 参照ドキュメント情報
        rating: 1-5評価
        domain: 検索対象ドメイン
        feedback_text: 自由記述（任意）
    """
    record = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "session_id": generate_session_id(),
        "question": question,
        "answer": answer,
        "sources": sources,
        "rating": rating,
        "feedback_text": feedback_text,
        "domain": domain
    }

    file_path = get_feedback_file_path()
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with open(file_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def get_feedback_file_path() -> Path:
    """月次フィードバックファイルのパス取得 (data/feedback/YYYY-MM.jsonl)"""
    base_dir = Path(__file__).parent.parent.parent / "data" / "feedback"
    filename = datetime.utcnow().strftime("%Y-%m.jsonl")
    return base_dir / filename


def generate_session_id() -> str:
    """セッションID生成（UUID4の最初8文字）"""
    return str(uuid.uuid4())[:8]
```

### Step 2: CLI Integration (src/kra/cli/output.py)

```python
from kra.feedback import save_feedback

def display_answer_with_feedback(
    question: str,
    answer: str,
    sources: List[Dict],
    domain: str
) -> None:
    """回答表示 + フィードバック収集"""

    # 回答表示
    print("\n" + "="*50)
    print("回答:")
    print("="*50)
    print(answer)

    # ソース表示
    if sources:
        print("\n参照ドキュメント:")
        for src in sources:
            score = src.get("relevance_score", 0.0)
            print(f"  - {src['path']} (関連度: {score:.2f})")

    # フィードバック収集
    print("\n" + "-"*50)
    try:
        rating = int(input("回答を評価してください (1-5): "))
        if not 1 <= rating <= 5:
            print("警告: 1-5の範囲で入力してください")
            rating = max(1, min(5, rating))

        feedback_text = input("コメント（任意、Enterでスキップ）: ").strip()

        # 保存
        save_feedback(
            question=question,
            answer=answer,
            sources=sources,
            rating=rating,
            domain=domain,
            feedback_text=feedback_text if feedback_text else None
        )
        print("✓ フィードバックを保存しました")

    except ValueError:
        print("警告: 数値を入力してください。フィードバックはスキップされました")
    except KeyboardInterrupt:
        print("\nフィードバックをスキップしました")
```

### Step 3: Integration to main.py

```python
# src/kra/main.py での使用例
from kra.cli.output import display_answer_with_feedback

def main():
    question = input("質問を入力してください: ")

    # 回答生成（FT07連携）
    answer, sources, domain = generate_answer(question)

    # 回答表示 + フィードバック収集
    display_answer_with_feedback(
        question=question,
        answer=answer,
        sources=sources,
        domain=domain
    )
```

## Testing Strategy

### Unit Tests (tests/test_feedback.py)

```python
import json
from pathlib import Path
from datetime import datetime
from kra.feedback import save_feedback, get_feedback_file_path, generate_session_id

def test_save_feedback_creates_file(tmp_path, monkeypatch):
    """フィードバック保存がファイル生成することを確認"""
    monkeypatch.setattr("kra.feedback.Path", lambda *args: tmp_path / "data" / "feedback")

    save_feedback(
        question="テスト質問",
        answer="テスト回答",
        sources=[{"path": "test.md", "relevance_score": 0.9}],
        rating=5,
        domain="test-domain"
    )

    files = list(tmp_path.glob("**/*.jsonl"))
    assert len(files) == 1
    assert files[0].name.endswith(".jsonl")


def test_feedback_jsonl_format(tmp_path, monkeypatch):
    """JSONL形式が正しいことを確認"""
    monkeypatch.setattr("kra.feedback.Path", lambda *args: tmp_path / "data" / "feedback")

    save_feedback(
        question="Q",
        answer="A",
        sources=[],
        rating=3,
        domain="test",
        feedback_text="コメント"
    )

    file_path = list(tmp_path.glob("**/*.jsonl"))[0]
    with open(file_path, "r", encoding="utf-8") as f:
        line = f.readline()
        record = json.loads(line)

    assert "timestamp" in record
    assert record["question"] == "Q"
    assert record["rating"] == 3


def test_session_id_uniqueness():
    """セッションIDがユニークであることを確認"""
    ids = [generate_session_id() for _ in range(100)]
    assert len(set(ids)) == 100


def test_monthly_file_rotation():
    """月次ファイル名が正しいことを確認"""
    path = get_feedback_file_path()
    expected_name = datetime.utcnow().strftime("%Y-%m.jsonl")
    assert path.name == expected_name
```

## File Management

### Directory Initialization
- `data/feedback/` が存在しない場合は自動作成
- 親ディレクトリも再帰的に作成（`parents=True`）

### Monthly Rotation
- ファイル名: `YYYY-MM.jsonl` (例: `2026-01.jsonl`)
- 月が変わると自動的に新ファイルに記録
- 手動ローテーション不要

### Error Handling
- ファイル書き込み失敗時: エラーログ出力、処理継続
- 入力値不正時: バリデーション + デフォルト値適用

## Usage Example

```bash
$ python -m kra.main

質問を入力してください: エラーE500の対処法は？

==================================================
回答:
==================================================
サーバー内部エラー(E500)は以下の手順で対処します...
[回答内容]

参照ドキュメント:
  - data/documents/error-handling/server-errors.md (関連度: 0.87)

--------------------------------------------------
回答を評価してください (1-5): 4
コメント（任意、Enterでスキップ）: もう少し具体例がほしい
✓ フィードバックを保存しました
```

## Success Criteria

- [ ] `src/kra/feedback.py` の実装完了
- [ ] `src/kra/cli/output.py` への統合完了
- [ ] 単体テスト全通過（カバレッジ >90%）
- [ ] 統合テストで実際のフィードバック保存を確認
- [ ] JSONL形式の検証（jq/Pandasで読み込み可能）

## Future Enhancements (Phase 3)

Phase 2評価後、必要に応じて実装:
- 分析スクリプト（ドメイン別集計、低評価クエリ抽出）
- 週次サマリーレポート自動生成
- RAGへのフィードバック統合

## References

- Related Features: FT08 (回答表示), FT07 (回答生成)
- Data Storage: `data/feedback/*.jsonl`
- Dependencies: Python標準ライブラリのみ
