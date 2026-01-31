import { notFound } from "next/navigation";
import InterpretationEditor from "@/components/ask/InterpretationEditor";
import { getInterpretation } from "@/lib/api";
import { ApiException } from "@/lib/api";

export default async function InterpretPage({
  searchParams,
}: {
  searchParams: { id: string };
}) {
  try {
    const interpretation = await getInterpretation(searchParams.id);

    return (
      <div className="container mx-auto max-w-3xl p-6">
        <h1 className="mb-2 text-3xl font-bold">質問の解釈</h1>
        <p className="mb-6 text-gray-600">
          システムが質問をどのように解釈したか確認してください。必要に応じて修正できます。
        </p>
        <InterpretationEditor interpretation={interpretation} />
      </div>
    );
  } catch (error) {
    if (error instanceof ApiException) {
      // エラーコードに応じた処理
      if (error.statusCode === 404) {
        notFound();
      }

      // その他のエラーはエラーページへ
      return (
        <div className="container mx-auto max-w-3xl p-6">
          <div className="rounded-lg border border-red-200 bg-red-50 p-6">
            <h2 className="mb-2 text-xl font-semibold text-red-800">
              エラーが発生しました
            </h2>
            <p className="text-red-700">{error.error}</p>
            {error.code && (
              <p className="mt-2 text-sm text-red-600">
                エラーコード: {error.code}
              </p>
            )}
          </div>
        </div>
      );
    }

    // 予期しないエラー
    throw error;
  }
}
