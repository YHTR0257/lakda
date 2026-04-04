import Header from '@/components/layout/Header'
import Footer from '@/components/layout/Footer'

export default function ChatLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div className="flex h-dvh flex-col">
      <Header />
      {children}
      <Footer />
    </div>
  )
}
