import { getFileContent, listDir } from '@/lib/github'

export const revalidate = 300

const POSTED = '.company/marketing/drafts/gaku_ai_life/posted'

interface PostData {
  name: string
  topic: string
  date: string
  views: number
  likes: number
  replies: number
  hasMetrics: boolean
}

function parsePost(name: string, content: string): PostData {
  const rawTopic = content.match(/^topic:\s*(.*)/m)?.[1] ?? ''
  const topic = rawTopic.replace(/^"|"$/g, '').trim() || name.replace(/\.md$/, '')
  const date = content.match(/^posted_at:\s*(\d{4}-\d{2}-\d{2})/m)?.[1] ?? name.slice(0, 10)
  const hasMetrics = content.includes('THREADS_METRICS')
  const views = parseInt(content.match(/\|\s*views\s*\|\s*(\d+)\s*\|/)?.[1] ?? '0')
  const likes = parseInt(content.match(/\|\s*likes\s*\|\s*(\d+)\s*\|/)?.[1] ?? '0')
  const replies = parseInt(content.match(/\|\s*replies\s*\|\s*(\d+)\s*\|/)?.[1] ?? '0')
  return { name, topic, date, views, likes, replies, hasMetrics }
}

export default async function AnalysisPage() {
  const files = await listDir(POSTED)
  const sorted = [...files].sort().reverse()

  const contents = await Promise.all(
    sorted.map((name) => getFileContent(`${POSTED}/${name}`))
  )

  const posts: PostData[] = sorted
    .map((name, i) =>
      contents[i] ? parsePost(name, contents[i]!) : null
    )
    .filter(Boolean) as PostData[]

  const withMetrics = posts.filter((p) => p.hasMetrics)
  const totalViews = withMetrics.reduce((s, p) => s + p.views, 0)
  const totalLikes = withMetrics.reduce((s, p) => s + p.likes, 0)
  const avgViews = withMetrics.length > 0 ? Math.round(totalViews / withMetrics.length) : 0

  const byViews = [...posts].filter((p) => p.hasMetrics).sort((a, b) => b.views - a.views)

  return (
    <main className="min-h-screen bg-zinc-950 text-zinc-100 pb-10">
      <div className="sticky top-0 z-10 bg-zinc-950/95 backdrop-blur border-b border-zinc-800 px-4 py-3">
        <h1 className="text-sm font-bold text-zinc-100">📈 Threads 分析</h1>
      </div>

      <div className="max-w-lg mx-auto px-4 pt-4 space-y-4">
        {/* summary */}
        <div className="grid grid-cols-3 gap-3">
          <StatCard label="投稿数" value={posts.length} unit="本" />
          <StatCard label="総views" value={totalViews} color="emerald" />
          <StatCard label="平均views" value={avgViews} color="zinc" />
        </div>
        <div className="grid grid-cols-2 gap-3">
          <StatCard label="総いいね" value={totalLikes} />
          <StatCard label="メトリクスあり" value={withMetrics.length} unit="本" />
        </div>

        {/* ranking */}
        {byViews.length > 0 && (
          <div className="bg-zinc-900 rounded-xl border border-zinc-800 p-4">
            <h2 className="text-sm font-semibold text-zinc-200 mb-3">views ランキング</h2>
            <div className="space-y-3">
              {byViews.slice(0, 10).map((post, i) => (
                <div key={post.name} className="flex items-start gap-3">
                  <span
                    className={`text-sm font-bold shrink-0 w-5 text-right ${
                      i === 0
                        ? 'text-yellow-400'
                        : i === 1
                        ? 'text-zinc-300'
                        : i === 2
                        ? 'text-amber-700'
                        : 'text-zinc-600'
                    }`}
                  >
                    {i + 1}
                  </span>
                  <div className="flex-1 min-w-0">
                    <div className="text-sm text-zinc-200 leading-snug line-clamp-2">{post.topic}</div>
                    <div className="text-xs text-zinc-600 mt-0.5 flex gap-2">
                      <span>{post.date}</span>
                      <span className="text-zinc-700">·</span>
                      <span>♡{post.likes}</span>
                      <span>💬{post.replies}</span>
                    </div>
                  </div>
                  <div className="shrink-0 text-right">
                    <div className="text-sm font-semibold text-emerald-400">
                      {post.views.toLocaleString()}
                    </div>
                    <div className="text-xs text-zinc-600">views</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* all posts */}
        <div className="bg-zinc-900 rounded-xl border border-zinc-800 p-4">
          <h2 className="text-sm font-semibold text-zinc-200 mb-3">
            全投稿一覧 <span className="text-zinc-600 font-normal">({posts.length}本)</span>
          </h2>
          <div className="space-y-0">
            {posts.map((post) => (
              <div
                key={post.name}
                className="flex items-center gap-2 py-2 border-b border-zinc-800/50 last:border-0"
              >
                <div className="flex-1 min-w-0">
                  <div className="text-xs text-zinc-300 truncate">{post.topic}</div>
                  <div className="text-xs text-zinc-600">{post.date}</div>
                </div>
                {post.hasMetrics ? (
                  <div className="shrink-0 flex gap-2 text-xs">
                    <span className="text-emerald-400 font-medium">{post.views.toLocaleString()}v</span>
                    <span className="text-zinc-500">♡{post.likes}</span>
                  </div>
                ) : (
                  <span className="text-xs text-zinc-700">計測待ち</span>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>
    </main>
  )
}

function StatCard({
  label,
  value,
  unit,
  color = 'white',
}: {
  label: string
  value: number
  unit?: string
  color?: 'white' | 'emerald' | 'zinc'
}) {
  const colors = { white: 'text-zinc-100', emerald: 'text-emerald-400', zinc: 'text-zinc-400' }
  return (
    <div className="bg-zinc-900 rounded-xl border border-zinc-800 p-3 text-center">
      <div className={`text-2xl font-bold leading-none ${colors[color]}`}>
        {value.toLocaleString()}
        {unit && <span className="text-xs font-normal text-zinc-600 ml-0.5">{unit}</span>}
      </div>
      <div className="text-xs text-zinc-500 mt-1.5">{label}</div>
    </div>
  )
}
