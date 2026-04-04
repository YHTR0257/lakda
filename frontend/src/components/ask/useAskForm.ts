"use client";

import { useActionState } from "react";
import { confirmQuestion } from "@/app/(chat)/ask/actions";
import type { ConfirmResponse } from "@/types/ask";
import { useEffect, useRef } from "react";

export interface AskActionState {
  success: boolean;
  answer: ConfirmResponse | null;
  answerHtml: string | null;
  error: string;
  code?: string;
}

const initialState: AskActionState = {
  success: false,
  answer: null,
  answerHtml: null,
  error: "",
};

export function useAskForm() {
  const [state, formAction] = useActionState(confirmQuestion, initialState as unknown);
  const typedState = state as AskActionState;
  const formRef = useRef<HTMLFormElement>(null);

  useEffect(() => {
    if (typedState.success) {
      formRef.current?.reset();
    }
  }, [typedState.success]);

  return { state: typedState, formAction, formRef };
}
