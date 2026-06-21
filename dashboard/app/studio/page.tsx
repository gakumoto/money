import fs from 'fs/promises'
import path from 'path'
import { getRawContent } from '@/lib/github'
import StudioBoard from './StudioBoard'

export const dynamic = 'force-dynamic'

interface Staff {
  id: string
  name: string
  role: string
  status: string
  detail: string
  kpiLabel: string
  kpiValue: string
}
interface StudioData {
  generated_at: string
  kpi: {
    research: { today: number; total: number }
    impressions: { recent7d: number | null; today: number | null }
    engagement: { replies7d: number | null; likes7d: number | null }
    followers: number | null
    sales: { yen: number; count: number }
    queued: number
  }
  staff: Staff[]
  activity: { who: string; action: string; what: string; at: string }[]
}

async function loadStudio(): Promise<StudioData | null> {
  for (const p of [
    path.join(process.cwd(), '..', '.company', 'reports', 'studio-data.json'),
    path.join(process.cwd(), '.company', 'reports', 'studio-data.json'),
  ]) {
    try {
      return JSON.parse(await fs.readFile(p, 'utf-8')) as StudioData
    } catch {
      /* next */
    }
  }
  try {
    const raw = await getRawContent('.company/reports/studio-data.json')
    return raw ? (JSON.parse(raw) as StudioData) : null
  } catch {
    return null
  }
}

function n(v: number | null | undefined): string {
  return v === null || v === undefined ? '—' : v.toLocaleString('en-US')
}

export default async function StudioPage() {
  const d = await loadStudio()
  if (!d) {
    return (
      <main className="min-h-screen bg-[#0a0e1a] text-zinc-200 p-6">
        <h1 className="text-xl font-bold">サクラStudio</h1>
        <p className="mt-4 text-zinc-400 text-sm">
          データ未生成です。<code className="text-emerald-400">python scripts/build_studio_data.py</code> を実行してください。
        </p>
      </main>
    )
  }
  const { kpi, staff, activity } = d
  const cards = [
    { big: `${kpi.research.today}`, unit: '件', label: 'リサーチ（ソラ）', sub: `総 ${kpi.research.total}件`, color: 'text-cyan-400' },
    { big: n(kpi.impressions.recent7d), unit: '', label: '発信インプ（エリカ）', sub: `本日 ${n(kpi.impressions.today)}`, color: 'text-blue-300' },
    { big: n(kpi.engagement.replies7d), unit: '件', label: '交流（ナナ）', sub: '7日・返信', color: 'text-violet-300' },
    { big: n(kpi.followers), unit: '人', label: 'フォロワー（全体）', sub: `キュー ${kpi.queued}本`, color: 'text-amber-300' },
    { big: `¥${kpi.sales.yen.toLocaleString('en-US')}`, unit: '', label: '販売（アオイ）', sub: `${kpi.sales.count}件`, color: 'text-fuchsia-300' },
  ]

  return (
    <main className="min-h-screen bg-[#0a0e1a] text-zinc-100 pb-16">
      {/* KPIバー（全幅） */}
      <header className="grid grid-cols-2 md:grid-cols-5 border-b border-zinc-800">
        {cards.map((c, i) => (
          <div key={c.label} className={`px-5 py-3 ${i ? 'md:border-l border-zinc-800' : ''}`}>
            <div className={`text-3xl font-extrabold leading-none ${c.color}`}>
              {c.big}
              {c.unit && <span className="text-base ml-1 font-bold">{c.unit}</span>}
            </div>
            <div className="text-[11px] text-zinc-300 mt-1">{c.label}</div>
            <div className="text-[10px] text-zinc-500">{c.sub}</div>
          </div>
        ))}
      </header>

      <StudioBoard staff={staff} activity={activity} generatedAt={d.generated_at} />
    </main>
  )
}
