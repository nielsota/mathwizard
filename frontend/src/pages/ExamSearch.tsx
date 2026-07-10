import { useState, useRef, useCallback } from 'react'
import ResultCard from '../components/ResultCard'
import type { FetchRequest, FetchResponse } from '../types/api'
import './ExamSearch.css'

type Status = 'idle' | 'loading' | 'done' | 'error'

export default function ExamSearch() {
  const [query, setQuery] = useState('')
  const [maxResults, setMaxResults] = useState(5)
  const [results, setResults] = useState<FetchResponse | null>(null)
  const [status, setStatus] = useState<Status>('idle')
  const [error, setError] = useState('')
  const lastPayload = useRef<FetchRequest | null>(null)

  const doFetch = useCallback(async (payload: FetchRequest) => {
    if (!payload.query.trim()) return

    setStatus('loading')
    setError('')
    lastPayload.current = payload

    try {
      const resp = await fetch('/api/v1/fetch', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })

      const text = await resp.text()
      if (!resp.ok) throw new Error(text || `HTTP ${resp.status}`)

      const data: FetchResponse = JSON.parse(text)
      setResults(data)
      setStatus('done')
    } catch (e) {
      setError(String(e))
      setStatus('error')
    }
  }, [])

  const handleSearch = (mode: 'best' | 'random') => {
    doFetch({ query, max_results: maxResults, mode })
  }

  const handleRedo = () => {
    if (lastPayload.current) doFetch(lastPayload.current)
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSearch('best')
    }
  }

  return (
    <div className="page-enter">
      {/* Decorative geometric accent */}
      <div className="search-hero-accent" aria-hidden="true">
        <svg viewBox="0 0 200 200" fill="none" width="200" height="200">
          <circle cx="100" cy="100" r="80" stroke="var(--blue-light)" strokeWidth="1" opacity="0.5" />
          <circle cx="100" cy="100" r="50" stroke="var(--blue-light)" strokeWidth="1" opacity="0.35" />
          <line x1="20" y1="100" x2="180" y2="100" stroke="var(--peach)" strokeWidth="1" opacity="0.4" />
          <line x1="100" y1="20" x2="100" y2="180" stroke="var(--peach)" strokeWidth="1" opacity="0.4" />
          <path d="M30 170 Q100 40 170 170" stroke="var(--blue)" strokeWidth="1.5" opacity="0.25" fill="none" />
        </svg>
      </div>

      <header className="search-header">
        <h1 className="search-title">Examenopgaven zoeken</h1>
        <p className="search-subtitle">
          Doorzoek de opgavenbank en vind relevante examenopgaven met behulp van AI
        </p>
      </header>

      <div className="search-card">
        <textarea
          className="search-input"
          value={query}
          onChange={e => setQuery(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Beschrijf de opgave die je zoekt..."
          rows={3}
        />

        <div className="search-controls">
          <div className="search-buttons">
            <button
              className="btn btn--primary"
              onClick={() => handleSearch('best')}
              disabled={status === 'loading' || !query.trim()}
            >
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                <circle cx="7" cy="7" r="5" stroke="currentColor" strokeWidth="2"/>
                <path d="M11 11L14 14" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
              </svg>
              Beste match
            </button>
            <button
              className="btn btn--secondary"
              onClick={() => handleSearch('random')}
              disabled={status === 'loading' || !query.trim()}
            >
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                <path d="M2 12L6 2L10 10L14 4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
              Willekeurig
            </button>
            <button
              className="btn btn--ghost"
              onClick={handleRedo}
              disabled={status === 'loading' || !lastPayload.current}
            >
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                <path d="M2 8a6 6 0 1 1 1.5 4" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                <path d="M2 12V8h4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
              Opnieuw
            </button>
          </div>

          <div className="search-max">
            <label className="search-max-label">
              Max
              <input
                type="number"
                min={1}
                max={20}
                value={maxResults}
                onChange={e => setMaxResults(parseInt(e.target.value) || 5)}
                className="search-max-input"
              />
            </label>
          </div>
        </div>

        {status === 'loading' && (
          <div className="search-status">
            <div className="search-spinner" />
            <span>Zoeken...</span>
          </div>
        )}
      </div>

      {status === 'error' && (
        <div className="search-error">{error}</div>
      )}

      {results && status === 'done' && (
        <div className="search-results">
          <ResultCard result={results} />
        </div>
      )}
    </div>
  )
}
