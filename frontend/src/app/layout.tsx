import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
    title: 'Knowledge Retrieval Assistant',
    description: 'A knowledge retrieval assistant application',
};

export default function RootLayout({
	children,
}: {
	children: React.ReactNode;
}) {
	return (
		<html lang="ja">
			<body className="min-h-screen bg-gray-50 text-gray-900">
				<header className="bg-white shadow-sm">
					<nav className="max-w-7xl mx-auto px-4 py-4">
            {/* ナビゲーション */}
          </nav>
				</header>
				<main className="max-w-7xl mx-auto px-4 py-8">
          {children}
        </main>
				<footer className="bg-gray-800 text-white mt-auto">
          <div className="max-w-7xl mx-auto px-4 py-6">
            {/* フッター */}
          </div>
        </footer>
			</body>
		</html>
	);
}