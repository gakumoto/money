import Link from 'next/link'
import { getFileContent, listDir } from '@/lib/github'

export const revalidate = 300

const ARTICLES_DIR = '.company/products/articles'
const PAGE_SIZE = 30

type Filter = 'all' | 'published' | 'draft'

interface Article {
  name: string
  title: string
  subtitle: string | null
  status: string | null
  date: string | null
  price: string | null
  wordCount: number
  excerpt: string
}

function unquote(v: string): string {
  return v.trim().replace(/^["']|["']$/g, '')
}

function getField(yaml: string, key: string): string | null {
  const re = new RegExp(`^${key}:\\s*(.+)$`, 'm')
  const m = yaml.match(re)
  return m ? unquote(m[1]) : null
}

function parseArticle(name: string, content: string): Article {
  const fm = content.match(/^---\n([\s\S]*?)\n---\n?([\s\S]*)$/)
  const yaml = fm?.[1] ?? ''
  const body = (fm?.[2] ?? content).trim()

  // タイトル: YAML title フィールド優先、なければ最初の H1、なければファイル名
  const h1 = body.match(/^# (.+)$/m)?.[1]?.trim()
  const title = getField(yaml, 'title') ?? h1 ?? name.replace(/\.md$/, '').replace(/[-_]/g, ' ')

  const subtitle = getField(yaml, 'subtitle')
  const status = getField(yaml, 'status')
  const date =
    getField(yaml, 'date') ??
    getField(yaml, 'created') ??
    getField(yaml, 'created_at') ??
    name.match(/^(\d{4}-\d{2}-\d{2})/)?.[1] ??
    null
  const price = getField(yaml, 'price')

  // 本文プレビュー (最初の段落・H1 除去)
  const cleanBody = body
    .replace(/^# .+$/m, '')
    .replace(/!\[.*?\]\(.*?\)/g, '')
    .trim()
  const excerpt = cleanBody.slice(0, 140).replace(/\n+/g, ' ')

  return {
    name,
    title,
    subtitle,
    status,
    date,
    price,
    wordCount: cleanBody.length,
    excerpt,
  }
}

interface PageProps {
  searchParams: { filter?: string }
}

export default async function NotesPage({ searchParams }: PageProps) {
  const filter = (searchParams.filter ?? 'all') as Filter

  const files = await listDir(ARTICLES_DIR)
  const articleFiles = files
    .filter((f) => f !== '_template.md')
    .sort()
    .reverse()

  const contents = await Promise.all(
    articleFiles.map((name) => getFileContent(`${ARTICLES_DIR}/${name}`)),
  )

  const allArticles: Article[] = articleFiles.map((name, i) =>
    contents[i]
      ? parseArticle(name, contents[i]!)
      : {
          name,
          title: name.replace(/\.md$/, ''),
          subtitle: null,
          status: null,
          date: null,
          price: null,
          wordCount: 0,
          excerpt: '',
        },
  )

  const published = allArticles.filter((a) => a.status === 'published' || a.status === 'public')
  const drafts = allArticles.filter((a) => a.status !== 'published' && a.status !== 'public')

  const filtered =
    filter === 'published' ? published : filter === 'draft' ? drafts : allArticles
  const visible = filtered.slice(0, PAGE_SIZE)

  return (
    <main className="min-h-screen bg-zinc-950 text-zinc-100 pb-20">
      <div className="sticky top-0 z-10 bg-zinc-950/95 backdrop-blur border-b border-zinc-800 px-4 py-3">
        <div className="flex items-center justify-between mb-3">
          <h1 className="text-sm font-bold text-zinc-100">📄 Note 記事</h1>
          <span className="text-xs text-zinc-500">
            {visible.length}/{filtered.length}本
          </span>
        </div>

        {/* tabs */}
        <div className="flex gap-1">
          <FilterTab href="/notes?filter=all" label="全部" count={allArticles.length} active={filter === 'all'} />
          <FilterTab
            href="/notes?filter=published"
            label="公開済み"
            count={published.length}
            active={filter === 'published'}
            color="emerald"
          />
          <FilterTab
            href="/notes?filter=draft"
            label="下書き"
            count={drafts.length}
            active={filter === 'draft'}
            color="amber"
          />
        </div>
      </div>

      <div className="max-w-lg mx-auto px-4 pt-4 space-y-3">
        {visible.length === 0 && (
          <div className="bg-zinc-900 rounded-xl border border-zinc-800 p-6 text-center text-sm text-zinc-500">
            記事がありません
          </div>
        )}

        {visible.map((article) => (
          <ArticleCard key={article.name} article={article} />
        ))}

        {filtered.length > PAGE_SIZE && (
          <div className="text-center text-xs text-zinc-600 py-4">
            最新 {PAGE_SIZE} 件を表示中（全 {filtered.length} 件）
          </div>
        )}
      </div>
    </main>
  )
}

function ArticleCard({ article }: { article: Article }) {
  return (
    <article className="bg-zinc-900 rounded-xl border border-zinc-800 p-4">
      <div className="flex items-start justify-between gap-2 mb-2">
        <h2 className="text-sm font-semibold text-zinc-100 leading-snug">{article.title}</h2>
        <StatusBadge status={article.status} />
      </div>

      {article.subtitle && (
        <p className="text-xs text-zinc-400 mb-2 leading-snug">{article.subtitle}</p>
      )}

      <div className="flex flex-wrap gap-1.5 mb-3 text-[11px] text-zinc-500">
        {article.date && <span>📅 {article.date}</span>}
        {article.price && (
          <span className={article.price === '有料' ? 'text-amber-400' : 'text-zinc-500'}>
            {article.price === '有料' ? '💰 有料' : '🆓 無料'}
          </span>
        )}
        {article.wordCount > 0 && <span>📝 {article.wordCount.toLocaleString()}字</span>}
      </div>

      {article.excerpt && (
        <p className="text-xs text-zinc-400 leading-relaxed bg-zinc-950/50 rounded-lg p-3 border border-zinc-800/50">
          {article.excerpt}
          {article.wordCount > 140 && '…'}
        </p>
      )}
    </article>
  )
}

function FilterTab({
  href,
  label,
  count,
  active,
  color,
}: {
  href: string
  label: string
  count: number
  active: boolean
  color?: 'emerald' | 'amber'
}) {
  const activeColor =
    color === 'emerald'
      ? 'bg-emerald-500 text-zinc-950'
      : color === 'amber'
        ? 'bg-amber-500 text-zinc-950'
        : 'bg-zinc-100 text-zinc-950'
  return (
    <Link
      href={href}
      className={`text-xs px-3 py-1.5 rounded-full font-medium transition-colors ${
        active ? activeColor : 'bg-zinc-900 text-zinc-400 border border-zinc-800'
      }`}
    >
      {label} <span className="opacity-60">{count}</span>
    </Link>
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
    <span
      className={`shrink-0 text-[10px] px-2 py-0.5 rounded-full font-medium ${style}`}
    >
      {status}
    </span>
  )
}
