"use client";

import { type FormEvent, type ChangeEvent, useRef } from "react";
import { useAutoResize } from "./useAutoResize";
import { Button } from "@/components/ui/Button";
import { Textarea } from "@/components/ui/Textarea";

interface Props {
  input: string;
  handleInputChange: (e: ChangeEvent<HTMLTextAreaElement>) => void;
  handleSubmit: (e: FormEvent<HTMLFormElement>) => void;
  isLoading: boolean;
  compact?: boolean;
}

export default function ChatInput({
  input,
  handleInputChange,
  handleSubmit,
  isLoading,
  compact = false,
}: Props) {
  const textareaRef = useAutoResize(input, compact ? 1 : 3);
  const fileInputRef = useRef<HTMLInputElement>(null);

  function onFileChange(e: ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (ev) => {
      const text = ev.target?.result as string;
      handleInputChange({ target: { value: text } } as ChangeEvent<HTMLTextAreaElement>);
    };
    reader.readAsText(file);
    e.target.value = "";
  }

  function onKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if ((e.metaKey || e.ctrlKey) && e.key === "Enter") {
      e.preventDefault();
      if (!isLoading && input.trim()) {
        const form = e.currentTarget.closest("form") as HTMLFormElement;
        form?.requestSubmit();
      }
    }
  }

  return (
    <div className="px-4 py-2">
      <form onSubmit={handleSubmit} className="mx-auto max-w-3xl">
        <div className="flex items-center gap-1.5 rounded-2xl border border-gray-300 bg-gray-50 px-3 py-1.5 transition-colors focus-within:border-blue-500 focus-within:ring-1 focus-within:ring-blue-500">
          <input
            ref={fileInputRef}
            type="file"
            accept="text/markdown,.md,application/pdf,.pdf"
            className="hidden"
            onChange={onFileChange}
          />
          <Button
            type="button"
            variant="ghost"
            size="icon"
            onClick={() => fileInputRef.current?.click()}
            title="ファイルをアップロード"
            className="h-6 w-6 flex-shrink-0 text-gray-400 hover:text-gray-600"
          >
            <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13"
              />
            </svg>
          </Button>
          <Textarea
            ref={textareaRef}
            rows={1}
            value={input}
            onChange={handleInputChange}
            onKeyDown={onKeyDown}
            placeholder="質問を入力 (Cmd+Enter で送信)"
            disabled={isLoading}
            className="flex-1 overflow-hidden border-0 bg-transparent px-0 py-0 text-sm text-gray-900 placeholder:text-gray-400 focus-visible:ring-0 focus-visible:ring-offset-0"
          />
          <Button
            type="submit"
            size="icon"
            disabled={isLoading || !input.trim()}
            className="h-7 w-7 flex-shrink-0 rounded-xl bg-blue-600 hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-gray-300"
          >
            {isLoading ? (
              <svg className="h-3.5 w-3.5 animate-spin" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
              </svg>
            ) : (
              <svg className="h-3.5 w-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 10l7-7m0 0l7 7m-7-7v18" />
              </svg>
            )}
          </Button>
        </div>
      </form>
    </div>
  );
}
