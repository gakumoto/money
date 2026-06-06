import LoginForm from './LoginForm'

export default function Login({ searchParams }: { searchParams: { from?: string } }) {
  return (
    <main className="min-h-screen bg-zinc-950 text-zinc-100 flex items-center justify-center px-4">
      <div className="w-full max-w-sm space-y-6">
        <div className="text-center">
          <div className="text-3xl mb-2">🔒</div>
          <h1 className="text-lg font-semibold">レビュー用ログイン</h1>
        </div>
        <LoginForm from={searchParams.from ?? '/review'} />
      </div>
    </main>
  )
}
