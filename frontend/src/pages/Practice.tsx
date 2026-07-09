import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import ExerciseCard from '../components/ExerciseCard'
import type { PracticeSet } from '../types/api'
import './Practice.css'

const TOPIC_META: Record<string, { title: string; subtitle: string; icon: string }> = {
  unitcircle: {
    title: 'Eenheidscirkel',
    subtitle: 'Oefen met de eenheidscirkel, sinus, cosinus en tangens',
    icon: '⊙',
  },
  derivatives: {
    title: 'Afgeleiden',
    subtitle: 'Opgaven over differentiëren en afgeleide functies',
    icon: "f'",
  },
  rootfinding: {
    title: 'Wortels vinden',
    subtitle: 'Snijpunten, nulpunten en vergelijkingen oplossen',
    icon: '√',
  },
  parametric: {
    title: 'Parametrische vergelijkingen',
    subtitle: 'Opgaven over parametrische krommen en vergelijkingen',
    icon: 't→',
  },
  goniometrie: {
    title: 'Goniometrie',
    subtitle: 'Goniometrische functies, identiteiten en vergelijkingen',
    icon: 'θ',
  },
}

export default function Practice() {
  const { topic } = useParams<{ topic: string }>()
  const [practiceSet, setPracticeSet] = useState<PracticeSet | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const meta = topic ? TOPIC_META[topic] : null

  useEffect(() => {
    if (!topic) return

    setLoading(true)
    setError('')

    fetch(`/api/v1/practice/${topic}`)
      .then(async resp => {
        if (!resp.ok) throw new Error(`HTTP ${resp.status}`)
        return resp.json()
      })
      .then((data: PracticeSet) => {
        setPracticeSet(data)
        setLoading(false)
      })
      .catch(e => {
        setError(String(e))
        setLoading(false)
      })
  }, [topic])

  return (
    <div className="page-enter">
      <header className="practice-header">
        {meta && <span className="practice-icon">{meta.icon}</span>}
        <div>
          <h1 className="practice-title">{meta?.title ?? topic}</h1>
          <p className="practice-subtitle">{meta?.subtitle ?? ''}</p>
        </div>
      </header>

      {loading && (
        <div className="practice-loading">
          <div className="search-spinner" />
          <span>Opgaven laden...</span>
        </div>
      )}

      {error && (
        <div className="search-error">{error}</div>
      )}

      {practiceSet && !loading && (
        <div className="practice-list">
          {practiceSet.exercises.length > 0 ? (
            practiceSet.exercises.map(ex => (
              <ExerciseCard key={ex.number} exercise={ex} />
            ))
          ) : (
            <div className="practice-empty">
              <p>Geen oefenopgaven beschikbaar voor dit onderwerp.</p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
