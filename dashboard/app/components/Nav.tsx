'use client'
import Link from 'next/link'
import { usePathname } from 'next/navigation'

const links = [
  { href: '/', label: 'Home', icon: '🏠' },
  { href: '/analysis', label: '分析', icon: '📈' },
  { href: '/notes', label: 'Note記事', icon: '📄' },
]

export default function Nav() {
  const path = usePathname()
  return (
    <nav className="fixed bottom-0 left-0 right-0 bg-zinc-950/95 backdrop-blur border-t border-zinc-800">
      <div className="max-w-lg mx-auto flex">
        {links.map(({ href, label, icon }) => (
          <Link
            key={href}
            href={href}
            className={`flex-1 flex flex-col items-center py-2.5 gap-1 transition-colors ${
              path === href ? 'text-emerald-400' : 'text-zinc-500'
            }`}
          >
            <span className="text-xl leading-none">{icon}</span>
            <span className="text-xs">{label}</span>
          </Link>
        ))}
      </div>
    </nav>
  )
}
