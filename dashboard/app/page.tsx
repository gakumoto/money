import type { ReactNode } from 'react'
import Link from 'next/link'
import { getFileContent, listDir } from '@/lib/github'

const DEADLINE = '2026-07-13'
const START_DATE = '2026-05-13'
const ACCOUNT = 'gaku_ai_life'
const DRAFTS = `.company/marketing/drafts/${ACCOUNT}`

// ── date utils ──────────────────────────────────────────────

function todayJST(): string {
  const now = new Date()
  const jst = new Date(now.getTime() + 9 * 3600 * 1000)
  const y = jst.getUTCFullYear()
  const m = String(jst.getUTCMonth() + 1).padStart(2, '0')
  const d = String(jst.getUTCDate()).padStart(2, '0')
  return `${y}-${m}-${d}`
}

function dateDiff(from: string, to: string): number {
  const ms = new Date(to + 'T00:00:00Z').getTime() - new Date(from + 'T00:00:00Z').getTime()
  return Math.round(ms / 86400000)
}

function dateMinusDays(date: string, days: number): string {
  const d = new Date(date + 'T00:00:00Z')
  d.setUTCDate(d.getUTCDate() - days)
  return d.toISOString().slice(0, 10)
}

function fileDate(name: string): string {
  return name.slice(0, 10)
}

// ── markdown parser ──────────────────────────────────────────

interface Task {
  text: string
  done: boolean
  priority: string | null
}

interface Section {
  title: string
  tasks: Task[]
}

