import type { Interpretation, Answer } from "@/types/ask";
import {
  mockSubmitQuestion,
  mockGetInterpretation,
  mockConfirmInterpretation,
  mockGetAnswer,
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
