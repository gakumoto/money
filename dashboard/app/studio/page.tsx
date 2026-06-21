import { getRawContent } from '@/lib/github'
import AutoRefresh from './AutoRefresh'

export const dynamic = 'force-dynamic'

// ── 型 ───────────────────────────────────────────────
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

// スタッフ別ネオン色
const COLOR: Record<string, { text: string; dot: string; ring: string }> = {
  sakura: { text: 'text-rose-400', dot: 'bg-rose-400', ring: 'ring-rose-500/40' },
  sora: { text: 'text-cyan-400', dot: 'bg-cyan-400', ring: 'ring-cyan-500/40' },
  erika: { text: 'text-emerald-400', dot: 'bg-emerald-400', ring: 'ring-emerald-500/40' },
  nana: { text: 'text-violet-400', dot: 'bg-violet-400', ring: 'ring-violet-500/40' },
  yui: { text: 'text-amber-400', dot: 'bg-amber-400', ring: 'ring-amber-500/40' },
  aoi: { text: 'text-fuchsia-400', dot: 'bg-fuchsia-400', ring: 'ring-fuchsia-500/40' },
}

const STATUS_STYLE: Record<string, string> = {
  完了: 'bg-emerald-500/15 text-emerald-300 border border-emerald-500/30',
  待機: 'bg-zinc-700/40 text-zinc-400 border border-zinc-600/40',
  巡回中: 'bg-rose-500/15 text-rose-300 border border-rose-500/30',
  実行中: 'bg-sky-500/15 text-sky-300 border border-sky-500/30',
}

function n(v: number | null | undefined): string {
  return v === null || v === undefined ? '—' : v.toLocaleString('en-US')
}

