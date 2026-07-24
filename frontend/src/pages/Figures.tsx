import { useEffect, useState } from 'react'
import FigureView from '../components/FigureView'
import { Card } from '../components/ui'
import type { FigureListResponse, FigureResponse } from '../types/api'
import './Figures.css'

interface FiguresProps {
  onUnauthorized: () => void
}

export default function Figures({ onUnauthorized }: FiguresProps) {
  const [figures, setFigures] = useState<FigureResponse[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    let active = true

    async function load() {
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

    load()
    return () => {
      active = false
    }
  }, [onUnauthorized])

  return (
    <div className="page-enter figures-page">
      <header className="figures-header">
        <h1 className="figures-title">Figuren</h1>
        <p className="figures-subtitle">Testgalerij voor in-house figuren</p>
      </header>

      {loading && <div className="figures-loading">Figuren laden...</div>}
      {error && <div className="search-error">{error}</div>}

      {!loading && !error && (
        <div className="figures-grid">
          {figures.map((figure) => (
            <Card key={figure.id} className="figures-card">
              <h2 className="figures-card-title">{figure.title}</h2>
              <FigureView spec={figure.spec} />
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
