import { NextResponse } from 'next/server'
import { cookies } from 'next/headers'
import { AUTH_COOKIE, checkPassword } from '@/lib/auth'

export const dynamic = 'force-dynamic'

export async function POST(req: Request) {
  const body = await req.json().catch(() => ({}))
  const password = typeof body?.password === 'string' ? body.password : ''
  if (!checkPassword(password)) {
    return new NextResponse('Unauthorized', { status: 401 })
  }
  cookies().set(AUTH_COOKIE, password, {
    httpOnly: true,
    secure: true,
    sameSite: 'lax',
    path: '/',
    maxAge: 60 * 60 * 24 * 30,
  })
  return NextResponse.json({ ok: true })
}
