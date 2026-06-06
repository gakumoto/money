'use client'
import { useState, useTransition } from 'react'
import { approveDraft, rejectDraft } from './actions'

interface Props {
  filename: string
  topic: string | null
  templateType: string | null
  purpose: string | null
  hookPattern: string | null
  body: string
}

function formatPublishAt(iso: string): string {
  const m = iso.match(/^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2})/)
  if (!m) return iso
  return `${m[2]}/${m[3]} ${m[4]}:${m[5]}`
}

export default function DraftCard(props: Props) {
  const [pending, start] = useTransition()
  const [rejecting, setRejecting] = useState(false)
  const [reason, setReason] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)

  const handleApprove = () => {
    setError(null)
    start(async () => {
      const result = await approveDraft(props.filename)
      if (!result.ok) {
        setError(result.message ?? '承認失敗')
      } else if (result.publishAt) {
        setSuccess(`承認 → ${formatPublishAt(result.publishAt)} に予約`)
      }
    })
  }

  const handleReject = () => {
    if (!reason.trim()) {
      setError('理由を入力してください')
      return
    }
    setError(null)
    start(async () => {
      const result = await rejectDraft(props.filename, reason)
      if (!result.ok) {
        setError(result.message ?? '却下失敗')
      } else {
        setSuccess('却下しました')
      }
    })
  }

  if (success) {
    return (
      <article className="bg-zinc-900 rounded-xl border border-emerald-900/60 p-4 text-sm text-emerald-400">
        ✓ {success}
      </article>
    )
  }

  return (
    <article className="bg-zinc-900 rounded-xl border border-zinc-800 p-4">
      <div className="flex items-center justify-between mb-2">
        <span className="text-[10px] text-zinc-600 truncate font-mono">{props.filename}</span>
      </div>

      {props.topic && (
        <h2 className="text-sm font-semibold text-zinc-100 leading-snug mb-2">
          {props.topic}
        </h2>
      )}

      <div className="flex flex-wrap gap-1.5 mb-3">
        {props.purpose && <Tag>{props.purpose}</Tag>}
        {props.templateType && <Tag>{props.templateType}</Tag>}
        {props.hookPattern && <Tag>フック: {props.hookPattern}</Tag>}
      </div>

      <pre className="text-sm text-zinc-200 whitespace-pre-wrap leading-relaxed font-sans bg-zinc-950/50 rounded-lg p-3 border border-zinc-800/50 mb-3">
        {props.body}
      </pre>

      {error && (
        <div className="text-xs text-red-400 bg-red-950/40 border border-red-900/50 rounded px-2 py-1.5 mb-2">
          {error}
        </div>
      )}

      {rejecting ? (
        <div className="space-y-2">
          <textarea
            value={reason}
            onChange={(e) => setReason(e.target.value)}
            placeholder="却下理由 (例: 危険ワードあり / 冒頭弱い)"
            rows={2}
            className="w-full bg-zinc-950 border border-zinc-800 rounded px-2 py-1.5 text-xs text-zinc-100 placeholder-zinc-600 focus:outline-none focus:border-zinc-600"
          />
          <div className="flex gap-2">
            <button
              type="button"
              onClick={() => {
                setRejecting(false)
                setReason('')
                setError(null)
              }}
              disabled={pending}
              className="flex-1 bg-zinc-800 text-zinc-300 rounded-lg py-2 text-sm font-medium"
            >
              戻る
            </button>
            <button
              type="button"
              onClick={handleReject}
              disabled={pending || !reason.trim()}
              className="flex-1 bg-red-700 disabled:bg-zinc-800 disabled:text-zinc-500 text-white rounded-lg py-2 text-sm font-medium"
            >
              {pending ? '...' : '❌ 却下確定'}
            </button>
          </div>
        </div>
      ) : (
        <div className="flex gap-2">
          <button
            type="button"
            onClick={handleApprove}
            disabled={pending}
            className="flex-1 bg-emerald-700 disabled:bg-zinc-800 disabled:text-zinc-500 text-white rounded-lg py-2 text-sm font-medium"
          >
            {pending ? '...' : '✅ 承認'}
          </button>
          <button
            type="button"
            onClick={() => setRejecting(true)}
            disabled={pending}
            className="flex-1 bg-zinc-800 disabled:opacity-50 text-zinc-300 rounded-lg py-2 text-sm font-medium"
          >
            ❌ 却下
          </button>
        </div>
      )}
    </article>
  )
}

function Tag({ children }: { children: React.ReactNode }) {
  return (
    <span className="text-[11px] px-2 py-0.5 rounded bg-zinc-800 text-zinc-400">
      {children}
    </span>
  )
}
