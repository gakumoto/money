'use server'

import { revalidatePath } from 'next/cache'
import { isAuthed } from '@/lib/auth'
import {
  deleteFile,
  getFileWithSha,
  listDir,
  putFile,
} from '@/lib/github'
import {
  bodyText,
  nextSlot,
  parseFrontmatter,
  setFrontmatterField,
} from '@/lib/draft'

const ACCOUNT = 'gaku_ai_life'
const DRAFTS_ROOT = `.company/marketing/drafts/${ACCOUNT}`

export interface ActionResult {
  ok: boolean
  message?: string
  publishAt?: string
}

async function moveFile(
  fromPath: string,
  toPath: string,
  newContent: string,
  commitMsg: string,
): Promise<{ ok: boolean; error?: string }> {
  const original = await getFileWithSha(fromPath)
  if (!original) return { ok: false, error: '元ファイルが見つかりません' }

  const put = await putFile(toPath, newContent, `${commitMsg}\n\n[dashboard]`)
  if (!put.ok) return { ok: false, error: `新ファイル作成失敗: ${put.status} ${put.error ?? ''}` }

  const del = await deleteFile(fromPath, original.sha, `${commitMsg} (delete original)\n\n[dashboard]`)
  if (!del.ok) {
    return { ok: false, error: `元ファイル削除失敗: ${del.status} ${del.error ?? ''}` }
  }
  return { ok: true }
}

export async function approveDraft(filename: string): Promise<ActionResult> {
  if (!isAuthed()) return { ok: false, message: '認証エラー' }
  if (!filename.endsWith('.md') || filename.includes('/')) {
    return { ok: false, message: '不正なファイル名' }
  }

  const fromPath = `${DRAFTS_ROOT}/${filename}`
  const original = await getFileWithSha(fromPath)
  if (!original) return { ok: false, message: '元ファイルが見つかりません' }

  // Pick next slot from currently queued publish_at values
  const queuedNames = await listDir(`${DRAFTS_ROOT}/queued`)
  const queuedFms = await Promise.all(
    queuedNames.map(async (n) => {
      const f = await getFileWithSha(`${DRAFTS_ROOT}/queued/${n}`)
      return f ? parseFrontmatter(f.content).fm : null
    }),
  )
  const usedPublishAts = queuedFms
    .map((fm) => fm?.publish_at ?? fm?.target_publish)
    .filter((v): v is string => Boolean(v))

  const slot = nextSlot(usedPublishAts)

  let updated = setFrontmatterField(original.content, 'status', 'queued')
  updated = setFrontmatterField(updated, 'publish_at', slot)

  const result = await moveFile(
    fromPath,
    `${DRAFTS_ROOT}/queued/${filename}`,
    updated,
    `approve via dashboard: ${filename}`,
  )
  if (!result.ok) return { ok: false, message: result.error }

  revalidatePath('/review')
  revalidatePath('/queue')
  revalidatePath('/')
  return { ok: true, publishAt: slot }
}

export async function rejectDraft(
  filename: string,
  reason: string,
): Promise<ActionResult> {
  if (!isAuthed()) return { ok: false, message: '認証エラー' }
  if (!filename.endsWith('.md') || filename.includes('/')) {
    return { ok: false, message: '不正なファイル名' }
  }
  if (!reason.trim()) return { ok: false, message: '理由が必要です' }

  const fromPath = `${DRAFTS_ROOT}/${filename}`
  const original = await getFileWithSha(fromPath)
  if (!original) return { ok: false, message: '元ファイルが見つかりません' }

  const cleanReason = reason.replace(/\n/g, ' ').replace(/"/g, "'").slice(0, 200)
  const now = new Date().toISOString().slice(0, 19)

  let updated = setFrontmatterField(original.content, 'status', 'rejected')
  updated = setFrontmatterField(updated, 'rejected_at', now)
  updated = setFrontmatterField(updated, 'rejected_reason', `"${cleanReason}"`)

  const result = await moveFile(
    fromPath,
    `${DRAFTS_ROOT}/rejected/${filename}`,
    updated,
    `reject via dashboard: ${filename}`,
  )
  if (!result.ok) return { ok: false, message: result.error }

  revalidatePath('/review')
  revalidatePath('/')
  return { ok: true }
}

export async function listUnreviewed(): Promise<
  Array<{
    filename: string
    topic: string | null
    templateType: string | null
    purpose: string | null
    hookPattern: string | null
    body: string
  }>
> {
  const names = await listDir(DRAFTS_ROOT)
  const items = await Promise.all(
    names.map(async (name) => {
      const f = await getFileWithSha(`${DRAFTS_ROOT}/${name}`)
      if (!f) return null
      const { fm } = parseFrontmatter(f.content)
      // Top-level files with status=draft or no status; skip if already queued/etc.
      if (fm.status && fm.status !== 'draft' && fm.status !== 'writing') return null
      return {
        filename: name,
        topic: fm.topic ?? null,
        templateType: fm.template_type ?? null,
        purpose: fm.purpose ?? null,
        hookPattern: fm.hook_pattern ?? fm.hook_type ?? null,
        body: bodyText(f.content),
      }
    }),
  )
  return items.filter((x): x is NonNullable<typeof x> => x !== null)
}
