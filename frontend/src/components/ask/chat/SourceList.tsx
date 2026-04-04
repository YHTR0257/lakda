import type { AnswerSource } from "@/types/ask";

interface Props {
  sources: AnswerSource[];
}

export default function SourceList({ sources }: Props) {
  if (sources.length === 0) return null;

  return (
    <div className="mt-3">
      <h3 className="mb-2 text-xs font-medium text-gray-500">
        参照ソース ({sources.length}件)
      </h3>
      <ul className="space-y-2">
        {sources.map((source, index) => (
          <li
            key={index}
            className="rounded-lg border border-gray-200 bg-gray-50 p-3"
          >
            <div className="mb-1 flex items-center justify-between">
              <span className="text-xs font-medium text-gray-700">
                {source.file}
              </span>
              <span className="text-xs text-gray-500">
                スコア: {(source.score * 100).toFixed(1)}%
              </span>
            </div>
            <p className="text-xs text-gray-600">{source.snippet}</p>
          </li>
        ))}
      </ul>
    </div>
  );
}
