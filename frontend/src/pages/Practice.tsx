import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import ExerciseCard from '../components/ExerciseCard'
import type { QuestionListResponse } from '../types/api'
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
  const [practiceSet, setPracticeSet] = useState<QuestionListResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const meta = topic ? TOPIC_META[topic] : null
  const questions = practiceSet?.questions ?? []
  const totalMarks = questions.reduce((sum, ex) => sum + ex.max_marks, 0)
  const tagCount = new Set(questions.flatMap(ex => ex.tags)).size

  useEffect(() => {
    if (!topic) return

    const controller = new AbortController()
    let active = true

    setLoading(true)
    setError('')
    setPracticeSet(null)

    fetch(`/api/v1/practice/${topic}`, {
      signal: controller.signal,
      credentials: 'include',
    })
      .then(async resp => {
        if (!resp.ok) throw new Error(`HTTP ${resp.status}`)
        return resp.json()
      })
      .then((data: QuestionListResponse) => {
        if (!active) return
        setPracticeSet(data)
        setLoading(false)
      })
      .catch(e => {
        if (!active) return
        setError(String(e))
        setPracticeSet(null)
        setLoading(false)
      })

    return () => {
      active = false
      controller.abort()
    }
  }, [topic])

  return (
    <div className="page-enter">
      <header className="practice-header">
        {meta && <span className="practice-icon">{meta.icon}</span>}
        <div>
          <h1 className="practice-title">{meta?.title ?? topic}</h1>
          <p className="practice-subtitle">{meta?.subtitle ?? ''}</p>
          {practiceSet && !loading && !error && (
            <div className="practice-summary">
              <span>{questions.length} opgaven</span>
              <span>{totalMarks} punten</span>
              <span>{tagCount} labels</span>
            </div>
          )}
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

      {practiceSet && !loading && !error && (
        <div className="practice-list">
          {questions.length > 0 ? (
            questions.map(question => (
              <ExerciseCard key={question.id} exercise={question} />
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
