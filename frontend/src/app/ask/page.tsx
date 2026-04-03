"use client";

import { useChatAsk } from "@/hooks/useChatAsk";
import ChatHistory from "@/components/ask/ChatHistory";
import ChatInput from "@/components/ask/ChatInput";

export default function AskPage() {
  const { messages, isPending, inputRef, submit, clearMessages } = useChatAsk();

  return (
    <div className="-mx-4 -my-8 flex h-[calc(100vh-8rem)] flex-col overflow-hidden rounded-xl border border-gray-200 bg-white shadow-sm">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-gray-200 px-6 py-3">
        <div>
          <h1 className="text-xl font-bold text-gray-900">LAKDA 🐫</h1>
          <p className="text-xs text-gray-500">
            ドキュメントに基づいて質問に回答します
          </p>
        </div>
        {messages.length > 0 && (
          <button
            type="button"
            onClick={clearMessages}
            className="rounded-lg px-3 py-1.5 text-xs text-gray-500 transition-colors hover:bg-gray-100 hover:text-gray-700"
          >
            会話をクリア
          </button>
        )}
      </div>

      {/* Chat history */}
      <ChatHistory messages={messages} isPending={isPending} />

      {/* Input area */}
      <ChatInput inputRef={inputRef} onSubmit={submit} isPending={isPending} />
    </div>
  );
}
