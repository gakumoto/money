const SLOTS = ['07:30', '12:30', '18:00', '21:30', '23:00']

export interface DraftFM {
  [key: string]: string | undefined
  status?: string
  topic?: string
  template_type?: string
  purpose?: string
  hook_pattern?: string
  hook_type?: string
  publish_at?: string
  target_publish?: string
  account?: string
  created_at?: string
}

function unquote(v: string): string {
  return v.trim().replace(/^["']|["']$/g, '')
}

export function parseFrontmatter(content: string): { fm: DraftFM; body: string; rawYaml: string } {
  const m = content.match(/^---\n([\s\S]*?)\n---\n?([\s\S]*)$/)
  if (!m) return { fm: {}, body: content, rawYaml: '' }
  const fm: DraftFM = {}
  for (const line of m[1].split('\n')) {
    const kv = line.match(/^([a-z_]+):\s*(.*)$/)
    if (kv) fm[kv[1]] = unquote(kv[2])
  }
  return { fm, body: m[2], rawYaml: m[1] }
}

export function bodyText(content: string): string {
  const { body } = parseFrontmatter(content)
  return body.replace(/^【本文】\s*\n?/, '').trim()
}

export function setFrontmatterField(content: string, key: string, value: string): string {
  const m = content.match(/^(---\n)([\s\S]*?)(\n---\n?)/)
  if (!m) return content
  const yaml = m[2]
  const keyRe = new RegExp(`^${key}:.*$`, 'm')
  const newYaml = keyRe.test(yaml)
    ? yaml.replace(keyRe, `${key}: ${value}`)
    : yaml + `\n${key}: ${value}`
  return m[1] + newYaml + m[3] + content.slice(m[0].length)
}

function jstParts(ms: number): { y: number; mo: number; d: number; h: number; mi: number } {
  const jst = new Date(ms + 9 * 3600 * 1000)
  return {
    y: jst.getUTCFullYear(),
    mo: jst.getUTCMonth() + 1,
    d: jst.getUTCDate(),
    h: jst.getUTCHours(),
    mi: jst.getUTCMinutes(),
  }
}

function pad(n: number): string {
  return String(n).padStart(2, '0')
}

function isoJst(ms: number): string {
  const p = jstParts(ms)
  return `${p.y}-${pad(p.mo)}-${pad(p.d)}T${pad(p.h)}:${pad(p.mi)}:00+09:00`
}

function slotKey(ms: number): string {
  const p = jstParts(ms)
  return `${p.y}-${pad(p.mo)}-${pad(p.d)} ${pad(p.h)}:${pad(p.mi)}`
}

export function nextSlot(usedPublishAts: string[]): string {
  const used = new Set<string>()
  for (const pub of usedPublishAts) {
    const t = Date.parse(pub)
    if (!isNaN(t)) used.add(slotKey(t))
  }
  const now = Date.now()
  for (let dayOffset = 0; dayOffset <= 2; dayOffset++) {
    const base = jstParts(now + dayOffset * 24 * 3600 * 1000)
    for (const slot of SLOTS) {
      const [hh, mm] = slot.split(':').map(Number)
      // Build JST datetime then convert to UTC ms by subtracting 9h
      const slotJstMs = Date.UTC(base.y, base.mo - 1, base.d, hh, mm, 0)
      const slotUtcMs = slotJstMs - 9 * 3600 * 1000
      if (slotUtcMs <= now) continue
      if (used.has(slotKey(slotUtcMs))) continue
      return isoJst(slotUtcMs)
    }
  }
  return isoJst(now + 3600 * 1000)
}
