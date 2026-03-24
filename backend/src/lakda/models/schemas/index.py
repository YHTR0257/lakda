from pydantic import BaseModel
from typing import Any


class IndexMarkdownRequest(BaseModel):
    markdown_text: str
    doc_id: str | None = None
    chunk_size: int = 256
    chunk_overlap: int = 32


class IndexResponse(BaseModel):
    doc_id: str | None
    status: str
    timestamp: str


class LlmHealthResponse(BaseModel):
    llm: bool
    embedding: bool
    ok: bool


class NodeLabelCount(BaseModel):
    label: str
    count: int


class RelTypeCount(BaseModel):
    type: str
    count: int


class GraphStatsResponse(BaseModel):
    node_count: int
    rel_count: int
    nodes_by_label: list[NodeLabelCount]
    rels_by_type: list[RelTypeCount]
    sample_nodes: list[dict[str, Any]]
