import DraftCard from './DraftCard'
import { listUnreviewed } from './actions'

export const dynamic = 'force-dynamic'

export default async function Review() {
  const items = await listUnreviewed()

  return (
    <main className="min-h-screen bg-zinc-950 text-zinc-100 pb-10">
      <div className="sticky top-0 z-10 bg-zinc-950/95 backdrop-blur border-b border-zinc-800 px-4 py-3 flex items-center justify-between">
        <span className="font-bold text-sm tracking-wide text-zinc-100">📝 レビュー</span>
        <span className="text-xs text-zinc-500">{items.length}本 未レビュー</span>
      </div>

      <div className="max-w-lg mx-auto px-4 pt-4 space-y-3">
        {items.length === 0 ? (
          <div className="bg-zinc-900 rounded-xl border border-zinc-800 p-6 text-center text-sm text-zinc-500">
            未レビューの下書きはありません
          </div>
        ) : (
          items.map((d) => <DraftCard key={d.filename} {...d} />)
        )}
      </div>
    </main>
  )
}
