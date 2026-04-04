import IndexForm from "@/components/index/IndexForm";

export default function IndexPage() {
  return (
    <div className="container mx-auto max-w-3xl p-6">
      <div className="mb-8">
        <h1 className="mb-2 text-3xl font-bold text-gray-900">Indexing</h1>
        <p className="text-gray-600">
          Markdown テキストを Neo4j グラフデータベースに登録します。
        </p>
      </div>

      <IndexForm />
    </div>
  );
}
