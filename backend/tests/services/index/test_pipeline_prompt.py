from lakda.services.index.pipeline import _JA_KG_TRIPLET_EXTRACT_PROMPT


class TestJaKgTripletExtractPrompt:
    def test_has_required_variable_max_knowledge_triplets(self):
        assert "{max_knowledge_triplets}" in _JA_KG_TRIPLET_EXTRACT_PROMPT.template

    def test_has_required_variable_text(self):
        assert "{text}" in _JA_KG_TRIPLET_EXTRACT_PROMPT.template

    def test_contains_japanese_instructions(self):
        assert "日本語" in _JA_KG_TRIPLET_EXTRACT_PROMPT.template

    def test_contains_snake_case_example(self):
        assert "snake_case" in _JA_KG_TRIPLET_EXTRACT_PROMPT.template

    def test_format_fills_variables(self):
        result = _JA_KG_TRIPLET_EXTRACT_PROMPT.format(
            max_knowledge_triplets=5,
            text="Python はプログラミング言語です。",
        )
        assert "5" in result
        assert "Python はプログラミング言語です。" in result

    def test_no_leftover_placeholders_after_format(self):
        result = _JA_KG_TRIPLET_EXTRACT_PROMPT.format(
            max_knowledge_triplets=3,
            text="テストテキスト",
        )
        assert "{max_knowledge_triplets}" not in result
        assert "{text}" not in result
