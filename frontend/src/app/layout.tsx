import type { Metadata } from 'next'
import './globals.css'
import Header from '@/components/layout/Header'
import Footer from '@/components/layout/Footer'

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
			<body className="flex min-h-screen flex-col bg-gray-50 text-gray-900">
				<Header />
				<main className="mx-auto w-full max-w-7xl flex-1 px-4 py-8">
          {children}
        </main>
				<Footer />
			</body>
		</html>
	);
}