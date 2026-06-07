import Link from 'next/link'
import { getRawContent, listDir } from '@/lib/github'

export const dynamic = 'force-dynamic'

const ACCOUNT = 'gaku_ai_life'
const BASE = `.company/marketing/drafts/${ACCOUNT}`

type State = 'pending' | 'queued' | 'posted' | 'rejected' | 'expired'

const STATE_CONFIG: Record<State, { label: string; icon: string; path: string }> = {
  pending: { label: '未レビュー', icon: '📝', path: BASE },
  queued: { label: 'キュー', icon: '📦', path: `${BASE}/queued` },
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
  hookPattern: string | null
  publishAt: string | null
  postedAt: string | null
  createdAt: string | null
  metrics: { views?: number; likes?: number; replies?: number; reposts?: number } | null
  body: string
}

function unquote(v: string): string {
  return v.trim().replace(/^["']|["']$/g, '')
}

function getField(yaml: string, key: string): string | null {
  const re = new RegExp(`^${key}:\\s*(.+)$`, 'm')
  const m = yaml.match(re)
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
  parse('views')
  parse('likes')
  parse('replies')
  parse('reposts')
  return m && Object.keys(m).length > 0 ? m : null
}

function parseDraft(filename: string, content: string): Draft {
  const fm = content.match(/^---\n([\s\S]*?)\n---\n?([\s\S]*)$/)
  const yaml = fm?.[1] ?? ''
  let body = fm?.[2] ?? content
  body = body.replace(/^【本文】\s*\n?/, '').trim()

  return {
    filename,
    topic: getField(yaml, 'topic'),
    templateType: getField(yaml, 'template_type'),
    purpose: getField(yaml, 'purpose'),
    hookPattern: getField(yaml, 'hook_pattern') ?? getField(yaml, 'hook_type'),
    publishAt: getField(yaml, 'publish_at') ?? getField(yaml, 'target_publish'),
    postedAt: getField(yaml, 'posted_at'),
    createdAt: getField(yaml, 'created_at'),
    metrics: getMetrics(yaml),
    body,
  }
}

// ── utils ────────────────────────────────────────────────────

function formatDateTime(raw: string | null): string | null {
  if (!raw) return null
  const m = raw.match(/^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2})/)
  if (!m) return raw.slice(0, 16)
  return `${m[1]}-${m[2]}-${m[3]} ${m[4]}:${m[5]}`
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
  const stateParam = (searchParams.state ?? 'posted') as State
  const state: State = stateParam in STATE_CONFIG ? stateParam : 'posted'
  const config = STATE_CONFIG[state]

  // listDir で .md ファイル名取得（同名サブフォルダは listDir 内のフィルタで .md だけ）
  const allFiles = await listDir(config.path)
  // 新しい順にソート（ファイル名先頭が日付）
  const sorted = [...allFiles].sort().reverse()
  const visible = sorted.slice(0, PAGE_SIZE)

  // 並列で本文取得
  const drafts = await Promise.all(
    visible.map(async (name) => {
      const content = await getRawContent(`${config.path}/${name}`)
      return content ? parseDraft(name, content) : null
    }),
  )
  const items = drafts.filter((d): d is Draft => d !== null)

  return (
    <main className="min-h-screen bg-zinc-950 text-zinc-100 pb-20">
      <div className="sticky top-0 z-10 bg-zinc-950/95 backdrop-blur border-b border-zinc-800 px-4 py-3">
        <div className="flex items-center justify-between mb-3">
          <span className="font-bold text-sm tracking-wide text-zinc-100">
            {config.icon} Threads 投稿 — {config.label}
          </span>
          <span className="text-xs text-zinc-500">
            {items.length}/{allFiles.length}本
          </span>
        </div>

        {/* タブ切替 */}
        <div className="flex gap-1 overflow-x-auto -mx-1 px-1 pb-1 scrollbar-hide">
          {(Object.keys(STATE_CONFIG) as State[]).map((s) => {
            const c = STATE_CONFIG[s]
            const active = s === state
            return (
              <Link
                key={s}
                href={`/threads?state=${s}`}
                className={`shrink-0 text-xs px-3 py-1.5 rounded-full font-medium transition-colors ${
                  active
                    ? 'bg-emerald-500 text-zinc-950'
                    : 'bg-zinc-900 text-zinc-400 border border-zinc-800'
                }`}
              >
                {c.icon} {c.label}
              </Link>
            )
          })}
        </div>
      </div>

      <div className="max-w-lg mx-auto px-4 pt-4 space-y-3">
        {items.length === 0 && (
          <div className="bg-zinc-900 rounded-xl border border-zinc-800 p-6 text-center text-sm text-zinc-500">
            このタブには投稿がありません
          </div>
        )}
        {items.map((d) => (
          <ThreadCard key={d.filename} draft={d} state={state} />
        ))}
        {allFiles.length > PAGE_SIZE && (
          <div className="text-center text-xs text-zinc-600 py-4">
            最新 {PAGE_SIZE} 件を表示中（全 {allFiles.length} 件）
          </div>
        )}
      </div>
    </main>
  )
}

