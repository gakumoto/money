'use client'
// 社員を選択 → 詳細パネル（読み取り専用）を開く操作盤。
// オフィスのキャラ/名札クリック、または右のSTAFFカードクリックで選択。
// 自動更新は router.refresh()（ソフト更新）でパネルを閉じずにデータ反映。

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import OfficeScene from './OfficeScene'

export interface Staff {
  id: string
  name: string
  role: string
  status: string
  detail: string
  kpiLabel: string
  kpiValue: string
}
interface Activity {
  who: string
  action: string
  what: string
  at: string
}

const ACCENT: Record<string, { text: string; border: string; ring: string }> = {
  sakura: { text: 'text-rose-400', border: 'border-l-rose-500', ring: 'ring-rose-500/40' },
  sora: { text: 'text-cyan-400', border: 'border-l-cyan-500', ring: 'ring-cyan-500/40' },
  erika: { text: 'text-blue-400', border: 'border-l-blue-500', ring: 'ring-blue-500/40' },
  nana: { text: 'text-violet-400', border: 'border-l-violet-500', ring: 'ring-violet-500/40' },
  yui: { text: 'text-amber-400', border: 'border-l-amber-500', ring: 'ring-amber-500/40' },
  aoi: { text: 'text-fuchsia-400', border: 'border-l-fuchsia-500', ring: 'ring-fuchsia-500/40' },
}
const BADGE: Record<string, string> = {
  完了: 'bg-emerald-500/15 text-emerald-300',
  待機: 'bg-zinc-700/40 text-zinc-400',
  巡回中: 'bg-rose-500/15 text-rose-300',
  統括: 'bg-rose-500/20 text-rose-300',
}
// 社員ごとの担当（役割の補足・どこを見ているか）
const INFO: Record<string, { mission: string; folder: string }> = {
  sakura: { mission: '全体を統括し、各社員に確認・指示を出す。', folder: '.company/ 全体' },
  sora: { mission: '競合・トレンドを調査し、投稿ネタを供給する。', folder: '.company/research/' },
  erika: { mission: 'Threadsで発信し、流入をつくる。', folder: '.company/marketing/drafts/gaku_ai_life/' },
  nana: { mission: 'リプ・引用でフォロワーと関係を築く（アウトバウンド絡み）。', folder: '.company/marketing/' },
  yui: { mission: '無料note・記事で教育し、導線をつくる。', folder: '.company/products/articles/' },
  aoi: { mission: '有料note・ファネルで収益化する。', folder: '.company/products/' },
}

