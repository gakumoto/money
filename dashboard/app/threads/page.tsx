import fs from 'fs/promises'
import path from 'path'
import Link from 'next/link'
import { getRawContent, listDir } from '@/lib/github'

export const dynamic = 'force-dynamic'

// ローカルfs優先（.env未設定でも動く）→ なければ GitHub フォールバック
async function localList(rel: string): Promise<string[] | null> {
  for (const base of [path.join(process.cwd(), '..'), process.cwd()]) {
    try {
      const names = (await fs.readdir(path.join(base, rel))).filter((n) => n.endsWith('.md'))
      if (names.length) return names
    } catch {
      /* next */
    }
  }
  return null
}

async function localRead(rel: string): Promise<string | null> {
  for (const base of [path.join(process.cwd(), '..'), process.cwd()]) {
    try {
      return await fs.readFile(path.join(base, rel), 'utf-8')
    } catch {
      /* next */
    }
  }
  return null
}

const ACCOUNT = 'gaku_ai_life'
const BASE = `.company/marketing/drafts/${ACCOUNT}`
const DISPLAY_NAME = 'Gaku'
const HANDLE = 'gaku_ai_life'

type State = 'queued' | 'pending' | 'posted' | 'rejected' | 'expired'

const STATE_CONFIG: Record<State, { label: string; icon: string; path: string }> = {
  queued: { label: 'キュー', icon: '📦', path: `${BASE}/queued` },
  pending: { label: '未レビュー', icon: '📝', path: BASE },
  posted: { label: '投稿済', icon: '✅', path: `${BASE}/posted` },
  rejected: { label: '却下', icon: '❌', path: `${BASE}/rejected` },
  expired: { label: '期限切れ', icon: '🕰️', path: `${BASE}/expired` },
}

const PAGE_SIZE = 30

// ── parser ───────────────────────────────────────────────────

interface Draft {
  filename: string
  topic: string | null
  templateType: string | null
  purpose: string | null
  publishAt: string | null
  postedAt: string | null
  goldenSlot: boolean
  sourceResearch: string | null
  metrics: { views?: number; likes?: number; replies?: number; reposts?: number } | null
  body: string
}

function unquote(v: string): string {
  return v.trim().replace(/^["']|["']$/g, '')
}

function getField(yaml: string, key: string): string | null {
  const m = yaml.match(new RegExp(`^${key}:\\s*(.+)$`, 'm'))
  return m ? unquote(m[1]) : null
}

function getMetrics(yaml: string): Draft['metrics'] {
  const block = yaml.match(/^metrics:\s*\n((?:[ \t]+.+\n?)+)/m)?.[1]
  if (!block) return null
  const m: Draft['metrics'] = {}
  const parse = (key: keyof NonNullable<Draft['metrics']>) => {
    const v = block.match(new RegExp(`^\\s+${key}:\\s*(.+)$`, 'm'))?.[1]?.trim()
    if (v && v !== '~' && !isNaN(Number(v))) m[key] = Number(v)
  }
  parse('views'); parse('likes'); parse('replies'); parse('reposts')
  return m && Object.keys(m).length > 0 ? m : null
}

function parseDraft(filename: string, content: string): Draft {
  const fm = content.match(/^---\n([\s\S]*?)\n---\n?([\s\S]*)$/)
  const yaml = fm?.[1] ?? ''
  let body = fm?.[2] ?? content
  body = body.replace(/^【本文】\s*\n?/, '')
  body = body.split(/\n【(?:コメント欄|添付)】/)[0].trim()

  const researchBlock = /^research_used:\s*\n[ \t]*-/m.test(yaml)
  return {
    filename,
    topic: getField(yaml, 'topic'),
    templateType: getField(yaml, 'template_type'),
    purpose: getField(yaml, 'purpose'),
    publishAt: getField(yaml, 'publish_at') ?? getField(yaml, 'target_publish'),
    postedAt: getField(yaml, 'posted_at'),
    goldenSlot: getField(yaml, 'golden_slot') === 'true',
    sourceResearch: getField(yaml, 'source_research') ?? (researchBlock ? 'リサーチ由来' : null),
    metrics: getMetrics(yaml),
    body,
  }
}

// ── utils ────────────────────────────────────────────────────

function shortTime(raw: string | null): string | null {
  if (!raw) return null
  const m = raw.match(/^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2})/)
  if (!m) return raw.slice(0, 16)
  return `${m[2]}/${m[3]} ${m[4]}:${m[5]}`
}

function compactNumber(n: number): string {
  if (n >= 10000) return `${(n / 10000).toFixed(1)}万`
  if (n >= 1000) return `${(n / 1000).toFixed(1)}k`
  return String(n)
}

// ── page ─────────────────────────────────────────────────────

interface PageProps {
  searchParams: { state?: string }
}

