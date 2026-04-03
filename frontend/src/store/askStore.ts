import { create } from "zustand";
import type { AnswerSource } from "@/types/ask";

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  text: string;
  answerHtml?: string | null;
  sources?: AnswerSource[];
  error?: string;
  timestamp: string;
}

interface AskStore {
  messages: ChatMessage[];
  addMessage: (message: ChatMessage) => void;
  clearMessages: () => void;
}

export const useAskStore = create<AskStore>((set) => ({
  messages: [],
  addMessage: (message) =>
    set((state) => ({ messages: [...state.messages, message] })),
  clearMessages: () => set({ messages: [] }),
}));
