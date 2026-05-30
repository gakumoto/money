import type { Metadata, Viewport } from 'next'
import Nav from './components/Nav'
import './globals.css'

export const metadata: Metadata = {
  title: 'Company Dashboard',
  description: '仮想カンパニー ダッシュボード',
}

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ja">
      <body className="pb-16">
        {children}
        <Nav />
      </body>
    </html>
  )
}
