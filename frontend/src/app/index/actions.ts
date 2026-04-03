"use client";

import * as api from "@/lib/api";
import { ApiException } from "@/lib/api";

const MARKDOWN_EXTENSIONS = [".md"];

function isMarkdownFile(file: File): boolean {
  return (
    MARKDOWN_EXTENSIONS.some((ext) => file.name.endsWith(ext)) ||
    file.type === "text/markdown"
  );
}

export async function indexDocument(
  prevState: unknown,
  formData: FormData
) {
  try {
    const file = formData.get("file") as File | null;

    // 非マークダウンファイル（PDF/JSON/画像）→ /documents/upload
    if (file && file.size > 0 && !isMarkdownFile(file)) {
      const result = await api.uploadDocument(file, "general", true);
      return {
        success: true,
        doc_id: result.doc_id,
        timestamp: new Date().toISOString(),
        error: "",
      };
    }

    // テキスト入力 / .md ファイル → /index/markdown
    const markdown_text = formData.get("markdown_text") as string;
    const doc_id = (formData.get("doc_id") as string) || undefined;

    if (!markdown_text || markdown_text.trim().length === 0) {
      return {
        success: false,
        doc_id: null,
        timestamp: "",
        error: "Markdown テキストを入力してください。",
      };
    }

    const result = await api.indexMarkdown(markdown_text, doc_id);

    return {
      success: true,
      doc_id: result.doc_id,
      timestamp: result.timestamp,
      error: "",
    };
  } catch (error) {
    console.error("Error indexing document:", error);

    if (error instanceof ApiException) {
      return {
        success: false,
        doc_id: null,
        timestamp: "",
        error: error.error,
      };
    }

    return {
      success: false,
      doc_id: null,
      timestamp: "",
      error: "インデキシング中に予期しないエラーが発生しました。",
    };
  }
}
