"use client";

import type { Message } from "ai/react";
import ChatMessage from "./ChatMessage";
import { useChatScroll } from "./useChatScroll";

interface Props {
  messages: Message[];
  isLoading: boolean;
}

export default function ChatWindow({ messages, isLoading }: Props) {
  const bottomRef = useChatScroll(messages);

  const lastMessage = messages.at(-1);
  const showTyping = isLoading && lastMessage?.role === "user";
  const streamingId =
    isLoading && lastMessage?.role === "assistant" ? lastMessage.id : null;

  return (
    <div className="flex-1 overflow-y-auto px-4 py-6">
      <div className="mx-auto max-w-3xl space-y-4">
        {messages.map((message) => (
          <ChatMessage
            key={message.id}
            message={message}
            isStreaming={message.id === streamingId}
          />
        ))}
        {showTyping && (
          <div className="flex justify-start">
            <div className="flex items-center gap-1 rounded-2xl border border-gray-200 bg-white px-4 py-3 shadow-sm">
              <span className="h-2 w-2 animate-bounce rounded-full bg-gray-400 [animation-delay:-0.3s]" />
              <span className="h-2 w-2 animate-bounce rounded-full bg-gray-400 [animation-delay:-0.15s]" />
              <span className="h-2 w-2 animate-bounce rounded-full bg-gray-400" />
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>
    </div>
  );
}
