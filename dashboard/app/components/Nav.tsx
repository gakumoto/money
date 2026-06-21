'use client'
import Link from 'next/link'
import { usePathname } from 'next/navigation'

const navItems = [
  { href: '/', label: 'Home', icon: '🏠', external: false },
  { href: '/studio', label: 'Studio', icon: '🏢', external: false },
  { href: '/review', label: 'レビュー', icon: '📝', external: false },
  { href: '/threads', label: 'Threads', icon: '🧵', external: false },
  { href: '/buzz', label: 'バズ', icon: '🔥', external: false },
  { href: '/notes', label: 'Note', icon: '📄', external: false },
  { href: '/analysis', label: '分析', icon: '📈', external: false },
  { href: '/api/report', label: 'レポート', icon: '📊', external: true },
]

export default function Nav() {
  const path = usePathname()
  return (
    <nav className="fixed bottom-0 left-0 right-0 bg-zinc-950/95 backdrop-blur border-t border-zinc-800">
      <div className="max-w-lg mx-auto flex">
        {navItems.map(({ href, label, icon, external }) => {
          const isActive = !external && path === href
          const cls = `flex-1 flex flex-col items-center py-2 gap-0.5 transition-colors ${
            isActive ? 'text-emerald-400' : 'text-zinc-500'
          }`
          return external ? (
            <a key={href} href={href} className={cls}>
              <span className="text-xl leading-none">{icon}</span>
              <span className="text-xs">{label}</span>
            </a>
          ) : (
            <Link key={href} href={href} className={cls}>
              <span className="text-xl leading-none">{icon}</span>
              <span className="text-xs">{label}</span>
            </Link>
          )
        })}
      </div>
    </nav>
  )
}
