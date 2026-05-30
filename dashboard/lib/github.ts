const API = 'https://api.github.com'

function headers(): Record<string, string> {
  return {
    Authorization: `Bearer ${process.env.GITHUB_TOKEN ?? ''}`,
    Accept: 'application/vnd.github.v3+json',
    'X-GitHub-Api-Version': '2022-11-28',
  }
}

function repo(): string {
  return process.env.GITHUB_REPO ?? ''
}

export async function getFileContent(path: string): Promise<string | null> {
  try {
    const res = await fetch(`${API}/repos/${repo()}/contents/${path}`, {
      headers: headers(),
      next: { revalidate: 60 },
    })
    if (!res.ok) return null
    const json = await res.json()
    if (json.type !== 'file' || !json.content) return null
    return Buffer.from(json.content.replace(/\n/g, ''), 'base64').toString('utf-8')
  } catch {
    return null
  }
}

export async function listDir(path: string): Promise<string[]> {
  try {
    const res = await fetch(`${API}/repos/${repo()}/contents/${path}`, {
      headers: headers(),
      next: { revalidate: 60 },
    })
    if (!res.ok) return []
    const json = await res.json()
    if (!Array.isArray(json)) return []
    return (json as Array<{ name: string; type: string }>)
      .filter((f) => f.type === 'file' && f.name.endsWith('.md'))
      .map((f) => f.name)
  } catch {
    return []
  }
}