// ── components ────────────────────────────────────────────────

function ThreadCard({ draft: d, state }: { draft: Draft; state: State }) {
  const publish = formatDateTime(d.publishAt)
  const posted = formatDateTime(d.postedAt)
  const dateLabel = state === 'posted' ? posted : publish

  return (
    <article className="bg-zinc-900 rounded-xl border border-zinc-800 p-4">
      <div className="flex items-center justify-between mb-2 gap-2">
        <span className="text-[10px] text-zinc-600 truncate font-mono">{d.filename}</span>
      </div>

      {d.topic && (
        <h2 className="text-sm font-semibold text-zinc-100 leading-snug mb-2">{d.topic}</h2>
      )}

      <div className="flex flex-wrap gap-1.5 mb-3">
        {dateLabel && <Tag color="emerald">🕒 {dateLabel}</Tag>}
        {d.purpose && <Tag color="zinc">{d.purpose}</Tag>}
        {d.templateType && <Tag color="zinc">{d.templateType}</Tag>}
        {d.hookPattern && <Tag color="zinc">フック: {d.hookPattern}</Tag>}
      </div>

      {d.metrics && (
        <div className="flex flex-wrap gap-3 mb-3 text-xs">
          {d.metrics.views !== undefined && (
            <Metric icon="👁" value={compactNumber(d.metrics.views)} label="閲覧" />
          )}
          {d.metrics.likes !== undefined && (
            <Metric icon="❤️" value={compactNumber(d.metrics.likes)} label="いいね" />
          )}
          {d.metrics.replies !== undefined && (
            <Metric icon="💬" value={compactNumber(d.metrics.replies)} label="返信" />
          )}
          {d.metrics.reposts !== undefined && (
            <Metric icon="🔁" value={compactNumber(d.metrics.reposts)} label="再投稿" />
          )}
        </div>
      )}

      <pre className="text-sm text-zinc-200 whitespace-pre-wrap leading-relaxed font-sans bg-zinc-950/50 rounded-lg p-3 border border-zinc-800/50">
        {d.body}
      </pre>
    </article>
  )
}

function Tag({
  children,
  color = 'zinc',
}: {
  children: React.ReactNode
  color?: 'zinc' | 'emerald'
}) {
  const styles: Record<string, string> = {
    zinc: 'bg-zinc-800 text-zinc-400',
    emerald: 'bg-emerald-950/60 text-emerald-400',
  }
  return (
    <span className={`text-[11px] px-2 py-0.5 rounded ${styles[color]}`}>{children}</span>
  )
}

function Metric({ icon, value, label }: { icon: string; value: string; label: string }) {
  return (
    <div className="flex items-baseline gap-1">
      <span>{icon}</span>
      <span className="font-medium text-zinc-100">{value}</span>
      <span className="text-zinc-600">{label}</span>
    </div>
  )
}