export default async function Threads({ searchParams }: PageProps) {
  const stateParam = (searchParams.state ?? 'queued') as State
  const state: State = stateParam in STATE_CONFIG ? stateParam : 'queued'
  const config = STATE_CONFIG[state]

  const allFiles = (await localList(config.path)) ?? (await listDir(config.path))
  const sorted = [...allFiles].sort()
  if (state === 'posted' || state === 'rejected' || state === 'expired') sorted.reverse()
  const visible = sorted.slice(0, PAGE_SIZE)

  const drafts = await Promise.all(
    visible.map(async (name) => {
      const content = (await localRead(`${config.path}/${name}`)) ?? (await getRawContent(`${config.path}/${name}`))
      return content ? parseDraft(name, content) : null
    }),
  )
  const items = drafts.filter((d): d is Draft => d !== null)

  return (
    <main className="min-h-screen bg-black text-zinc-100 pb-20">
      <div className="sticky top-0 z-10 bg-black/90 backdrop-blur border-b border-zinc-800 px-4 py-3">
        <div className="flex items-center justify-between mb-3 max-w-lg mx-auto">
          <span className="font-bold text-base tracking-tight">Threads 投稿</span>
          <span className="text-xs text-zinc-500">{items.length}/{allFiles.length}本</span>
        </div>
        <div className="flex gap-1 overflow-x-auto max-w-lg mx-auto scrollbar-hide">
          {(Object.keys(STATE_CONFIG) as State[]).map((s) => {
            const c = STATE_CONFIG[s]
            const active = s === state
            return (
              <Link
                key={s}
                href={`/threads?state=${s}`}
                className={`shrink-0 text-xs px-3 py-1.5 rounded-full font-medium transition-colors ${
                  active ? 'bg-zinc-100 text-black' : 'bg-zinc-900 text-zinc-400 border border-zinc-800'
                }`}
              >
                {c.icon} {c.label}
              </Link>
            )
          })}
        </div>
      </div>

      <div className="max-w-lg mx-auto">
        {items.length === 0 && (
          <div className="p-10 text-center text-sm text-zinc-500">このタブには投稿がありません</div>
        )}
        {items.map((d) => (
          <ThreadPost key={d.filename} draft={d} state={state} />
        ))}
        {allFiles.length > PAGE_SIZE && (
          <div className="text-center text-xs text-zinc-600 py-4">
            {PAGE_SIZE} 件表示中（全 {allFiles.length} 件）
          </div>
        )}
      </div>
    </main>
  )
}

// ── Threads風カード ────────────────────────────────────────────

function ThreadPost({ draft: d, state }: { draft: Draft; state: State }) {
  const time = state === 'posted' ? shortTime(d.postedAt) : shortTime(d.publishAt)

  return (
    <article className="flex gap-3 px-4 py-4 border-b border-zinc-800/80">
      <div className="shrink-0">
        <div className="w-10 h-10 rounded-full bg-gradient-to-br from-emerald-400 to-cyan-500 flex items-center justify-center text-black font-bold text-lg">
          G
        </div>
      </div>

      <div className="min-w-0 flex-1">
        <div className="flex items-center gap-1.5 text-sm">
          <span className="font-semibold text-zinc-100">{DISPLAY_NAME}</span>
          <span className="text-zinc-500">@{HANDLE}</span>
          {time && <span className="text-zinc-600">· {time}</span>}
          {d.goldenSlot && (
            <span className="ml-auto text-[10px] px-1.5 py-0.5 rounded-full bg-rose-500/15 text-rose-300">勝負枠</span>
          )}
        </div>

        <p className="mt-1 text-[15px] text-zinc-100 whitespace-pre-wrap leading-relaxed break-words">
          {d.body}
        </p>

        <div className="flex flex-wrap items-center gap-1.5 mt-2">
          {d.sourceResearch && (
            <span className="text-[10px] px-1.5 py-0.5 rounded bg-amber-500/15 text-amber-300">🔍 リサーチ由来</span>
          )}
          {d.purpose && <span className="text-[10px] px-1.5 py-0.5 rounded bg-zinc-800 text-zinc-400">{d.purpose}</span>}
          {d.templateType && (
            <span className="text-[10px] px-1.5 py-0.5 rounded bg-zinc-800 text-zinc-500 truncate max-w-[180px]">{d.templateType}</span>
          )}
        </div>

        <div className="flex items-center gap-6 mt-3 text-zinc-500">
          <Action glyph="♡" value={d.metrics?.likes} />
          <Action glyph="💬" value={d.metrics?.replies} />
          <Action glyph="🔁" value={d.metrics?.reposts} />
          <Action glyph="✈" value={d.metrics?.views} />
        </div>
      </div>
    </article>
  )
}

function Action({ glyph, value }: { glyph: string; value?: number }) {
  return (
    <span className="flex items-center gap-1 text-sm">
      <span className="text-base leading-none">{glyph}</span>
      {value !== undefined && <span className="text-xs text-zinc-400">{compactNumber(value)}</span>}
    </span>
  )
}
