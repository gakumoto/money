import fs from 'fs/promises'
import path from 'path'
import { getRawContent } from '@/lib/github'
import AutoRefresh from './AutoRefresh'
import OfficeScene from './OfficeScene'

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

const ACCENT: Record<string, { text: string; border: string; dot: string }> = {
  sakura: { text: 'text-rose-400', border: 'border-l-rose-500', dot: 'bg-rose-400' },
  sora: { text: 'text-cyan-400', border: 'border-l-cyan-500', dot: 'bg-cyan-400' },
  erika: { text: 'text-blue-400', border: 'border-l-blue-500', dot: 'bg-blue-400' },
  nana: { text: 'text-violet-400', border: 'border-l-violet-500', dot: 'bg-violet-400' },
  yui: { text: 'text-amber-400', border: 'border-l-amber-500', dot: 'bg-amber-400' },
  aoi: { text: 'text-fuchsia-400', border: 'border-l-fuchsia-500', dot: 'bg-fuchsia-400' },
}
const BADGE: Record<string, string> = {
  完了: 'bg-emerald-500/15 text-emerald-300',
  待機: 'bg-zinc-700/40 text-zinc-400',
  巡回中: 'bg-rose-500/15 text-rose-300',
  統括: 'bg-rose-500/20 text-rose-300',
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
      <AutoRefresh seconds={60} />

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

      <div className="grid lg:grid-cols-[1fr_330px] gap-4 p-4">
        {/* オフィス＋アクティビティ */}
        <div className="relative rounded-2xl overflow-hidden border border-zinc-800 bg-[#0a0e1a]">
          <OfficeScene staff={staff} />
          <div className="absolute bottom-2 left-2 w-56 rounded-lg bg-black/70 backdrop-blur border border-zinc-800 p-2.5">
            <div className="text-[10px] text-zinc-500 uppercase tracking-wider mb-1">activity</div>
            <ul className="space-y-0.5">
              {activity.length === 0 && <li className="text-[11px] text-zinc-600">記録なし</li>}
              {activity.map((a, i) => (
                <li key={i} className="text-[11px] text-zinc-400 flex gap-1.5 truncate">
                  <span className="text-zinc-600 tabular-nums">{a.at}</span>
                  <span className="text-zinc-300">{a.who}</span>
                  <span className="text-emerald-400">{a.action}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* STAFFパネル */}
        <aside>
          <div className="flex items-center justify-between mb-2">
            <div>
              <h1 className="text-base font-bold">サクラ<span className="text-rose-400">Studio</span></h1>
              <p className="text-[10px] text-zinc-500 uppercase tracking-widest">staff</p>
            </div>
            <span className="text-[11px] text-emerald-400">● {d.generated_at.slice(11, 16)}</span>
          </div>
          <div className="space-y-2">
            {staff.map((s) => {
              const a = ACCENT[s.id] ?? ACCENT.sora
              return (
                <div key={s.id} className={`rounded-xl bg-[#121826] border border-zinc-800 border-l-4 ${a.border} p-3`}>
                  <div className="flex items-start justify-between">
                    <div>
                      <div className="font-bold text-sm">{s.name}<span className="text-[10px] text-zinc-500 ml-1">{s.role}</span></div>
                      <div className="text-[11px] text-zinc-400 mt-0.5">{s.detail}</div>
                    </div>
                    <span className={`shrink-0 text-[10px] px-1.5 py-0.5 rounded ${BADGE[s.status] ?? BADGE['待機']}`}>{s.status}</span>
                  </div>
                  {s.id === 'sakura' ? (
                    <div className="mt-2 text-[11px] text-rose-300">▶ 社内を巡回中</div>
                  ) : (
                    <div className="mt-2 rounded-lg bg-black/30 px-2.5 py-1.5">
                      {s.status === '完了' ? (
                        <div className="text-[11px]">
                          <span className="text-emerald-400">✓ </span>
                          <span className="text-zinc-300">{s.kpiLabel} </span>
                          <span className={`font-bold ${a.text}`}>{s.kpiValue}</span>
                        </div>
                      ) : (
                        <div className="text-[11px] text-zinc-500">まだ成果はありません</div>
                      )}
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        </aside>
      </div>
    </main>
  )
}
