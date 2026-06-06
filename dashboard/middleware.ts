import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'
import { AUTH_COOKIE } from '@/lib/auth'

export function middleware(req: NextRequest) {
  const expected = process.env.DASHBOARD_PASSWORD
  if (!expected) {
    return NextResponse.next()
  }
  const got = req.cookies.get(AUTH_COOKIE)?.value
  if (got && got.length === expected.length) {
    let diff = 0
    for (let i = 0; i < got.length; i++) {
      diff |= got.charCodeAt(i) ^ expected.charCodeAt(i)
    }
    if (diff === 0) return NextResponse.next()
  }
  const url = new URL('/login', req.url)
  url.searchParams.set('from', req.nextUrl.pathname)
  return NextResponse.redirect(url)
}

export const config = {
  matcher: ['/review/:path*'],
}