export default function StudioBoard({
  staff, activity, generatedAt,
}: {
  staff: Staff[]; activity: Activity[]; generatedAt: string
}) {
  const router = useRouter()
  const [selectedId, setSelectedId] = useState<string | null>(null)

  // ソフト更新（60秒ごと・選択パネルは閉じない）
  useEffect(() => {
    const t = setInterval(() => router.refresh(), 60000)
    return () => clearInterval(t)
  }, [router])

  const selected = staff.find((s) => s.id === selectedId) ?? null
  const a = selected ? ACCENT[selected.id] ?? ACCENT.sora : ACCENT.sora
  const info = selected ? INFO[selected.id] : null
  const recent = selected ? activity.filter((x) => x.who === selected.name).slice(0, 6) : []

  return (
    <div className="grid lg:grid-cols-[1fr_330px] gap-4 p-4">
      {/* オフィス＋アクティビティ */}
      <div className="relative rounded-2xl overflow-hidden border border-zinc-800 bg-[#0a0e1a]">
        <OfficeScene staff={staff} selectedId={selectedId ?? undefined} onSelect={setSelectedId} />
        <div className="absolute top-2 left-2 text-[10px] text-zinc-500 bg-black/50 rounded px-2 py-1">
          社員をタップで詳細
        </div>
        <div className="absolute bottom-2 left-2 w-56 rounded-lg bg-black/70 backdrop-blur border border-zinc-800 p-2.5">
          <div className="text-[10px] text-zinc-500 uppercase tracking-wider mb-1">activity</div>
          <ul className="space-y-0.5">
            {activity.length === 0 && <li className="text-[11px] text-zinc-600">記録なし</li>}
            {activity.map((x, i) => (
              <li key={i} className="text-[11px] text-zinc-400 flex gap-1.5 truncate">
                <span className="text-zinc-600 tabular-nums">{x.at}</span>
                <span className="text-zinc-300">{x.who}</span>
                <span className="text-emerald-400">{x.action}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* STAFFパネル（カードクリックでも選択） */}
      <aside>
        <div className="flex items-center justify-between mb-2">
          <div>
            <h1 className="text-base font-bold">サクラ<span className="text-rose-400">Studio</span></h1>
            <p className="text-[10px] text-zinc-500 uppercase tracking-widest">staff</p>
          </div>
          <span className="text-[11px] text-emerald-400">● {generatedAt.slice(11, 16)}</span>
        </div>
        <div className="space-y-2">
          {staff.map((s) => {
            const ac = ACCENT[s.id] ?? ACCENT.sora
            const on = s.id === selectedId
            return (
              <button
                key={s.id}
                onClick={() => setSelectedId(on ? null : s.id)}
                className={`w-full text-left rounded-xl bg-[#121826] border border-zinc-800 border-l-4 ${ac.border} p-3 transition ${on ? `ring-2 ${ac.ring}` : 'hover:bg-[#161d2e]'}`}
              >
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
                        <span className={`font-bold ${ac.text}`}>{s.kpiValue}</span>
                      </div>
                    ) : (
                      <div className="text-[11px] text-zinc-500">まだ成果はありません</div>
                    )}
                  </div>
                )}
              </button>
            )
          })}
        </div>
      </aside>

      {/* 詳細ドロワー */}
      {selected && (
        <div className="fixed inset-0 z-50 flex justify-end" onClick={() => setSelectedId(null)}>
          <div className="absolute inset-0 bg-black/50" />
          <div
            className={`relative w-full max-w-sm h-full bg-[#0d1320] border-l-4 ${a.border} shadow-2xl p-5 overflow-y-auto`}
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-start justify-between">
              <div>
                <div className="text-xl font-bold">{selected.name}</div>
                <div className={`text-xs ${a.text}`}>{selected.role}</div>
              </div>
              <button onClick={() => setSelectedId(null)} className="text-zinc-500 hover:text-zinc-200 text-2xl leading-none">×</button>
            </div>

            <div className="mt-3">
              <span className={`text-[11px] px-2 py-0.5 rounded ${BADGE[selected.status] ?? BADGE['待機']}`}>{selected.status}</span>
            </div>

            <div className="mt-4 rounded-lg bg-black/30 p-3">
              <div className="text-[10px] text-zinc-500 uppercase tracking-wider">今の成果</div>
              {selected.id === 'sakura' ? (
                <div className="text-sm text-rose-300 mt-1">▶ 社内を巡回・統括中</div>
              ) : selected.status === '完了' ? (
                <div className="text-sm mt-1">
                  <span className="text-emerald-400">✓ </span>
                  <span className="text-zinc-300">{selected.kpiLabel} </span>
                  <span className={`font-bold ${a.text}`}>{selected.kpiValue}</span>
                </div>
              ) : (
                <div className="text-sm text-zinc-500 mt-1">まだ成果はありません</div>
              )}
            </div>

            <div className="mt-4">
              <div className="text-[10px] text-zinc-500 uppercase tracking-wider">役割</div>
              <p className="text-sm text-zinc-300 mt-1">{selected.detail}</p>
              {info && <p className="text-[12px] text-zinc-400 mt-1">{info.mission}</p>}
            </div>

            {info && (
              <div className="mt-4">
                <div className="text-[10px] text-zinc-500 uppercase tracking-wider">担当</div>
                <code className="text-[12px] text-emerald-300 break-all">{info.folder}</code>
              </div>
            )}

            <div className="mt-4">
              <div className="text-[10px] text-zinc-500 uppercase tracking-wider">最近の動き</div>
              <ul className="mt-1 space-y-1">
                {recent.length === 0 && <li className="text-[12px] text-zinc-600">記録なし</li>}
                {recent.map((x, i) => (
                  <li key={i} className="text-[12px] text-zinc-400 flex gap-2">
                    <span className="text-zinc-600 tabular-nums">{x.at}</span>
                    <span className="text-emerald-400">{x.action}</span>
                    <span className="text-zinc-300 truncate">{x.what}</span>
                  </li>
                ))}
              </ul>
            </div>

            <div className="mt-5 text-[11px] text-zinc-600">
              ※ 表示は読み取り専用。実行ボタン（仕事を走らせる）は次フェーズで追加可能。
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
