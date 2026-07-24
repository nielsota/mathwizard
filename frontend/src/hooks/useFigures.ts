import { useEffect, useState } from 'react'
import type { FigureListResponse, FigureResponse } from '../types/api'

interface UseFiguresResult {
  figures: FigureResponse[]
  loading: boolean
  error: string
}

export function useFigures(onUnauthorized: () => void): UseFiguresResult {
  const [figures, setFigures] = useState<FigureResponse[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    let active = true

    async function load(): Promise<void> {
      try {
        const listResp = await fetch('/api/v1/figures', { credentials: 'include' })
        if (listResp.status === 401) {
          onUnauthorized()
          return
        }
        if (!listResp.ok) throw new Error(`HTTP ${listResp.status}`)
        const list: FigureListResponse = await listResp.json()

        const details = await Promise.all(
          list.figures.map(async (summary) => {
            const resp = await fetch(`/api/v1/figures/${summary.id}`, {
              credentials: 'include',
            })
            if (!resp.ok) throw new Error(`HTTP ${resp.status}`)
            return (await resp.json()) as FigureResponse
          }),
        )
        if (!active) return
        setFigures(details)
        setLoading(false)
      } catch (e) {
        if (!active) return
        setError(String(e))
        setLoading(false)
      }
    }

    void load()
    return () => {
      active = false
    }
  }, [onUnauthorized])

  return { figures, loading, error }
}
