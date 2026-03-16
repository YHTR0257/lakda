"""Ask リトリーバル - Neo4j PropertyGraphStore の検索"""

from llama_index.core import PropertyGraphIndex
from llama_index.core.base.response.schema import RESPONSE_TYPE


class AskRetrieval:
    """PropertyGraphIndex を使って Neo4j を検索するクラス

    LlamaIndex の PropertyGraphIndex.as_query_engine() を通じて
    Neo4j PropertyGraphStore からノード・リレーションを検索し、
    LLM で回答を生成します。

    Attributes:
        _index: 検索対象の PropertyGraphIndex
    """

    def __init__(self, index: PropertyGraphIndex) -> None:
        """AskRetrieval を初期化する

        Args:
            index: 検索対象の PropertyGraphIndex
        """
        self._index = index

    def query(self, question: str, max_results: int = 3) -> RESPONSE_TYPE:
        """質問に対してグラフ検索と回答生成を実行する

        LlamaIndex Settings.llm および Settings.embed_model が
        事前に設定されている必要があります。

        Args:
            question: 質問テキスト
            max_results: 参照するソースノードの最大数

        Returns:
            LlamaIndex のレスポンスオブジェクト（.response と .source_nodes を持つ）
        """
        query_engine = self._index.as_query_engine(
            include_text=True,
            similarity_top_k=max_results,
        )
        return query_engine.query(question)
