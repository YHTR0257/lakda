"use client";

import { useEffect, useRef } from "react";
import type { Message } from "ai/react";

export function useChatScroll(messages: Message[]) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return bottomRef;
}
