import { cookies } from 'next/headers'

export const AUTH_COOKIE = 'auth'

export function isAuthed(): boolean {
  const expected = process.env.DASHBOARD_PASSWORD
  if (!expected) return false
  const got = cookies().get(AUTH_COOKIE)?.value
  if (!got) return false
  return constantTimeEqual(got, expected)
}

export function checkPassword(password: string): boolean {
  const expected = process.env.DASHBOARD_PASSWORD
  if (!expected) return false
  return constantTimeEqual(password, expected)
}

function constantTimeEqual(a: string, b: string): boolean {
  if (a.length !== b.length) return false
  let diff = 0
  for (let i = 0; i < a.length; i++) {
    diff |= a.charCodeAt(i) ^ b.charCodeAt(i)
  }
  return diff === 0
}
