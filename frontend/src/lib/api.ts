import type { Interpretation, Answer, ConfirmResponse } from "@/types/ask";
import type { IndexResponse, LlmHealthResponse } from "@/types/index";
import {
  mockSubmitQuestion,
  mockGetInterpretation,
  mockConfirmInterpretation,
  mockGetAnswer,
  mockIndexMarkdown,
  mockCheckIndexHealth,
  mockConfirmAsk,
} from "@/lib/mock-api";
import { ApiError } from "next/dist/server/api-utils";

const USE_MOCK = process.env.NEXT_PUBLIC_USE_MOCK == "true";
const BACKEND_URL = process.env.BACKEND_URL || "http://localhost:8000";

export class ApiException extends Error {
  constructor(
    public statusCode: number,
    public error: string,
    public code?: string,
    public details?: Record<string, any>
  ) {
    super(error);
    this.name = "ApiException";
  }
}

// 質問をバックエンドに送信し、回答を取得する
export async function submitQuestion(question: string) {
  if (USE_MOCK) {
    return await mockSubmitQuestion(question);
  }

  const response = await fetch("${BACKEND_URL}/api/ask/interpret", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ question }),
  });

  if (!response.ok) {
    const errorData: ApiError = await response.json().catch(() => ({
      error: "質問の送信に失敗しました。",
    }));
    throw new ApiException(
      response.status,
      errorData.error,
      errorData.code,
      errorData.details
    );
  }
}

export async function getInterpretation(id: string): Promise<Interpretation> {
  if (USE_MOCK) {
    return await mockGetInterpretation(id);
  }

  const response = await fetch(`${BACKEND_URL}/api/ask/interpretation/${id}`, {
    cache: "no-store",
  });

  if (!response.ok) {
    const errorData: ApiError = await response.json().catch(() => ({
      error: "質問の送信に失敗しました。",
    }));
    throw new ApiException(
      response.status,
      errorData.error,
      errorData.code,
      errorData.details
    );
  }

  return response.json();
}

export async function checkIndexHealth(): Promise<LlmHealthResponse> {
  if (USE_MOCK) {
    return await mockCheckIndexHealth();
  }

  const response = await fetch(`${BACKEND_URL}/index/health`);

  if (!response.ok) {
    return { llm: false, embedding: false, ok: false };
  }

  return response.json();
}

export async function confirmAsk(
  question: string,
  sessionId: string
): Promise<ConfirmResponse> {
  if (USE_MOCK) {
    return await mockConfirmAsk(question, sessionId);
  }

  const response = await fetch(`${BACKEND_URL}/ask/confirm`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      session_id: sessionId,
      confirmed_question: question,
      options: { max_results: 5 },
    }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => null);
    throw new ApiException(
      response.status,
      errorData?.detail ?? errorData?.error ?? "質問への回答に失敗しました。",
      errorData?.code,
      errorData?.details
    );
  }

  return response.json();
}

export async function indexMarkdown(
  markdown_text: string,
  doc_id?: string
): Promise<IndexResponse> {
  if (USE_MOCK) {
    return await mockIndexMarkdown(markdown_text, doc_id);
  }

  const response = await fetch(`${BACKEND_URL}/index/markdown`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ markdown_text, doc_id }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => null);
    throw new ApiException(
      response.status,
      errorData?.detail ?? errorData?.error ?? "インデキシングに失敗しました。",
      errorData?.code,
      errorData?.details
    );
  }

  return response.json();
}
