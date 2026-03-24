"""ドキュメントのインデックス作成とリトリーブを試すスクリプト

Docker コンテナ内で実行することを想定:
  docker compose exec backend python /app/scripts/index.py

前提:
  - Neo4j が起動していること
  - Ollama が起動し、llama3.1:8b と bge-m3 モデルがプルされていること
  - data/documents/ にドキュメントが配置されていること
"""

import os
from pathlib import Path

import dotenv
import nest_asyncio
from llama_index.core import PropertyGraphIndex, Settings, SimpleDirectoryReader
from llama_index.core.node_parser import MarkdownNodeParser
from llama_index.graph_stores.neo4j import Neo4jPropertyGraphStore

from lakda.llm.client import LlmClientManager

dotenv.load_dotenv()
nest_asyncio.apply()

# --- LLMクライアント一元管理 ---
manager = LlmClientManager()

# チャットLLM登録
manager.register(
    provider="ollama",
    model="llama3.1:8b",
    base_url=os.getenv("OLLAMA_URL"),
)

# embedding登録
manager.register_embedding(
    provider="ollama",
    model_name="bge-m3",
    request_timeout=300.0,
    base_url=os.getenv("OLLAMA_URL"),
)

Settings.llm = manager.get_llm()
Settings.embed_model = manager.get_embed_model()

print(f"LLM: {Settings.llm.model}")  # type: ignore[union-attr]
print(f"Embed model: {Settings.embed_model.model_name}")

# --- ドキュメント読み込み ---
root_dir = Path("/app")
data_dir = root_dir / "data" / "documents"

if not data_dir.exists():
    raise FileNotFoundError(f"ドキュメントディレクトリが見つかりません: {data_dir}")

documents = SimpleDirectoryReader(str(data_dir)).load_data()
print(f"読み込んだドキュメント数: {len(documents)}")

# --- ノードパーサー ---
parser = MarkdownNodeParser()
nodes = parser.get_nodes_from_documents(documents, show_progress=True)
print(f"パースしたノード数: {len(nodes)}")

# --- Neo4j グラフストア ---
graph_store = Neo4jPropertyGraphStore(
    username=os.getenv("NEO4J_USER", "neo4j"),
    password=os.getenv("NEO4J_PASSWORD", "password"),
    url=os.getenv("DATABASE_URL_BOLT", "bolt://localhost:7687"),
)

# --- インデックス作成 ---
print("インデックスを作成中...")
index = PropertyGraphIndex.from_documents(
    documents=documents,
    property_graph_store=graph_store,
    show_progress=True,
)
print("インデックス作成完了")

# --- リトリーブ ---
query = "Tailwindってなんですか?"
print(f"\nクエリ: {query}")

retriever = index.as_retriever(include_text=True)
results = retriever.retrieve(query)

print(f"取得したノード数: {len(results)}")
for i, node in enumerate(results):
    print(f"\n--- Result {i + 1} (score: {node.score:.4f}) ---")
    print(node.text[:500])