function parseTodo(content: string): Section[] {
  const lines = content.split('\n')
  const sections: Section[] = []
  let current: Section = { title: '', tasks: [] }

  for (const line of lines) {
    if (line.startsWith('## ')) {
      if (current.title || current.tasks.length) sections.push(current)
      current = { title: line.replace(/^## /, ''), tasks: [] }
    } else if (/^- \[[ x]\]/.test(line)) {
      const done = line.includes('[x]')
      const text = line.replace(/^- \[[ x]\] /, '').replace(/ \|.*$/, '').trim()
      const priority = line.match(/優先度: (高|通常|低)/)?.[1] ?? null
      current.tasks.push({ text, done, priority })
    }
  }
  if (current.title || current.tasks.length) sections.push(current)
  return sections.filter((s) => s.tasks.length > 0)
}

// ── page ─────────────────────────────────────────────────────

export default async function Dashboard() {
  const today = todayJST()
  const daysLeft = dateDiff(today, DEADLINE)
  const elapsed = dateDiff(START_DATE, today)
  const totalDays = dateDiff(START_DATE, DEADLINE)
  const progress = Math.min(100, Math.round((elapsed / totalDays) * 100))
  const weekAgo = dateMinusDays(today, 7)

  const [todoContent, reportContent, queued, posted, expired, rejected] = await Promise.all([
    getFileContent(`.company/secretary/todos/${today}.md`),
    getFileContent(`.company/secretary/reports/${today}.md`),
    listDir(`${DRAFTS}/queued`),
    listDir(`${DRAFTS}/posted`),
    listDir(`${DRAFTS}/expired`),
    listDir(`${DRAFTS}/rejected`),
  ])

  const todoSections = todoContent ? parseTodo(todoContent) : []
  const allTasks = todoSections.flatMap((s) => s.tasks)
  const pendingCount = allTasks.filter((t) => !t.done).length
  const doneCount = allTasks.filter((t) => t.done).length

  const staleQueued = queued.filter((name) => dateDiff(fileDate(name), today) >= 7)
  const thisWeekPosted = posted.filter((name) => fileDate(name) >= weekAgo)

  return (
    <main className="min-h-screen bg-zinc-950 text-zinc-100 pb-10">
      {/* sticky header */}
      <div className="sticky top-0 z-10 bg-zinc-950/95 backdrop-blur border-b border-zinc-800 px-4 py-3 flex items-center justify-between">
        <span className="font-bold text-sm tracking-wide text-zinc-100">Company</span>
        <div className="flex items-center gap-3 text-xs">
          <span className="text-zinc-500">{today}</span>
          <span className={`font-semibold ${daysLeft <= 14 ? 'text-red-400' : 'text-emerald-400'}`}>
            残{daysLeft}日
          </span>
        </div>
      </div>

      <div className="max-w-lg mx-auto px-4 pt-4 space-y-4">
        {/* roadmap */}
        <Card title="🎯 100kロードマップ">
          <div className="space-y-2">
            <div className="flex justify-between text-xs text-zinc-500">
              <span>Phase 1</span>
              <span>{elapsed}日経過 / {totalDays}日</span>
            </div>
            <div className="w-full bg-zinc-800 rounded-full h-2">
              <div
                className="bg-emerald-500 h-2 rounded-full"
                style={{ width: `${progress}%` }}
              />
            </div>
            <div className="flex justify-between text-xs">
              <span className="text-zinc-600">2026-05-13</span>
              <span className="text-zinc-300 font-medium">{progress}%</span>
              <span className="text-zinc-600">2026-07-13</span>
            </div>
          </div>
        </Card>

        {/* todo */}
        <Card
          title="📋 今日のTODO"
          badge={
            allTasks.length > 0
              ? `未完了 ${pendingCount} / 完了 ${doneCount}`
              : undefined
          }
          badgeColor={pendingCount === 0 ? 'emerald' : 'amber'}
        >
          {todoContent ? (
            <div className="space-y-5">
              {todoSections.map((section) => (
                <div key={section.title}>
                  {section.title && (
                    <div className="text-xs text-zinc-600 uppercase tracking-wider mb-2">
                      {section.title}
                    </div>
                  )}
                  <div className="space-y-2">
                    {section.tasks.map((task, i) => (
                      <div key={i} className="flex items-start gap-2">
                        <span className={`mt-0.5 text-sm leading-none shrink-0 ${task.done ? 'text-emerald-500' : 'text-zinc-600'}`}>
                          {task.done ? '✓' : '○'}
                        </span>
                        <span className={`text-sm leading-snug flex-1 ${task.done ? 'line-through text-zinc-600' : 'text-zinc-200'}`}>
                          {task.text}
                        </span>
                        {task.priority === '高' && !task.done && (
                          <span className="shrink-0 text-xs text-red-400 font-medium bg-red-950/60 px-1.5 py-0.5 rounded">
                            高
                          </span>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-zinc-600">今日のTODOファイルがありません</p>
          )}
        </Card>

        {/* queue */}
        <Link href="/queue" className="block">
          <Card title="📦 投稿キュー" linkHint>
            <div className="space-y-3">
              <div className="flex items-center gap-4">
                <div className="text-center">
                  <div className="text-3xl font-bold text-zinc-100 leading-none">{queued.length}</div>
                  <div className="text-xs text-zinc-500 mt-1">本 待機中</div>
                </div>
                {staleQueued.length > 0 && (
                  <div className="flex-1 bg-amber-950/40 border border-amber-900/50 text-amber-400 rounded-lg px-3 py-2 text-sm">
                    ⚠️ 7日超え: <strong>{staleQueued.length}本</strong> — 要確認
                  </div>
                )}
                {staleQueued.length === 0 && queued.length > 0 && (
                  <div className="flex-1 bg-emerald-950/40 border border-emerald-900/50 text-emerald-400 rounded-lg px-3 py-2 text-sm">
                    鮮度OK
                  </div>
                )}
              </div>
              {staleQueued.length > 0 && (
                <div className="space-y-1">
                  {staleQueued.slice(0, 4).map((name) => (
                    <div key={name} className="text-xs text-amber-700 truncate">
                      {name}
                    </div>
                  ))}
                  {staleQueued.length > 4 && (
                    <div className="text-xs text-zinc-600">…他{staleQueued.length - 4}本</div>
                  )}
                </div>
              )}
            </div>
          </Card>
        </Link>

        {/* report */}
        <Card title="📝 今日の日報">
          {reportContent ? (
            <pre className="text-xs text-zinc-300 whitespace-pre-wrap leading-relaxed font-mono">
              {reportContent.replace(/^---[\s\S]*?---\n/, '').slice(0, 800)}
              {reportContent.length > 800 ? '\n…' : ''}
            </pre>
          ) : (
            <p className="text-sm text-zinc-600">まだありません</p>
          )}
        </Card>

        {/* analysis */}
        <Card title="📈 分析">
          <div className="grid grid-cols-2 gap-3">
            <Stat label="今週投稿" value={thisWeekPosted.length} unit="本" color="emerald" />
            <Stat label="queued" value={queued.length} unit="本" />
            <Stat label="posted 累計" value={posted.length} unit="本" />
            <Stat label="expired" value={expired.length} unit="本" color="amber" />
            <Stat label="rejected" value={rejected.length} unit="本" color="zinc" />
          </div>
        </Card>
      </div>
    </main>
  )
}

// ── components ────────────────────────────────────────────────

function Card({
  title,
  children,
  badge,
  badgeColor = 'zinc',
  linkHint = false,
}: {
  title: string
  children: ReactNode
  badge?: string
  badgeColor?: 'zinc' | 'amber' | 'emerald'
  linkHint?: boolean
}) {
  const badgeStyles: Record<string, string> = {
    zinc: 'bg-zinc-800 text-zinc-400',
    amber: 'bg-amber-950 text-amber-400',
    emerald: 'bg-emerald-950 text-emerald-400',
  }
  return (
    <div className="bg-zinc-900 rounded-xl border border-zinc-800 p-4">
      <div className="flex items-center justify-between mb-3">
        <h2 className="text-sm font-semibold text-zinc-200">{title}</h2>
        {badge ? (
          <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${badgeStyles[badgeColor]}`}>
            {badge}
          </span>
        ) : linkHint ? (
          <span className="text-xs text-zinc-600">一覧 →</span>
        ) : null}
      </div>
      {children}
    </div>
  )
}

function Stat({
  label,
  value,
  unit,
  color = 'white',
}: {
  label: string
  value: number
  unit: string
  color?: 'white' | 'amber' | 'zinc' | 'emerald'
}) {
  const valueStyles: Record<string, string> = {
    white: 'text-zinc-100',
    amber: 'text-amber-400',
    zinc: 'text-zinc-500',
    emerald: 'text-emerald-400',
  }
  return (
    <div className="bg-zinc-800/50 rounded-lg px-3 py-2.5">
      <div className="text-xs text-zinc-500 mb-1">{label}</div>
      <div className={`text-2xl font-bold leading-none ${valueStyles[color]}`}>
        {value}
        <span className="text-xs font-normal text-zinc-500 ml-0.5">{unit}</span>
      </div>
    </div>
  )
}