export default async function StudioPage() {
  const raw = await getRawContent('.company/reports/studio-data.json')
  let d: StudioData | null = null
  try {
    d = raw ? (JSON.parse(raw) as StudioData) : null
  } catch {
    d = null
  }

  if (!d) {
    return (
      <main className="min-h-screen bg-[#0a0e1a] text-zinc-200 p-6">
        <h1 className="text-xl font-bold">サクラStudio</h1>
        <p className="mt-4 text-zinc-400 text-sm">
          データ未生成です。ターミナルで{' '}
          <code className="text-emerald-400">python scripts/build_studio_data.py --push</code>{' '}
          を実行してください。
        </p>
      </main>
    )
  }

  const { kpi, staff, activity } = d
  const cards = [
    { label: 'リサーチ', who: 'ソラ', value: `${kpi.research.today}`, unit: '件', sub: `総 ${kpi.research.total}件`, color: 'text-cyan-400' },
    { label: '発信インプ', who: 'エリカ', value: n(kpi.impressions.recent7d), unit: '', sub: `本日 ${n(kpi.impressions.today)}`, color: 'text-emerald-400' },
    { label: '交流', who: 'ナナ', value: n(kpi.engagement.replies7d), unit: '件', sub: `7日・返信`, color: 'text-violet-400' },
    { label: 'フォロワー', who: '全体', value: n(kpi.followers), unit: '人', sub: `キュー ${kpi.queued}本`, color: 'text-amber-400' },
    { label: '販売', who: 'アオイ', value: `¥${kpi.sales.yen.toLocaleString('en-US')}`, unit: '', sub: `${kpi.sales.count}件`, color: 'text-fuchsia-400' },
  ]

  return (
    <main className="min-h-screen bg-[#0a0e1a] text-zinc-100 px-4 py-5 pb-20">
      <AutoRefresh seconds={60} />

      {/* ヘッダ */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <h1 className="text-lg font-bold tracking-wide">
            サクラ<span className="text-rose-400">Studio</span>
          </h1>
          <p className="text-[10px] text-zinc-500 uppercase tracking-widest">virtual company</p>
        </div>
        <p className="text-[11px] text-zinc-500">
          更新 {d.generated_at.slice(11, 16)} ・ 60秒ごと自動
        </p>
      </div>

      {/* KPIカード */}
      <section className="grid grid-cols-2 md:grid-cols-5 gap-2.5 mb-5">
        {cards.map((c) => (
          <div key={c.label} className="rounded-xl bg-zinc-900/70 border border-zinc-800 px-3 py-2.5">
            <div className={`text-2xl font-bold leading-tight ${c.color}`}>
              {c.value}
              {c.unit && <span className="text-sm ml-0.5">{c.unit}</span>}
            </div>
            <div className="text-[11px] text-zinc-300 mt-0.5">{c.label}</div>
            <div className="text-[10px] text-zinc-500">{c.who} ・ {c.sub}</div>
          </div>
        ))}
      </section>

      <div className="grid md:grid-cols-3 gap-4">
        {/* オフィス図(Phase1: 簡易) */}
        <section className="md:col-span-2 rounded-2xl bg-gradient-to-b from-zinc-900/80 to-zinc-950 border border-zinc-800 p-4">
          <div className="text-[11px] text-zinc-500 mb-3 uppercase tracking-wider">office</div>
          <div className="grid grid-cols-3 gap-3">
            {staff.map((s) => {
              const col = COLOR[s.id] ?? COLOR.sora
              return (
                <div key={s.id} className="flex flex-col items-center gap-1.5 py-3">
                  {/* デスク */}
                  <div className="w-full h-6 rounded-md bg-zinc-800/80 border border-zinc-700" />
                  {/* キャラ */}
                  <div className={`-mt-7 w-10 h-10 rounded-full ${col.dot} ring-4 ${col.ring} shadow-lg`} />
                  {/* 名札 */}
                  <div className="mt-1 px-2 py-0.5 rounded bg-black/60 text-[10px] whitespace-nowrap">
                    {s.name}
                    <span className="text-zinc-500">（{s.role.split(' ')[0]}）</span>
                  </div>
                  {s.status === '完了' && <span className="text-[9px] text-emerald-400">● 稼働</span>}
                  {s.status === '巡回中' && <span className="text-[9px] text-rose-400">● 巡回</span>}
                  {s.status === '待機' && <span className="text-[9px] text-zinc-600">○ 待機</span>}
                </div>
              )
            })}
          </div>

          {/* アクティビティ */}
          <div className="mt-4 rounded-lg bg-black/40 border border-zinc-800 p-3">
            <div className="text-[10px] text-zinc-500 uppercase tracking-wider mb-2">activity</div>
            <ul className="space-y-1">
              {activity.length === 0 && <li className="text-[11px] text-zinc-600">記録なし</li>}
              {activity.map((a, i) => (
                <li key={i} className="text-[11px] text-zinc-400 flex gap-2">
                  <span className="text-zinc-600 tabular-nums">{a.at}</span>
                  <span className="text-zinc-300">{a.who}</span>
                  <span className="text-emerald-400">{a.action}</span>
                  <span className="truncate text-zinc-500">{a.what}</span>
                </li>
              ))}
            </ul>
          </div>
        </section>

        {/* STAFFパネル */}
        <section className="space-y-2">
          <div className="text-[11px] text-zinc-500 uppercase tracking-wider">staff</div>
          {staff.map((s) => {
            const col = COLOR[s.id] ?? COLOR.sora
            return (
              <div key={s.id} className="rounded-xl bg-zinc-900/70 border border-zinc-800 p-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className={`w-2.5 h-2.5 rounded-full ${col.dot}`} />
                    <span className="font-bold text-sm">{s.name}</span>
                    <span className="text-[10px] text-zinc-500">{s.role}</span>
                  </div>
                  <span className={`text-[10px] px-1.5 py-0.5 rounded ${STATUS_STYLE[s.status] ?? STATUS_STYLE['待機']}`}>
                    {s.status}
                  </span>
                </div>
                <div className="text-[11px] text-zinc-400 mt-1">{s.detail}</div>
                <div className="mt-1.5 text-[11px]">
                  <span className="text-zinc-500">{s.kpiLabel}：</span>
                  <span className={`font-bold ${col.text}`}>{s.kpiValue}</span>
                </div>
              </div>
            )
          })}
        </section>
      </div>
    </main>
  )
}
