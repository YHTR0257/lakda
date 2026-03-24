"""HeadingContextInjector のユニットテスト"""

import pytest
from llama_index.core.schema import TextNode

from lakda.services.index.heading_context_injector import HeadingContextInjector


@pytest.fixture
def injector():
    return HeadingContextInjector()


def make_node(text: str, header_path: str = "/") -> TextNode:
    node = TextNode(text=text)
    node.metadata["header_path"] = header_path
    return node


class TestHeadingContextInjector:
    def test_root_node_no_breadcrumb(self, injector):
        """ルートレベル（header_path='/'）はパンくずなし"""
        node = make_node("# ドキュメント", header_path="/")
        result = injector([node])[0]
        assert "[セクション:" not in result.text

    def test_child_section_injects_parent(self, injector):
        """親セクション配下のノードに親名が注入される"""
        node = make_node("## 子セクション\n内容", header_path="/親セクション/")
        result = injector([node])[0]
        assert "[セクション: 親セクション > 子セクション]" in result.text

    def test_grandchild_section(self, injector):
        """3階層のパンくずが正しく生成される"""
        node = make_node("### 孫セクション\n内容B", header_path="/親/子セクション2/")
        result = injector([node])[0]
        assert "[セクション: 親 > 子セクション2 > 孫セクション]" in result.text

    def test_original_text_preserved(self, injector):
        """元のテキストがパンくずの後に残る"""
        node = make_node("## 子\n本文テキスト", header_path="/親/")
        result = injector([node])[0]
        assert "本文テキスト" in result.text

    def test_no_duplicate_in_breadcrumb(self, injector):
        """header_path と現在見出しが同じ名前の場合、パンくず内に重複しない"""
        node = make_node("## 子セクション\n内容", header_path="/親/子セクション/")
        result = injector([node])[0]
        # パンくず行（1行目）に「子セクション」は1回だけ
        breadcrumb_line = result.text.splitlines()[0]
        assert breadcrumb_line.count("子セクション") == 1
