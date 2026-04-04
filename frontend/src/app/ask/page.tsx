"use client";

import { useChat } from "ai/react";
import ChatWindow from "@/components/ask/chat/ChatWindow";
import ChatInput from "@/components/ask/chat/ChatInput";

export default function AskPage() {
  const { messages, input, handleInputChange, handleSubmit, isLoading, error } =
    useChat({ api: "/api/ask/chat" });

  return (
    <div className="flex h-dvh flex-col">
      <header className="border-b border-gray-200 bg-white px-6 py-4">
        <h1 className="text-xl font-bold text-gray-900">LAKDA 🐫</h1>
        <p className="text-sm text-gray-500">
          アップロードされたドキュメントに基づいて質問に回答します
        </p>
      </header>

      <ChatWindow messages={messages} isLoading={isLoading} />

      {error && (
        <div className="mx-auto mb-2 w-full max-w-3xl px-4">
          <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-2">
            <p className="text-sm text-red-700">{error.message}</p>
          </div>
        </div>
      )}

      <ChatInput
        input={input}
        handleInputChange={handleInputChange}
        handleSubmit={handleSubmit}
        isLoading={isLoading}
      />
    </div>
  );
}
