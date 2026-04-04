"use client";

import type { Message } from "ai/react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import rehypeSanitize from "rehype-sanitize";
import rehypeHighlight from "rehype-highlight";
import SourceList from "./SourceList";
import type { ChatMessageData } from "@/types/ask";

interface Props {
  message: Message;
  isStreaming?: boolean;
}

export default function ChatMessage({ message, isStreaming = false }: Props) {
  const isUser = message.role === "user";

  const sources =
    !isStreaming && message.role === "assistant"
      ? ((message.data as ChatMessageData[] | undefined)?.find((d) => d.sources)
          ?.sources ?? [])
      : [];

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-[80%] rounded-2xl px-4 py-3 ${
          isUser
            ? "bg-blue-600 text-white"
            : "border border-gray-200 bg-white text-gray-900 shadow-sm"
        }`}
      >
        {isUser ? (
          <p className="whitespace-pre-wrap text-sm">{message.content}</p>
        ) : (
          <>
            <div className="prose prose-sm max-w-none text-gray-900">
              <ReactMarkdown
                remarkPlugins={[remarkGfm]}
                rehypePlugins={[rehypeSanitize, rehypeHighlight]}
              >
                {message.content}
              </ReactMarkdown>
            </div>
            {sources.length > 0 && <SourceList sources={sources} />}
          </>
        )}
      </div>
    </div>
  );
}
