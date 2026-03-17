"use server";

import * as api from "@/lib/api";
import { ApiException } from "@/lib/api";
import { marked } from "marked";

export async function confirmQuestion(
  _prevState: unknown,
  formData: FormData
): Promise<unknown> {
  try {
    const question = formData.get("question") as string;

    if (!question || question.trim().length < 10) {
      return {
        success: false,
        answer: null,
        error: "質問は10文字以上で入力してください。",
      };
    }

    const sessionId = crypto.randomUUID();
    const result = await api.confirmAsk(question.trim(), sessionId);

    return {
      success: true,
      answer: result,
      error: "",
    };
  } catch (error) {
    console.error("Error confirming question:", error);

    if (error instanceof ApiException) {
      return {
        success: false,
        answer: null,
        error: error.error,
        code: error.code,
      };
    }

    return {
      success: false,
      answer: null,
      error: "質問の送信中に予期しないエラーが発生しました。",
    };
  }
}
