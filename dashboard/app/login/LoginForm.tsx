'use client'
import { useState } from 'react'
import { useRouter } from 'next/navigation'

export default function LoginForm({ from }: { from: string }) {
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const router = useRouter()

  const submit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    const res = await fetch('/api/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ password }),
    })
    setLoading(false)
    if (res.ok) {
      router.push(from)
      router.refresh()
    } else {
      setError('パスワードが違います')
      setPassword('')
    }
  }

  return (
    <form onSubmit={submit} className="space-y-3">
      <input
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        placeholder="パスワード"
        autoFocus
        className="w-full bg-zinc-900 border border-zinc-800 rounded-lg px-3 py-2.5 text-sm text-zinc-100 placeholder-zinc-600 focus:outline-none focus:border-zinc-600"
      />
      {error && <div className="text-sm text-red-400">{error}</div>}
      <button
        type="submit"
        disabled={loading || !password}
        className="w-full bg-emerald-700 disabled:bg-zinc-800 disabled:text-zinc-500 rounded-lg py-2.5 text-sm font-medium"
      >
        {loading ? '...' : 'ログイン'}
      </button>
    </form>
  )
}
