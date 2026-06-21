'use client'
import { useEffect } from 'react'

export default function AutoRefresh({ seconds = 60 }: { seconds?: number }) {
  useEffect(() => {
    const t = setInterval(() => location.reload(), seconds * 1000)
    return () => clearInterval(t)
  }, [seconds])
  return null
}
