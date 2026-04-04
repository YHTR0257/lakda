"use client";

import { type FormEvent, type ChangeEvent } from "react";
import { useAutoResize } from "./useAutoResize";
import { useDropzone } from "react-dropzone";

interface Props {
  input: string;
  handleInputChange: (e: ChangeEvent<HTMLTextAreaElement>) => void;
  handleSubmit: (e: FormEvent<HTMLFormElement>) => void;
  isLoading: boolean;
}

export default function ChatInput({
  input,
  handleInputChange,
  handleSubmit,
  isLoading,
}: Props) {
  const textareaRef = useAutoResize(input);

  const { getRootProps, getInputProps, isDragActive, open } = useDropzone({
    noClick: true,
    noKeyboard: true,
    accept: { "text/markdown": [".md"], "application/pdf": [".pdf"] },
    onDrop: (files) => {
      if (files.length === 0) return;
      const file = files[0];
      const reader = new FileReader();
      reader.onload = (e) => {
        const text = e.target?.result as string;
        const syntheticEvent = {
          target: { value: text },
        } as ChangeEvent<HTMLTextAreaElement>;
        handleInputChange(syntheticEvent);
      };
      reader.readAsText(file);
    },
  });

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
    <div className="border-t border-gray-200 bg-white px-4 py-4">
      <form
        onSubmit={handleSubmit}
        className="mx-auto max-w-3xl"
        {...getRootProps()}
      >
        <div
          className={`flex items-end gap-2 rounded-2xl border px-4 py-3 transition-colors ${
            isDragActive
              ? "border-blue-400 bg-blue-50"
              : "border-gray-300 bg-white focus-within:border-blue-500 focus-within:ring-1 focus-within:ring-blue-500"
          }`}
        >
          {/* react-dropzone hidden input */}
          <input {...getInputProps()} />
          <button
            type="button"
            onClick={open}
            title="ファイルをアップロード"
            className="mb-1 flex-shrink-0 rounded p-1 text-gray-400 hover:text-gray-600"
          >
            <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13"
              />
            </svg>
          </button>
          <textarea
            ref={textareaRef}
            rows={1}
            value={input}
            onChange={handleInputChange}
            onKeyDown={onKeyDown}
            placeholder="質問を入力 (Cmd+Enter で送信)"
            disabled={isLoading}
            className="flex-1 resize-none overflow-hidden bg-transparent text-sm text-gray-900 placeholder-gray-400 focus:outline-none disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={isLoading || !input.trim()}
            className="mb-1 flex-shrink-0 rounded-xl bg-blue-600 p-2 text-white transition-colors hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-gray-300"
          >
            {isLoading ? (
              <svg className="h-4 w-4 animate-spin" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
              </svg>
            ) : (
              <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 10l7-7m0 0l7 7m-7-7v18" />
              </svg>
            )}
          </button>
        </div>
        <p className="mt-1 text-center text-xs text-gray-400">
          .md / .pdf をドラッグ＆ドロップできます
        </p>
      </form>
    </div>
  );
}
