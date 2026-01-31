import QuestionForm from "@/components/ask/QuestionForm";

export default function AskPage() {
  return (
    <div className="container mx-auto max-w-3xl p-6">
      <div className="mb-8">
        <h1 className="mb-2 text-3xl font-bold text-gray-900">LAKDA 🐫</h1>
        <p className="text-gray-600">
          アップロードされたドキュメントに基づいて質問に回答します。
          質問を入力すると、LAKDAは質問を解釈し、データベースから関連情報を検索し、コンテキストに基づいた回答を生成します。
        </p>
      </div>

      <QuestionForm />
    </div>
  );
}
