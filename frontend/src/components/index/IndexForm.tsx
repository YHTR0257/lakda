"use client";

import { useFormStatus } from "react-dom";
import { useIndexForm, type HealthStatus } from "./useIndexForm";
import type { LlmHealthResponse } from "@/types/index";

// ---- 小コンポーネント ------------------------------------------------

function HealthIndicator({ label, ok }: { label: string; ok: boolean }) {
  return (
    <div className="flex items-center gap-2 text-sm">
      {ok ? (
        <span className="flex h-5 w-5 items-center justify-center rounded-full bg-green-100 text-green-600">✓</span>
      ) : (
        <span className="flex h-5 w-5 items-center justify-center rounded-full bg-red-100 text-red-600">✗</span>
      )}
      <span className={ok ? "text-green-700" : "text-red-700"}>{label}</span>
    </div>
  );
}

function HealthPanel({
  healthStatus,
  health,
  onCheck,
}: {
  healthStatus: HealthStatus;
  health: LlmHealthResponse | null;
  onCheck: () => void;
}) {
  return (
    <div className="rounded-lg border border-gray-200 bg-gray-50 p-4">
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium text-gray-700">LLM 接続状態</span>
        <button
          type="button"
          onClick={onCheck}
          disabled={healthStatus === "checking"}
          className="rounded-md bg-white px-3 py-1 text-xs font-medium text-gray-600 shadow-sm ring-1 ring-gray-300 hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {healthStatus === "checking" ? "確認中..." : "確認"}
        </button>
      </div>

      {healthStatus === "idle" && (
        <p className="mt-2 text-xs text-gray-400">「確認」ボタンで LLM サーバーの接続状態を確認できます</p>
      )}
      {healthStatus === "checking" && (
        <p className="mt-2 text-xs text-gray-500">確認中...</p>
      )}
      {(healthStatus === "ok" || healthStatus === "error") && health && (
        <div className="mt-3 flex gap-6">
          <HealthIndicator label="LLM" ok={health.llm} />
          <HealthIndicator label="Embedding" ok={health.embedding} />
        </div>
      )}
    </div>
  );
}

function CamelWalking() {
  const { pending } = useFormStatus();
  if (!pending) return null;

  return (
    <div className="relative h-12 overflow-hidden rounded-lg bg-amber-50">
      <span
        className="absolute bottom-1 text-3xl leading-none"
        style={{ animation: "camel-walk 3s linear infinite" }}
      >
        🐫
      </span>
    </div>
  );
}

function SubmitButton() {
  const { pending } = useFormStatus();

  return (
    <button
      type="submit"
      disabled={pending}
      className="flex w-full items-center justify-center rounded-lg bg-blue-600 px-6 py-3 font-medium text-white transition-colors hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-gray-400"
    >
      {pending ? (
        <>
          <svg
            className="mr-3 -ml-1 h-5 w-5 animate-spin text-white"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            />
          </svg>
          Indexing...
        </>
      ) : (
        "Run Indexing"
      )}
    </button>
  );
}

// ---- メインフォーム --------------------------------------------------

export default function IndexForm() {
  const {
    state,
    formAction,
    formRef,
    activeTab,
    setActiveTab,
    fileContent,
    fileName,
    handleFileChange,
    healthStatus,
    health,
    handleHealthCheck,
  } = useIndexForm();

  return (
    <form ref={formRef} action={formAction} className="space-y-6">
      <HealthPanel healthStatus={healthStatus} health={health} onCheck={handleHealthCheck} />

      {/* Doc ID */}
      <div>
        <label htmlFor="doc_id" className="mb-2 block text-sm font-medium text-gray-700">
          Document ID（任意）
        </label>
        <input
          id="doc_id"
          name="doc_id"
          type="text"
          className="w-full rounded-lg border border-gray-300 px-4 py-2 focus:border-transparent focus:ring-2 focus:ring-blue-500"
          placeholder="doc-001"
        />
      </div>

      {/* Tabs */}
      <div>
        <div className="flex border-b border-gray-200">
          {(["text", "file"] as const).map((tab) => (
            <button
              key={tab}
              type="button"
              onClick={() => setActiveTab(tab)}
              className={`px-4 py-2 text-sm font-medium transition-colors ${
                activeTab === tab
                  ? "border-b-2 border-blue-600 text-blue-600"
                  : "text-gray-500 hover:text-gray-700"
              }`}
            >
              {tab === "text" ? "テキスト入力" : "ファイルアップロード"}
            </button>
          ))}
        </div>

        {activeTab === "text" && (
          <div className="mt-4">
            <textarea
              id="markdown_text"
              name="markdown_text"
              rows={12}
              required
              className="w-full resize-none rounded-lg border border-gray-300 px-4 py-3 focus:border-transparent focus:ring-2 focus:ring-blue-500"
              placeholder={`# タイトル\n\nMarkdown テキストを入力してください。`}
            />
          </div>
        )}

        {activeTab === "file" && (
          <div className="mt-4 space-y-4">
            <label
              htmlFor="md_file"
              className="flex cursor-pointer flex-col items-center justify-center rounded-lg border-2 border-dashed border-gray-300 px-6 py-10 transition-colors hover:border-blue-400 hover:bg-blue-50"
            >
              <svg className="mb-3 h-8 w-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                />
              </svg>
              <span className="text-sm text-gray-600">
                {fileName ? (
                  <span className="font-medium text-blue-600">{fileName}</span>
                ) : (
                  <>クリックして <span className="font-medium text-blue-600">.md / .pdf / .json / 画像</span> を選択</>
)}
              </span>
              <input
                id="md_file"
                name="file"
                type="file"
                accept=".md,.pdf,.json,.jpg,.jpeg,.png,text/markdown"
                className="sr-only"
                onChange={handleFileChange}
              />
            </label>

            <textarea name="markdown_text" required readOnly value={fileContent} className="sr-only" />

            {fileContent && (
              <div className="rounded-lg border border-gray-200 bg-gray-50 p-3">
                <p className="mb-1 text-xs font-medium text-gray-500">プレビュー</p>
                <pre className="max-h-48 overflow-y-auto whitespace-pre-wrap text-xs text-gray-700">{fileContent}</pre>
              </div>
            )}
            {fileName && !fileContent && (
              <p className="text-xs text-gray-500 mt-2">プレビュー不可（バイナリファイル）</p>
            )}
          </div>
        )}
      </div>

      <CamelWalking />

      {/* Success banner */}
      {state.success && (
        <div className="rounded-lg border border-green-200 bg-green-50 p-4">
          <p className="text-sm font-medium text-green-800">
            Indexing complete
            {state.doc_id && <span className="ml-2 text-green-600">（ID: {state.doc_id}）</span>}
          </p>
          {state.timestamp && <p className="mt-1 text-xs text-green-600">{state.timestamp}</p>}
        </div>
      )}

      {/* Error banner */}
      {state.error && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4">
          <div className="flex items-start">
            <svg className="mt-0.5 mr-3 h-5 w-5 text-red-600" fill="currentColor" viewBox="0 0 20 20">
              <path
                fillRule="evenodd"
                d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                clipRule="evenodd"
              />
            </svg>
            <p className="text-sm font-medium text-red-800">{state.error}</p>
          </div>
        </div>
      )}

      <SubmitButton />
    </form>
  );
}
