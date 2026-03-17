import type { ConfirmResponse } from "@/types/ask";

interface Props {
  answer: ConfirmResponse;
  answerHtml: string | null;
}

export default function AnswerDisplay({ answer, answerHtml }: Props) {
  return (
    <div className="mt-8 space-y-6">
      {/* 回答テキスト */}
      <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
        <h2 className="mb-1 text-sm font-medium text-gray-500">質問</h2>
        <p className="mb-4 text-gray-800">{answer.question}</p>
        <h2 className="mb-2 text-sm font-medium text-gray-500">回答</h2>
        <div className="whitespace-pre-wrap text-gray-900">{answer.answer}</div>
      </div>

      {/* ソース一覧 */}
      {answer.sources.length > 0 && (
        <div>
          <h3 className="mb-3 text-sm font-medium text-gray-700">
            参照ソース ({answer.sources.length}件)
          </h3>
          <ul className="space-y-3">
            {answer.sources.map((source, index) => (
              <li
                key={index}
                className="rounded-lg border border-gray-200 bg-gray-50 p-4"
              >
                <div className="mb-1 flex items-center justify-between">
                  <span className="text-sm font-medium text-gray-700">
                    {source.file}
                  </span>
                  <span className="text-xs text-gray-500">
                    スコア: {(source.score * 100).toFixed(1)}%
                  </span>
                </div>
                <p className="text-sm text-gray-600">{source.snippet}</p>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
