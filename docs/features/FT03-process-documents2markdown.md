# FT03: Document Processing - Design Document

## Overview

**Feature ID**: FT03
**Feature Name**: ドキュメント処理 (Document Processing)
**Description**: アップロードされたドキュメント(PDF, Word, Excel, PowerPoint等)をMarkdown形式に変換・正規化する機能
**Implementation Phase**: Phase 2
**Library**: [markitdown](https://github.com/microsoft/markitdown) (Microsoft製のPythonライブラリ)

## Objectives

1. 様々なフォーマット(PDF, DOCX, XLSX, PPTX等)のドキュメントをMarkdown形式に統一変換する
2. 変換後のMarkdownファイルを適切なドメインディレクトリに保存する
3. 変換エラーを適切にハンドリングし、ログを記録する
4. Phase 2のシンプルな実装方針に従い、必要最小限の機能を実装する

## Technology Selection

### markitdown Library

Microsoft製のPythonライブラリで、以下の特徴を持つ:

**サポートフォーマット**:
- PDF (.pdf)
- Word (.docx)
- PowerPoint (.pptx)
- Excel (.xlsx)
- HTML (.html)
- 画像 (.jpg, .png) - OCR機能あり
- 音声 (.mp3, .wav) - 文字起こし機能あり
- CSV (.csv)
- JSON (.json)
- XML (.xml)

**特徴**:
- シンプルなAPI (`MarkItDown().convert(file_path)`)
- Pythonライブラリとして直接importして使用可能
- 依存ライブラリが少ない
- Microsoft製で継続的なメンテナンスが期待できる

**選定理由**:
- Phase 2の方針「MarkItDown Pythonライブラリを直接使用」に合致
- MCPサーバー経由ではなくPythonコードから直接呼び出し可能
- 多様なフォーマットに対応しており、将来的な拡張性が高い

## Architecture Design

### Module Structure

```
src/data/processor.py (コアロジック)
├── DocumentProcessor (メインクラス)
│   ├── __init__()                    # 初期化
│   ├── convert_file()                # 単一ファイル変換
│   ├── convert_directory()           # ディレクトリ一括変換
│   ├── _save_markdown()              # Markdown保存
│   └── _generate_filename()          # 出力ファイル名生成
│
├── SupportedFormat (Enum)            # サポートフォーマット定義
│
└── ConversionResult (Pydantic Model) # 変換結果データモデル

scripts/convert_documents.py (CLIエントリーポイント)
└── main()                            # CLI実行用エントリーポイント
```

### Data Flow

```mermaid
graph LR
    A[Upload File<br/>data/uploads/] --> B[DocumentProcessor]
    B --> C{Format Check}
    C -->|Supported| D[markitdown.convert()]
    C -->|Unsupported| E[Error Log]
    D --> F{Conversion Success?}
    F -->|Yes| G[Save to<br/>data/documents/{domain}/]
    F -->|No| E
    G --> H[ConversionResult<br/>success=True]
    E --> I[ConversionResult<br/>success=False]
```

### Directory Structure

**入力元**:
```
data/uploads/
├── document1.pdf
├── document2.docx
├── document3.xlsx
└── presentation.pptx
```

**出力先**:
```
data/documents/
├── error-handling/
│   └── document1.md
├── architecture/
│   └── document2.md
├── api-guides/
│   └── document3.md
└── business-logic/
    └── presentation.md
```

## Implementation Details

### 1. Class Definitions

#### SupportedFormat Enum

```python
from enum import Enum

class SupportedFormat(str, Enum):
    """サポートされるドキュメントフォーマット"""
    PDF = ".pdf"
    DOCX = ".docx"
    XLSX = ".xlsx"
    PPTX = ".pptx"
    HTML = ".html"
    TXT = ".txt"
    CSV = ".csv"
    JSON = ".json"
    XML = ".xml"
    # 画像・音声は Phase 2 では対象外（必要に応じて追加）
```

#### ConversionResult Model

```python
from pydantic import BaseModel, Field
from pathlib import Path
from typing import Optional

class ConversionResult(BaseModel):
    """ドキュメント変換結果"""
    success: bool = Field(..., description="変換成功フラグ")
    source_path: Path = Field(..., description="変換元ファイルパス")
    output_path: Optional[Path] = Field(None, description="変換後ファイルパス")
    error_message: Optional[str] = Field(None, description="エラーメッセージ")
    markdown_content: Optional[str] = Field(None, description="変換後Markdownコンテンツ")
```

### 2. DocumentProcessor Class (src/data/processor.py)

#### Main Methods

```python
from pathlib import Path
from typing import List, Optional
from markitdown import MarkItDown
import logging

class DocumentProcessor:
    """ドキュメント変換処理クラス"""

    def __init__(
        self,
        uploads_dir: Path = Path("data/uploads"),
        documents_dir: Path = Path("data/documents"),
        default_domain: str = "general"
    ):
        """
        初期化

        Args:
            uploads_dir: アップロード元ディレクトリ
            documents_dir: 変換後ドキュメント保存先ディレクトリ
            default_domain: デフォルトドメイン名
        """
        self.uploads_dir = uploads_dir
        self.documents_dir = documents_dir
        self.default_domain = default_domain
        self.converter = MarkItDown()
        self.logger = logging.getLogger(__name__)

        # ディレクトリ存在確認
        self.uploads_dir.mkdir(parents=True, exist_ok=True)
        self.documents_dir.mkdir(parents=True, exist_ok=True)

    def convert_file(
        self,
        file_path: Path,
        domain: Optional[str] = None,
        output_filename: Optional[str] = None
    ) -> ConversionResult:
        """
        単一ファイルをMarkdownに変換

        Args:
            file_path: 変換対象ファイルパス
            domain: 保存先ドメイン名（Noneの場合はdefault_domain）
            output_filename: 出力ファイル名（Noneの場合は元のファイル名を使用）

        Returns:
            ConversionResult: 変換結果
        """
        pass  # Implementation details below

    def convert_directory(
        self,
        source_dir: Optional[Path] = None,
        domain: Optional[str] = None
    ) -> List[ConversionResult]:
        """
        ディレクトリ内の全ファイルを一括変換

        Args:
            source_dir: 変換対象ディレクトリ（Noneの場合はuploads_dir）
            domain: 保存先ドメイン名（Noneの場合はdefault_domain）

        Returns:
            List[ConversionResult]: 変換結果リスト
        """
        pass  # Implementation details below

    def _save_markdown(
        self,
        content: str,
        output_path: Path
    ) -> None:
        """
        Markdownコンテンツをファイルに保存

        Args:
            content: Markdownコンテンツ
            output_path: 保存先パス
        """
        pass

    def _generate_filename(
        self,
        original_path: Path,
        custom_name: Optional[str] = None
    ) -> str:
        """
        出力ファイル名を生成

        Args:
            original_path: 元のファイルパス
            custom_name: カスタムファイル名

        Returns:
            str: 出力ファイル名（.md拡張子付き）
        """
        pass

    def _is_supported_format(self, file_path: Path) -> bool:
        """
        サポートされているフォーマットかチェック

        Args:
            file_path: チェック対象ファイルパス

        Returns:
            bool: サポートされている場合True
        """
        return file_path.suffix.lower() in [fmt.value for fmt in SupportedFormat]
```

### 3. Implementation Logic

#### convert_file() メソッド

```python
def convert_file(
    self,
    file_path: Path,
    domain: Optional[str] = None,
    output_filename: Optional[str] = None
) -> ConversionResult:
    """単一ファイルをMarkdownに変換"""

    # 1. ファイル存在確認
    if not file_path.exists():
        return ConversionResult(
            success=False,
            source_path=file_path,
            error_message=f"File not found: {file_path}"
        )

    # 2. フォーマットサポート確認
    if not self._is_supported_format(file_path):
        return ConversionResult(
            success=False,
            source_path=file_path,
            error_message=f"Unsupported format: {file_path.suffix}"
        )

    try:
        # 3. markitdownで変換
        result = self.converter.convert(str(file_path))
        markdown_content = result.text_content

        # 4. 出力先パス生成
        target_domain = domain or self.default_domain
        domain_dir = self.documents_dir / target_domain
        domain_dir.mkdir(parents=True, exist_ok=True)

        filename = self._generate_filename(file_path, output_filename)
        output_path = domain_dir / filename

        # 5. Markdown保存
        self._save_markdown(markdown_content, output_path)

        self.logger.info(f"Successfully converted: {file_path} → {output_path}")

        return ConversionResult(
            success=True,
            source_path=file_path,
            output_path=output_path,
            markdown_content=markdown_content
        )

    except Exception as e:
        self.logger.error(f"Conversion failed: {file_path}, Error: {str(e)}")
        return ConversionResult(
            success=False,
            source_path=file_path,
            error_message=str(e)
        )
```

#### convert_directory() メソッド

```python
def convert_directory(
    self,
    source_dir: Optional[Path] = None,
    domain: Optional[str] = None
) -> List[ConversionResult]:
    """ディレクトリ内の全ファイルを一括変換"""

    source = source_dir or self.uploads_dir

    if not source.exists():
        self.logger.error(f"Source directory not found: {source}")
        return []

    results = []

    # サポートされている拡張子のファイルのみ処理
    supported_extensions = [fmt.value for fmt in SupportedFormat]

    for file_path in source.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
            result = self.convert_file(file_path, domain=domain)
            results.append(result)

    # サマリーログ
    success_count = sum(1 for r in results if r.success)
    total_count = len(results)
    self.logger.info(
        f"Batch conversion completed: {success_count}/{total_count} files succeeded"
    )

    return results
```

#### Helper Methods

```python
def _save_markdown(self, content: str, output_path: Path) -> None:
    """Markdownコンテンツをファイルに保存"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)

def _generate_filename(
    self,
    original_path: Path,
    custom_name: Optional[str] = None
) -> str:
    """出力ファイル名を生成"""
    if custom_name:
        # カスタム名が指定されている場合
        base_name = custom_name
    else:
        # 元のファイル名を使用（拡張子を除く）
        base_name = original_path.stem

    # .md拡張子を付与
    return f"{base_name}.md"
```

### 4. CLI Script (scripts/convert_documents.py)

**Note**: CLIは`click`ライブラリを使用して実装します。

```python
#!/usr/bin/env python3
"""
Document Conversion CLI Script

Usage:
    # 単一ファイル変換
    python scripts/convert_documents.py data/uploads/document.pdf -d error-handling

    # カスタムファイル名指定
    python scripts/convert_documents.py data/uploads/document.pdf -d architecture -o custom_name

    # ディレクトリ一括変換
    python scripts/convert_documents.py data/uploads/ -d api-guides -v
"""

import sys
from pathlib import Path

import click

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from data.processor import DocumentProcessor


@click.command()
@click.argument(
    "input_path",
    type=click.Path(exists=True, path_type=Path),
)
@click.option(
    "-d", "--domain",
    type=str,
    default="general",
    show_default=True,
    help="Target domain directory"
)
@click.option(
    "-o", "--output",
    type=str,
    help="Custom output filename (without extension)"
)
@click.option(
    "-v", "--verbose",
    is_flag=True,
    help="Enable verbose output"
)
def main(input_path: Path, domain: str, output: str, verbose: bool):
    """
    Convert documents to Markdown format.

    INPUT_PATH: Input file or directory path to convert

    \b
    Examples:
      # 単一ファイル変換
      python scripts/convert_documents.py data/uploads/document.pdf -d error-handling

      # カスタムファイル名指定
      python scripts/convert_documents.py data/uploads/document.pdf -d architecture -o custom_name

      # ディレクトリ一括変換（詳細表示）
      python scripts/convert_documents.py data/uploads/ -d api-guides -v
    """
    # ログレベル設定
    if verbose:
        import logging
        logging.basicConfig(level=logging.INFO)

    # DocumentProcessorインスタンス作成
    processor = DocumentProcessor()

    # ファイル vs ディレクトリ判定
    if input_path.is_file():
        # 単一ファイル変換
        result = processor.convert_file(
            input_path,
            domain=domain,
            output_filename=output
        )

        if result.success:
            click.secho("✓ Conversion succeeded", fg="green")
            click.echo(f"  Source: {result.source_path}")
            click.echo(f"  Output: {result.output_path}")
        else:
            click.secho("✗ Conversion failed", fg="red")
            click.echo(f"  Source: {result.source_path}")
            click.echo(f"  Error: {result.error_message}")
            sys.exit(1)

    elif input_path.is_dir():
        # ディレクトリ一括変換
        results = processor.convert_directory(input_path, domain=domain)

        success_count = sum(1 for r in results if r.success)
        total_count = len(results)

        click.echo("\nBatch Conversion Results:")
        click.echo(f"  Total: {total_count} files")
        click.secho(f"  Success: {success_count} files", fg="green")
        if success_count < total_count:
            click.secho(f"  Failed: {total_count - success_count} files", fg="red")

        # 詳細表示
        if verbose:
            click.echo("\nDetails:")
            for result in results:
                if result.success:
                    click.secho(f"  ✓ {result.source_path.name}", fg="green")
                else:
                    click.secho(f"  ✗ {result.source_path.name}", fg="red")
                    click.echo(f"    Error: {result.error_message}")

        if success_count < total_count:
            sys.exit(1)

    else:
        click.secho(f"Error: {input_path} is neither a file nor a directory", fg="red")
        sys.exit(1)


if __name__ == "__main__":
    main()
```

## Configuration

### Logging Configuration

```python
# src/data/processor.py の冒頭に追加

import logging
from pathlib import Path

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/document_processor.log'),
        logging.StreamHandler()
    ]
)
```

### Directory Structure Setup

```bash
# Phase 2 セットアップ時に実行
mkdir -p data/uploads
mkdir -p data/documents/error-handling
mkdir -p data/documents/architecture
mkdir -p data/documents/api-guides
mkdir -p data/documents/business-logic
mkdir -p logs
```

## Usage Examples

### Example 1: Pythonコードから使用

```python
from pathlib import Path
from src.data.processor import DocumentProcessor

processor = DocumentProcessor()

# PDFファイルをerror-handlingドメインに変換
result = processor.convert_file(
    file_path=Path("data/uploads/error_guide.pdf"),
    domain="error-handling"
)

if result.success:
    print(f"変換成功: {result.output_path}")
else:
    print(f"変換失敗: {result.error_message}")
```

### Example 2: ディレクトリ一括変換

```python
from pathlib import Path
from src.data.processor import DocumentProcessor

processor = DocumentProcessor()

# data/uploads/ 内の全ファイルをarchitectureドメインに変換
results = processor.convert_directory(domain="architecture")

for result in results:
    if result.success:
        print(f"✓ {result.source_path.name} → {result.output_path}")
    else:
        print(f"✗ {result.source_path.name}: {result.error_message}")
```

### Example 3: CLIスクリプトから実行（click使用）

```bash
# 単一ファイル変換
python scripts/convert_documents.py data/uploads/document.pdf -d error-handling

# カスタムファイル名指定
python scripts/convert_documents.py data/uploads/document.pdf -d architecture -o custom_name

# ディレクトリ一括変換（詳細表示）
python scripts/convert_documents.py data/uploads/ -d api-guides -v

# ヘルプ表示
python scripts/convert_documents.py --help
```

**Output Example**:
```
✓ Conversion succeeded
  Source: data/uploads/document.pdf
  Output: data/documents/error-handling/document.md
```

## Dependencies

### Required Libraries

```toml
# pyproject.toml に追加
[project]
dependencies = [
    # ... existing dependencies ...
    "markitdown>=0.0.1",  # ドキュメント変換
]
```

### Installation

```bash
# markitdown をインストール
uv add markitdown

# または既存の依存関係と一緒にインストール
uv sync
```

## Testing Strategy

### Unit Tests

```python
# tests/test_processor.py

import pytest
from pathlib import Path
from src.data.processor import DocumentProcessor, SupportedFormat, ConversionResult

@pytest.fixture
def processor():
    """テスト用のDocumentProcessorインスタンス"""
    return DocumentProcessor(
        uploads_dir=Path("tests/fixtures/uploads"),
        documents_dir=Path("tests/fixtures/documents")
    )

def test_supported_format_check(processor):
    """サポートフォーマットのチェック"""
    assert processor._is_supported_format(Path("test.pdf")) == True
    assert processor._is_supported_format(Path("test.docx")) == True
    assert processor._is_supported_format(Path("test.xyz")) == False

def test_generate_filename(processor):
    """ファイル名生成のテスト"""
    assert processor._generate_filename(Path("test.pdf")) == "test.md"
    assert processor._generate_filename(Path("test.pdf"), "custom") == "custom.md"

def test_convert_file_success(processor, tmp_path):
    """ファイル変換成功のテスト"""
    # テスト用のサンプルファイルを作成
    test_file = tmp_path / "test.txt"
    test_file.write_text("Test content")

    result = processor.convert_file(test_file, domain="test-domain")

    assert result.success == True
    assert result.output_path is not None
    assert result.markdown_content is not None

def test_convert_file_not_found(processor):
    """存在しないファイルの変換テスト"""
    result = processor.convert_file(Path("nonexistent.pdf"))

    assert result.success == False
    assert "not found" in result.error_message.lower()

def test_convert_directory(processor, tmp_path):
    """ディレクトリ一括変換のテスト"""
    # テスト用のファイルを複数作成
    (tmp_path / "test1.txt").write_text("Content 1")
    (tmp_path / "test2.txt").write_text("Content 2")

    results = processor.convert_directory(tmp_path, domain="test-domain")

    assert len(results) == 2
    assert all(r.success for r in results)
```

### Integration Tests

```python
# tests/test_integration_processor.py

def test_end_to_end_conversion():
    """エンドツーエンドの変換フローテスト"""
    # 1. DocumentProcessorを初期化
    processor = DocumentProcessor()

    # 2. サンプルPDFをアップロード（テストフィクスチャ）
    sample_pdf = Path("tests/fixtures/sample.pdf")

    # 3. 変換実行
    result = processor.convert_file(sample_pdf, domain="error-handling")

    # 4. 検証
    assert result.success == True
    assert result.output_path.exists()
    assert result.markdown_content is not None
    assert len(result.markdown_content) > 0
```

## Error Handling

### Error Types

| Error Type | Handling Strategy | User Impact |
|-----------|------------------|-------------|
| File Not Found | ログ記録 + エラーメッセージ返却 | 変換失敗通知 |
| Unsupported Format | ログ記録 + サポートフォーマットリスト表示 | フォーマット選択ガイド |
| Conversion Failure | ログ記録 + 詳細エラーメッセージ | リトライ推奨 |
| Permission Error | ログ記録 + 権限エラーメッセージ | 管理者連絡推奨 |
| Disk Space Error | ログ記録 + ディスク容量不足警告 | ストレージクリーンアップ推奨 |

### Error Logging Format

```python
# ログフォーマット例
# 2026-01-01 15:30:45 - processor - ERROR - Conversion failed: /path/to/file.pdf, Error: Permission denied
# 2026-01-01 15:30:46 - processor - INFO - Successfully converted: /path/to/file.docx → /path/to/output.md
```

## Performance Considerations

### Phase 2 Constraints
- **同期処理**: Phase 2では非同期処理は実装せず、シンプルな同期処理
- **バッチサイズ**: ディレクトリ一括変換時は全ファイルを一度に処理（Phase 3で最適化検討）
- **メモリ使用**: 大容量ファイルは一時的にメモリを消費する可能性あり

### Future Optimizations (Phase 3)
- 非同期処理 (asyncio) による並列変換
- プログレスバー表示
- 変換キューシステム
- チャンク処理による大容量ファイル対応

## Integration with Other Modules

### FT02 (uploader.py) との連携

```python
# src/data/uploader.py から processor を呼び出す例

from src.data.processor import DocumentProcessor

def upload_and_convert(file_path: Path, domain: str):
    """アップロード後に自動的に変換"""
    # 1. ファイルをdata/uploads/にコピー（uploader.pyの役割）
    # ...

    # 2. 自動的にMarkdownに変換
    processor = DocumentProcessor()
    result = processor.convert_file(file_path, domain=domain)

    return result
```

### FT04 (metadata.py) との連携

```python
# processor.py の convert_file() に追加

from src.data.metadata import MetadataGenerator

def convert_file(self, file_path: Path, domain: Optional[str] = None,
                 add_metadata: bool = True) -> ConversionResult:
    """変換後にメタデータを自動付与"""
    result = self.convert_file(file_path, domain)

    if result.success and add_metadata:
        # FT04: メタデータ自動付与
        metadata_generator = MetadataGenerator()
        metadata_generator.add_frontmatter(result.output_path)

    return result
```

## Acceptance Criteria

### Definition of Done

- [ ] markitdown ライブラリがインストールされている
- [ ] DocumentProcessor クラスが実装されている
- [ ] 以下のメソッドが正常に動作する:
  - [ ] `convert_file()` - 単一ファイル変換
  - [ ] `convert_directory()` - ディレクトリ一括変換
  - [ ] `_is_supported_format()` - フォーマットチェック
- [ ] サポートフォーマット（PDF, DOCX, XLSX, PPTX等）が正常に変換される
- [ ] 変換エラーが適切にハンドリングされ、ログに記録される
- [ ] ユニットテストが実装され、全てパスする
- [ ] CLI経由での手動実行が可能（`scripts/convert_documents.py`）
- [ ] ドキュメントが `docs/FT03-process-documents2markdown.md` に記載されている

### Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| 変換成功率 | >95% | (成功数 / 全変換試行数) × 100 |
| サポートフォーマット数 | 5種類以上 | PDF, DOCX, XLSX, PPTX, HTML |
| エラーハンドリング網羅率 | 100% | 全エラーケースでログ記録 + メッセージ返却 |
| 平均変換時間（小サイズファイル） | <5秒 | 1MB以下のファイル |

## Implementation Timeline

| Task | Estimated Time | Priority |
|------|---------------|----------|
| markitdown インストール | 5分 | High |
| SupportedFormat Enum 実装 | 10分 | High |
| ConversionResult Model 実装 | 15分 | High |
| DocumentProcessor クラス骨格 | 30分 | High |
| convert_file() メソッド実装 | 1時間 | High |
| convert_directory() メソッド実装 | 30分 | High |
| エラーハンドリング実装 | 30分 | High |
| ログ設定 | 15分 | Medium |
| CLI スクリプト実装 (scripts/convert_documents.py) | 30分 | Medium |
| ユニットテスト実装 | 1.5時間 | High |
| 統合テスト実装 | 1時間 | Medium |
| ドキュメント作成（本ファイル） | 完了 | High |

**Total Estimated Time**: 約6時間

## Risks and Mitigation

### Risk 1: markitdown ライブラリの変換精度が低い

**Impact**: 変換後のMarkdownが不正確で、検索精度が低下

**Mitigation**:
- Phase 2 Week 1での早期評価（サンプルファイル3-5件で検証）
- 変換後のMarkdownを目視確認し、精度を評価
- 必要に応じて代替ライブラリ（pypdf, python-docx等）を検討

### Risk 2: 大容量ファイルでメモリエラーが発生

**Impact**: 変換処理が途中で失敗

**Mitigation**:
- Phase 2では小〜中サイズファイル（<10MB）のみを対象とする
- エラーハンドリングで適切なメッセージを返す
- Phase 3でチャンク処理を実装

### Risk 3: 特定フォーマットで変換が失敗する

**Impact**: 一部のドキュメントが変換できない

**Mitigation**:
- サポートフォーマットを明示的に定義（SupportedFormat Enum）
- 非サポートフォーマットは事前にチェックして弾く
- エラーログに詳細情報を記録し、原因を特定しやすくする

## References

- [markitdown GitHub Repository](https://github.com/microsoft/markitdown)
- [project_design.md](./project_design.md) - FT03の位置づけ
- [Phase 2 Architecture](./project_design.md#phase-2-architecture-current-target)

## Changelog

| Date | Version | Changes |
|------|---------|---------|
| 2026-01-01 | 1.0 | 初版作成 - CLIスクリプトをscripts/に配置 |
| 2026-01-01 | 1.1 | CLIをargparseからclickに変更 - カラー出力、型安全性向上 |
