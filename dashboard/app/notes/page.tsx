import { getFileContent, listDir } from '@/lib/github'

export const revalidate = 300

const ARTICLES_DIR = '.company/products/articles'

interface Article {
  name: string
  title: string
  status: string | null
  date: string | null
}

function parseArticle(name: string, content: string): Article {
  const h1 = content.match(/^# (.+)$/m)?.[1]?.trim()
  const title = h1 ?? name.replace(/\.md$/, '').replace(/-/g, ' ')
  const status = content.match(/^status:\s*(.*)/m)?.[1]?.trim() ?? null
  const date =
    content.match(/^date:\s*"?([\d-]+)"?/m)?.[1] ??
    content.match(/^created_at:\s*([\d-]+)/m)?.[1] ??
    null
  return { name, title, status, date }
}

export default async function NotesPage() {
  const files = await listDir(ARTICLES_DIR)
  const articleFiles = files.filter((f) => f !== '_template.md').sort().reverse()

  const contents = await Promise.all(
    articleFiles.map((name) => getFileContent(`${ARTICLES_DIR}/${name}`))
  )

  const articles: Article[] = articleFiles.map((name, i) =>
    contents[i] ? parseArticle(name, contents[i]!) : { name, title: name.replace(/\.md$/, ''), status: null, date: null }
  )

  const published = articles.filter((a) => a.status === 'published' || a.status === 'public')
  const drafts = articles.filter((a) => a.status !== 'published' && a.status !== 'public')

  return (
    <main className="min-h-screen bg-zinc-950 text-zinc-100 pb-10">
      <div className="sticky top-0 z-10 bg-zinc-950/95 backdrop-blur border-b border-zinc-800 px-4 py-3">
        <h1 className="text-sm font-bold text-zinc-100">📄 Note 記事一覧</h1>
      </div>

      <div className="max-w-lg mx-auto px-4 pt-4 space-y-4">
        {/* summary */}
        <div className="grid grid-cols-3 gap-3">
          <div className="bg-zinc-900 rounded-xl border border-zinc-800 p-3 text-center">
            <div className="text-2xl font-bold text-zinc-100">{articles.length}</div>
            <div className="text-xs text-zinc-500 mt-1">合計</div>
          </div>
          <div className="bg-zinc-900 rounded-xl border border-zinc-800 p-3 text-center">
            <div className="text-2xl font-bold text-emerald-400">{published.length}</div>
            <div className="text-xs text-zinc-500 mt-1">公開済み</div>
          </div>
          <div className="bg-zinc-900 rounded-xl border border-zinc-800 p-3 text-center">
            <div className="text-2xl font-bold text-amber-400">{drafts.length}</div>
            <div className="text-xs text-zinc-500 mt-1">下書き</div>
          </div>
        </div>

        {/* article list */}
        <div className="bg-zinc-900 rounded-xl border border-zinc-800 p-4">
          <div className="space-y-0">
            {articles.map((article) => (
              <div
                key={article.name}
                className="flex items-start gap-3 py-3 border-b border-zinc-800/50 last:border-0"
              >
                <div className="flex-1 min-w-0">
                  <div className="text-sm text-zinc-200 leading-snug">{article.title}</div>
                  {article.date && (
                    <div className="text-xs text-zinc-600 mt-0.5">{article.date}</div>
                  )}
                </div>
                <StatusBadge status={article.status} />
              </div>
            ))}
            {articles.length === 0 && (
              <p className="text-sm text-zinc-600 py-2">記事がありません</p>
            )}
          </div>
        </div>
      </div>
    </main>
  )
}

function StatusBadge({ status }: { status: string | null }) {
  if (!status) return null
  const styles: Record<string, string> = {
    published: 'bg-emerald-950 text-emerald-400',
    public: 'bg-emerald-950 text-emerald-400',
    draft: 'bg-zinc-800 text-zinc-500',
    writing: 'bg-amber-950 text-amber-400',
    review: 'bg-blue-950 text-blue-400',
  }
  const style = styles[status] ?? 'bg-zinc-800 text-zinc-500'
  return (
    <span className={`shrink-0 text-xs px-2 py-0.5 rounded-full font-medium ${style}`}>
      {status}
    </span>
  )
}
