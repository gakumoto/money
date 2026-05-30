import { NextResponse } from 'next/server'
import { getRawContent } from '@/lib/github'

export const dynamic = 'force-dynamic'

export async function GET() {
  const html = await getRawContent('.company/reports/gaku_ai_life_report.html')

  if (!html) {
    return new NextResponse(
      `<!DOCTYPE html>
<html lang="ja">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>レポート未生成</title>
<style>body{background:#0f172a;color:#94a3b8;font-family:sans-serif;display:flex;align-items:center;justify-content:center;min-height:100vh;text-align:center;padding:40px;}</style>
</head>
<body>
  <div>
    <div style="font-size:48px;margin-bottom:16px;">📊</div>
    <h2 style="color:#e2e8f0;margin-bottom:12px;">レポートがまだ生成されていません</h2>
    <p style="font-size:14px;line-height:1.7;">
      ローカルで以下を実行してください:<br>
      <code style="background:#1e293b;padding:8px 16px;border-radius:6px;display:inline-block;margin-top:8px;color:#4ade80;">
        python scripts/fetch_all_metrics.py gaku_ai_life
      </code>
    </p>
    <p style="font-size:12px;margin-top:16px;color:#64748b;">
      実行後、自動的にGitHubへpushされ、このページで見られるようになります。
    </p>
  </div>
</body>
</html>`,
      { status: 404, headers: { 'Content-Type': 'text/html; charset=utf-8' } }
    )
  }

  return new NextResponse(html, {
    headers: {
      'Content-Type': 'text/html; charset=utf-8',
      'Cache-Control': 'no-cache, must-revalidate',
    },
  })
}
