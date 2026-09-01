import { useState } from 'react'
import { MathJax } from 'better-react-mathjax'
import type { QuestionResponse } from '../types/api'
import { Badge } from './ui'
import './ExerciseCard.css'

interface ExerciseCardProps {
  exercise: QuestionResponse
  number: number
}

type DifficultyTone = 'easy' | 'med' | 'hard' | 'neutral'

function difficultyMeta(difficulty?: number | null): { label: string; tone: DifficultyTone } {
  if (difficulty == null) {
    return { label: 'Onbekend', tone: 'neutral' }
  }

  if (difficulty <= 1) {
    return { label: 'Makkelijk', tone: 'easy' }
  }

  if (difficulty === 2) {
    return { label: 'Gemiddeld', tone: 'med' }
  }

  return { label: 'Moeilijk', tone: 'hard' }
}

export default function ExerciseCard({ exercise, number }: ExerciseCardProps) {
  const [expanded, setExpanded] = useState(false)
  const difficulty = difficultyMeta(exercise.difficulty)
  const bodyId = `exercise-${exercise.id}-body`
  const toggleExpanded = () => setExpanded(current => !current)

  return (
    <article className={`ex-card ${expanded ? 'ex-card--expanded' : ''}`}>
      <header className="ex-card-header" onClick={toggleExpanded}>
        <div className="ex-card-title-row">
          <span className="ex-card-number">Opgave {number}</span>
          {exercise.title && <span className="ex-card-title">{exercise.title}</span>}
        </div>
        <div className="ex-card-meta">
          <Badge tone={difficulty.tone}>{difficulty.label}</Badge>
          {exercise.max_marks > 0 && (
            <Badge tone="neutral">{exercise.max_marks}p</Badge>
          )}
          <Badge tone="neutral">
            {exercise.calculator_allowed ? 'Rekenmachine' : 'Zonder rekenmachine'}
          </Badge>
          <button
            type="button"
            className="ex-card-toggle"
            aria-label={expanded ? 'Inklappen' : 'Uitklappen'}
            aria-expanded={expanded}
            aria-controls={bodyId}
            onClick={event => {
              event.stopPropagation()
              toggleExpanded()
            }}
          >
            <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
              <path
                d="M4.5 7L9 11.5L13.5 7"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </button>
        </div>
      </header>

      {expanded && (
        <div className="ex-card-body" id={bodyId}>
          <div className="ex-card-divider" />
          <MathJax dynamic>
            <div
              className="ex-card-stem"
              dangerouslySetInnerHTML={{ __html: exercise.question_text }}
            />
            {exercise.parts.length > 0 && (
              <ol className="ex-card-parts" type="a">
                {exercise.parts.map(part => (
                  <li key={part.label} dangerouslySetInnerHTML={{ __html: part.text }} />
                ))}
              </ol>
            )}
          </MathJax>
        </div>
      )}
    </article>
  )
}
