"use client";

import { useRef, useTransition } from "react";
import { confirmQuestion } from "@/app/ask/actions";
import { useAskStore } from "@/store/askStore";
import type { AskActionState } from "@/components/ask/useAskForm";

export function useChatAsk() {
  const [isPending, startTransition] = useTransition();
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const { messages, addMessage, clearMessages } = useAskStore();

  const submit = (text: string) => {
    const question = text.trim();
    if (!question || isPending) return;

    addMessage({
      id: crypto.randomUUID(),
      role: "user",
      text: question,
      timestamp: new Date().toISOString(),
    });

    if (inputRef.current) {
      inputRef.current.value = "";
    }

    const formData = new FormData();
    formData.set("question", question);

    startTransition(async () => {
      try {
        const result = (await confirmQuestion(
          undefined,
          formData
        )) as AskActionState;

        if (result.success && result.answer) {
          addMessage({
            id: crypto.randomUUID(),
            role: "assistant",
            text: result.answer.answer,
            answerHtml: result.answerHtml,
            sources: result.answer.sources,
            timestamp: new Date().toISOString(),
          });
        } else {
          addMessage({
            id: crypto.randomUUID(),
            role: "assistant",
            text: "",
            error: result.error || "エラーが発生しました。",
            timestamp: new Date().toISOString(),
          });
        }
      } catch (err) {
        const message =
          err instanceof Error ? err.message : "予期しないエラーが発生しました。";
        addMessage({
          id: crypto.randomUUID(),
          role: "assistant",
          text: "",
          error: message,
          timestamp: new Date().toISOString(),
        });
      }
    });
  };

  return { messages, isPending, inputRef, submit, clearMessages };
}
