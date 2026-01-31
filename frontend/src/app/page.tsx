import Link from 'next/link';
import { Button } from '@/components/ui/Button';

export default function Home() {
  return (
    <div className="space-y-8">
      <section className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          Welcome
        </h1>
        <p className="text-lg text-gray-600">
          knowledge-retrieval-assistantへようこそ！ここでは、ドキュメントのアップロードと相談が可能です。
        </p>

				<p className="text-lg text-gray-600 mt-2">
					左のサイドバーから操作を開始してください。
				</p>
        <div className="mt-8">
          <Link href="/ask" passHref>
            <Button>質問を開始する</Button>
          </Link>
        </div>
      </section>

      <section className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-semibold mb-2">Card 1</h2>
          <p className="text-gray-600">コンテンツ</p>
        </div>
        {/* 他のカード */}
      </section>
    </div>
  )
}