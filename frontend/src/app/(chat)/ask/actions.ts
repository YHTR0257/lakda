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
    const answerHtml = await marked.parse(result.answer);

    return {
      success: true,
      answer: result,
      answerHtml,
      error: "",
    };
  } catch (error) {
    if (error instanceof ApiException) {
      return {
        success: false,
        answer: null,
        answerHtml: null,
        error: error.error,
        code: error.code,
      };
    }

    const message = error instanceof Error ? error.message : String(error);
    return {
      success: false,
      answer: null,
      answerHtml: null,
      error: `質問の送信中に予期しないエラーが発生しました: ${message}`,
    };
  }
}
