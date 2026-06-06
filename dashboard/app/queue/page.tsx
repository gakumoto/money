import { getRawContent, listDir } from '@/lib/github'

export const dynamic = 'force-dynamic'

const ACCOUNT = 'gaku_ai_life'
const DRAFTS = `.company/marketing/drafts/${ACCOUNT}/queued`

// ── date utils ──────────────────────────────────────────────

function todayJST(): string {
  const now = new Date()
  const jst = new Date(now.getTime() + 9 * 3600 * 1000)
  return jst.toISOString().slice(0, 10)
}

function dateDiff(from: string, to: string): number {
  const ms = new Date(to + 'T00:00:00Z').getTime() - new Date(from + 'T00:00:00Z').getTime()
  return Math.round(ms / 86400000)
}

function fileDate(name: string): string {
  return name.slice(0, 10)
}

function formatPublishAt(raw: string | null): string | null {
  if (!raw) return null
  const m = raw.match(/^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2})/)
  if (!m) return raw.slice(0, 16)
  return `${m[1]}-${m[2]}-${m[3]} ${m[4]}:${m[5]}`
}

// ── parser ───────────────────────────────────────────────────

interface Draft {
  filename: string
  topic: string | null
  templateType: string | null
  purpose: string | null
  hookPattern: string | null
  publishAt: string | null
  createdAt: string | null
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
    createdAt: getField(yaml, 'created_at'),
    body,
  }
}

// ── page ─────────────────────────────────────────────────────

export default async function Queue() {
  const today = todayJST()
  const names = await listDir(DRAFTS)
  const sorted = [...names].sort()

  const drafts = await Promise.all(
    sorted.map(async (name) => {
      const content = await getRawContent(`${DRAFTS}/${name}`)
      return content ? parseDraft(name, content) : null
    }),
  )
  const items = drafts.filter((d): d is Draft => d !== null)

  const staleCount = items.filter((d) => dateDiff(fileDate(d.filename), today) >= 7).length

  return (
    <main className="min-h-screen bg-zinc-950 text-zinc-100 pb-10">
      <div className="sticky top-0 z-10 bg-zinc-950/95 backdrop-blur border-b border-zinc-800 px-4 py-3 flex items-center justify-between">
        <span className="font-bold text-sm tracking-wide text-zinc-100">📦 投稿キュー</span>
        <div className="flex items-center gap-2 text-xs">
          <span className="text-zinc-500">{items.length}本</span>
          {staleCount > 0 && (
            <span className="text-amber-400 font-medium">⚠ 7日超 {staleCount}</span>
          )}
        </div>
      </div>

      <div className="max-w-lg mx-auto px-4 pt-4 space-y-3">
        {items.length === 0 && (
          <div className="bg-zinc-900 rounded-xl border border-zinc-800 p-6 text-center text-sm text-zinc-500">
            キューは空です
          </div>
        )}
        {items.map((d) => {
          const stale = dateDiff(fileDate(d.filename), today) >= 7
          const publish = formatPublishAt(d.publishAt)
          return (
            <article
              key={d.filename}
              className={`bg-zinc-900 rounded-xl border p-4 ${
                stale ? 'border-amber-900/60' : 'border-zinc-800'
              }`}
            >
              <div className="flex items-center justify-between mb-2 gap-2">
                <span className="text-[10px] text-zinc-600 truncate font-mono">{d.filename}</span>
                {stale && (
                  <span className="text-[10px] text-amber-400 bg-amber-950/60 px-1.5 py-0.5 rounded shrink-0">
                    {dateDiff(fileDate(d.filename), today)}日経過
                  </span>
                )}
              </div>

              {d.topic && (
                <h2 className="text-sm font-semibold text-zinc-100 leading-snug mb-2">
                  {d.topic}
                </h2>
              )}

              <div className="flex flex-wrap gap-1.5 mb-3">
                {publish && (
                  <Tag color="emerald">🕒 {publish}</Tag>
                )}
                {d.purpose && <Tag color="zinc">{d.purpose}</Tag>}
                {d.templateType && <Tag color="zinc">{d.templateType}</Tag>}
                {d.hookPattern && <Tag color="zinc">フック: {d.hookPattern}</Tag>}
              </div>

              <pre className="text-sm text-zinc-200 whitespace-pre-wrap leading-relaxed font-sans bg-zinc-950/50 rounded-lg p-3 border border-zinc-800/50">
                {d.body}
              </pre>
            </article>
          )
        })}
      </div>
    </main>
  )
}

// ── components ────────────────────────────────────────────────

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
    <span className={`text-[11px] px-2 py-0.5 rounded ${styles[color]}`}>
      {children}
    </span>
  )
}
