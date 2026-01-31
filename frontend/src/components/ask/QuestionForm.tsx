"use client";

import { useFormState } from "react-dom";
import { submitQuestion } from "@/app/ask/actions";
import SubmitButton from "./SubmitButton";
import { useEffect, useRef } from "react";

const initialState = {
  success: false,
  error: "",
  code: "",
};

export default function QuestionForm() {
  const [state, formAction] = useFormState(submitQuestion, initialState);
  const formRef = useRef<HTMLFormElement>(null);

  // 送信成功後にフォームをリセット（リダイレクト前）
  useEffect(() => {
    if (state.success) {
      formRef.current?.reset();
    }
  }, [state.success]);

  return (
    <form ref={formRef} action={formAction} className="space-y-6">
      {/* 質問入力エリア */}
      <div>
        <label
          htmlFor="question"
          className="mb-2 block text-sm font-medium text-gray-700"
        >
          質問内容
        </label>
        <textarea
          id="question"
          name="question"
          rows={8}
          required
          minLength={10}
          className="w-full resize-none rounded-lg border border-gray-300 px-4 py-3 focus:border-transparent focus:ring-2 focus:ring-blue-500"
          placeholder="研究に関する質問を入力してください。
          例: 弾性メタマテリアルの逆設計手法について、特にトポロジー最適化とGNNを組み合わせたアプローチを知りたいです。"
        />
        <p className="mt-2 text-sm text-gray-500">
          最低10文字以上で入力してください
        </p>
      </div>

      {/* エラー表示 */}
      {state.error && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4">
          <div className="flex items-start">
            <svg
              className="mt-0.5 mr-3 h-5 w-5 text-red-600"
              fill="currentColor"
              viewBox="0 0 20 20"
            >
              <path
                fillRule="evenodd"
                d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                clipRule="evenodd"
              />
            </svg>
            <div className="flex-1">
              <p className="text-sm font-medium text-red-800">{state.error}</p>
              {state.code && (
                <p className="mt-1 text-xs text-red-600">
                  エラーコード: {state.code}
                </p>
              )}
            </div>
          </div>
        </div>
      )}

      {/* 送信ボタン */}
      <SubmitButton />
    </form>
  );
}
