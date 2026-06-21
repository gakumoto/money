import fs from 'fs/promises'
import path from 'path'
import Link from 'next/link'
import { getRawContent } from '@/lib/github'

export const dynamic = 'force-dynamic'

interface Buzz {
  url: string
  handle: string
  post_id: string
  likes: number | null
  genre: string | null
  body?: string
}
interface BuzzData {
  generated_at: string
  count: number
  by_genre: Record<string, number>
  items: Buzz[]
}

async function load(): Promise<BuzzData | null> {
  for (const base of [path.join(process.cwd(), '..'), process.cwd()]) {
    try {
      return JSON.parse(await fs.readFile(path.join(base, '.company/research/threads-buzz.json'), 'utf-8'))
    } catch {
      /* next */
    }
  }
  try {
    const raw = await getRawContent('.company/research/threads-buzz.json')
    return raw ? JSON.parse(raw) : null
  } catch {
    return null
  }
}

const GENRES = ['すべて', 'Threads', 'note', '副業', 'Claude/AI']

function compact(n: number | null): string {
  if (n === null) return '—'
  if (n >= 10000) return `${(n / 10000).toFixed(1)}万`
  if (n >= 1000) return `${(n / 1000).toFixed(1)}k`
  return String(n)
}

export default async function Buzz({ searchParams }: { searchParams: { g?: string } }) {
  const data = await load()
  if (!data) {
    return (
      <main className="min-h-screen bg-black text-zinc-200 p-6">
        <h1 className="font-bold">バズ投稿リサーチ</h1>
        <p className="mt-3 text-sm text-zinc-400">
          データ未生成です。<code className="text-emerald-400">python scripts/build_threads_buzz.py</code> を実行してください。
        </p>
      </main>
    )
  }
  const g = searchParams.g && GENRES.includes(searchParams.g) ? searchParams.g : 'すべて'
  const items = g === 'すべて' ? data.items : data.items.filter((i) => i.genre === g)

  return (
    <main className="min-h-screen bg-black text-zinc-100 pb-20">
      <div className="sticky top-0 z-10 bg-black/90 backdrop-blur border-b border-zinc-800 px-4 py-3">
        <div className="flex items-center justify-between mb-3 max-w-lg mx-auto">
          <span className="font-bold text-base tracking-tight">🔥 バズ投稿リサーチ</span>
          <span className="text-xs text-zinc-500">{items.length}/{data.count}件</span>
        </div>
        <div className="flex gap-1 overflow-x-auto max-w-lg mx-auto scrollbar-hide">
          {GENRES.map((gn) => {
            const active = gn === g
            const n = gn === 'すべて' ? data.count : data.by_genre[gn] ?? 0
            return (
              <Link
                key={gn}
                href={gn === 'すべて' ? '/buzz' : `/buzz?g=${encodeURIComponent(gn)}`}
                className={`shrink-0 text-xs px-3 py-1.5 rounded-full font-medium transition-colors ${
                  active ? 'bg-zinc-100 text-black' : 'bg-zinc-900 text-zinc-400 border border-zinc-800'
                }`}
              >
                {gn} {n}
              </Link>
            )
          })}
        </div>
      </div>

      <div className="max-w-lg mx-auto">
        <p className="px-4 pt-3 text-[11px] text-zinc-600">
          いいね順。本文は未収録（外部収集はURL＋いいね数のみ）。タップで実物が開きます。
        </p>
        {items.map((it, idx) => (
          <a
            key={it.url}
            href={it.url}
            target="_blank"
            rel="noopener noreferrer"
            className="flex gap-3 px-4 py-3.5 border-b border-zinc-800/80 hover:bg-zinc-900/40 transition-colors"
          >
            <div className="shrink-0 flex flex-col items-center gap-1">
              <div className="w-10 h-10 rounded-full bg-gradient-to-br from-zinc-600 to-zinc-800 flex items-center justify-center text-zinc-100 font-bold text-base uppercase">
                {it.handle.charAt(0)}
              </div>
              <span className="text-[10px] text-zinc-600">#{idx + 1}</span>
            </div>
            <div className="min-w-0 flex-1">
              <div className="flex items-center gap-1.5 text-sm">
                <span className="font-semibold text-zinc-100 truncate">@{it.handle}</span>
                {it.genre && (
                  <span className="shrink-0 text-[10px] px-1.5 py-0.5 rounded bg-zinc-800 text-zinc-400">{it.genre}</span>
                )}
                <span className="ml-auto shrink-0 text-zinc-600 text-xs">↗</span>
              </div>
              {it.body && (
                <p className="mt-1 text-[14px] text-zinc-200 whitespace-pre-wrap leading-relaxed break-words line-clamp-6">
                  {it.body}
                </p>
              )}
              <div className="mt-1.5 flex items-center gap-1 text-rose-400">
                <span className="text-base leading-none">♡</span>
                <span className="font-bold">{compact(it.likes)}</span>
                <span className="text-xs text-zinc-600 ml-1">いいね</span>
              </div>
            </div>
          </a>
        ))}
      </div>
    </main>
  )
}
