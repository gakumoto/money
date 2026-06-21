// /studio の「実行ボタン」用 API。許可済みの python スクリプトだけを実行する（ローカル運用前提）。
import { NextResponse } from 'next/server'
import { spawn } from 'child_process'
import path from 'path'
import fs from 'fs'

export const dynamic = 'force-dynamic'

const ROOT = path.join(process.cwd(), '..') // dashboard/ の一つ上 = リポジトリルート

function pyExe(): string {
  const v = path.join(ROOT, '.venv', 'Scripts', 'python.exe')
  return fs.existsSync(v) ? v : 'python'
}

// action → 実行スクリプト列（allowlist）。任意コマンド実行はさせない。
const SCRIPTS: Record<string, string[]> = {
  refresh: ['build_studio_data.py'],
  ceo: ['ceo_briefing.py', 'build_studio_data.py'],
  research: ['build_research_index.py', 'build_studio_data.py'],
  outbound: ['build_outbound_targets.py', 'build_studio_data.py'],
}

function run(script: string): Promise<{ code: number; out: string }> {
  return new Promise((resolve) => {
    const p = spawn(pyExe(), [path.join(ROOT, 'scripts', script)], { cwd: ROOT })
    let out = ''
    p.stdout.on('data', (d) => (out += d.toString()))
    p.stderr.on('data', (d) => (out += d.toString()))
    p.on('close', (code) => resolve({ code: code ?? -1, out: out.slice(-800) }))
    p.on('error', (e) => resolve({ code: -1, out: String(e) }))
  })
}

export async function POST(req: Request) {
  const body = await req.json().catch(() => ({ action: '' }))
  const seq = SCRIPTS[body?.action as string]
  if (!seq) {
    return NextResponse.json({ ok: false, error: 'unknown action' }, { status: 400 })
  }
  const results: { script: string; code: number; out: string }[] = []
  for (const s of seq) {
    const r = await run(s)
    results.push({ script: s, ...r })
    if (r.code !== 0) break
  }
  const ok = results.every((r) => r.code === 0)
  return NextResponse.json({ ok, results })
}
