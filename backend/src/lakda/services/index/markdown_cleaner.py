"""Markdown 記号除去ユーティリティ

PropertyGraph のエンティティ抽出前に Markdown の装飾記号を取り除き、
LLM が純粋なテキストとしてエンティティを認識できるようにします。
"""

import re


def clean_markdown(text: str) -> str:
    """Markdown 記号を除去してプレーンテキストに変換する

    以下を処理します:
    - 見出し記号 (# ## ### ...)
    - 太字・斜体 (**text**, *text*, __text__, _text_)
    - インラインコード (`code`)
    - コードブロック (```...```)
    - 水平線 (---, ***)
    - リスト記号 (- item, * item, 1. item)
    - リンク・画像 ([text](url), ![alt](url))
    - 引用 (> text)
    - HTMLタグ (<tag>)

    Args:
        text: Markdown テキスト

    Returns:
        プレーンテキスト
    """
    # コードブロック（```...```）→ 中身だけ残す
    text = re.sub(r"```[^\n]*\n(.*?)```", r"\1", text, flags=re.DOTALL)

    # インラインコード（`code`）→ code
    text = re.sub(r"`([^`]+)`", r"\1", text)

    # 見出し記号（# ## ### ...）→ 後続テキストだけ残す
    text = re.sub(r"^#{1,6}\s+", "", text, flags=re.MULTILINE)

    # 太字+斜体（***text***）
    text = re.sub(r"\*{3}([^*]+)\*{3}", r"\1", text)

    # 太字（**text** または __text__）
    text = re.sub(r"\*{2}([^*]+)\*{2}", r"\1", text)
    text = re.sub(r"_{2}([^_]+)_{2}", r"\1", text)

    # 斜体（*text* または _text_）
    text = re.sub(r"\*([^*]+)\*", r"\1", text)
    text = re.sub(r"_([^_]+)_", r"\1", text)

    # 水平線（--- または ***）→ 除去
    text = re.sub(r"^[-*]{3,}\s*$", "", text, flags=re.MULTILINE)

    # リンク（[text](url)）→ text
    text = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", text)

    # 引用（> text）→ text
    text = re.sub(r"^>\s*", "", text, flags=re.MULTILINE)

    # リスト記号（- / * / 1. 等）→ 除去
    text = re.sub(r"^[\-*+]\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\d+\.\s+", "", text, flags=re.MULTILINE)

    # HTMLタグ → 除去
    text = re.sub(r"<[^>]+>", "", text)

    # 連続する空行を1行に圧縮
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()
