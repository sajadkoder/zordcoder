import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Zord Coder - AI Coding Assistant',
  description: 'AI Coding Assistant by SaJad - Fast, intelligent, and beautiful',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className="antialiased">
        {children}
      </body>
    </html>
  )
}
