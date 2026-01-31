"use client";

import { redirect } from "next/navigation";
import * as api from "@/lib/api";
import { ApiException } from "@/lib/api";

export async function submitQuestion(formData: FormData) {
  try {
    const question = formData.get("question") as string;

    if (!question || question.trim().length === 0) {
      return { success: false, error: "質問を入力してください。" };
    }

    const result = await api.submitQuestion(question);

    redirect(`/ask/interpret?id=${result.interpretationId}`);
  } catch (error) {
    console.error("Error submitting question:", error);

    if (error instanceof ApiException) {
      return {
        success: false,
        error: error.error,
        code: error.code,
        details: error.details,
      };
    }

    return {
      success: false,
      error: "質問の送信中に予期しないエラーが発生しました。",
    };
  }
}
