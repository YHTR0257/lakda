export interface IndexMarkdownRequest {
  markdown_text: string;
  doc_id?: string;
}

export interface IndexResponse {
  doc_id: string | null;
  status: string;
  timestamp: string;
}

export interface LlmHealthResponse {
  llm: boolean;
  embedding: boolean;
  ok: boolean;
}
