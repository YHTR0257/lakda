import type { ChatMessage } from "@/store/askStore";

interface Props {
  message: ChatMessage;
}

export default function ChatMessageBubble({ message }: Props) {
  const isUser = message.role === "user";

  return (
    <div
      className={`flex w-full ${isUser ? "justify-end" : "justify-start"}`}
      data-testid={`chat-message-${message.role}`}
    >
      {!isUser && (
        <div className="mr-2 flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-blue-600 text-sm text-white">
          🐫
        </div>
      )}

      <div
        className={`max-w-[80%] space-y-2 ${isUser ? "items-end" : "items-start"} flex flex-col`}
      >
        <div
          className={`rounded-2xl px-4 py-3 ${
            isUser
              ? "rounded-tr-sm bg-blue-600 text-white"
              : "rounded-tl-sm border border-gray-200 bg-white text-gray-900 shadow-sm"
          }`}
        >
          {message.error ? (
            <div className="flex items-start gap-2">
              <span className="text-red-500">⚠</span>
              <p className="text-sm text-red-600">{message.error}</p>
            </div>
          ) : message.answerHtml ? (
            <div
              className="prose prose-sm max-w-none"
              dangerouslySetInnerHTML={{ __html: message.answerHtml }}
            />
          ) : (
            <p className="whitespace-pre-wrap text-sm">{message.text}</p>
          )}
        </div>

        {message.sources && message.sources.length > 0 && (
          <div className="w-full space-y-2">
            <p className="text-xs text-gray-500">
              参照ソース ({message.sources.length}件)
            </p>
            <ul className="space-y-1">
              {message.sources.map((source, index) => (
                <li
                  key={index}
                  className="rounded-lg border border-gray-200 bg-gray-50 px-3 py-2 text-xs"
                >
                  <div className="flex items-center justify-between">
                    <span className="font-medium text-gray-700">
                      {source.file}
                    </span>
                    <span className="text-gray-500">
                      {(source.score * 100).toFixed(1)}%
                    </span>
                  </div>
                  <p className="mt-1 text-gray-600">{source.snippet}</p>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {isUser && (
        <div className="ml-2 flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-gray-200 text-sm text-gray-600">
          👤
        </div>
      )}
    </div>
  );
}
