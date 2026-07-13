import { useState } from 'react'
import { MathJax } from 'better-react-mathjax'
import type { QuestionResponse } from '../types/api'
import './ExerciseCard.css'

interface ExerciseCardProps {
  exercise: QuestionResponse
}

function difficultyMeta(difficulty?: number | null) {
  if (difficulty == null) {
    return { label: 'Unknown', className: 'ex-badge--difficulty-unknown' }
  }

  if (difficulty <= 1) {
    return { label: 'Easy', className: 'ex-badge--difficulty-easy' }
  }

  if (difficulty === 2) {
    return { label: 'Medium', className: 'ex-badge--difficulty-medium' }
  }

  return { label: 'Hard', className: 'ex-badge--difficulty-hard' }
}

export default function ExerciseCard({ exercise }: ExerciseCardProps) {
  const [expanded, setExpanded] = useState(false)
  const difficulty = difficultyMeta(exercise.difficulty)
  const bodyId = `exercise-${exercise.id}-body`
  const toggleExpanded = () => setExpanded(current => !current)

  return (
    <article className={`ex-card ${expanded ? 'ex-card--expanded' : ''}`}>
      <header className="ex-card-header" onClick={toggleExpanded}>
        <div className="ex-card-title-row">
          <span className="ex-card-number">Opgave {exercise.number}</span>
          {exercise.title && <span className="ex-card-title">{exercise.title}</span>}
        </div>
        <div className="ex-card-meta">
          <span className={`ex-badge ex-badge--difficulty ${difficulty.className}`}>
            {difficulty.label}
          </span>
          {exercise.max_marks > 0 && (
            <span className="ex-badge ex-badge--marks">
              {exercise.max_marks}p
            </span>
          )}
          <span className={`ex-badge ${exercise.calculator_allowed ? 'ex-badge--calc' : 'ex-badge--no-calc'}`}>
            {exercise.calculator_allowed ? 'Rekenmachine' : 'Zonder rekenmachine'}
          </span>
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
                {exercise.parts.map((part, i) => (
                  <li key={i} dangerouslySetInnerHTML={{ __html: part }} />
                ))}
              </ol>
            )}
          </MathJax>

          {exercise.figure_images.length > 0 && (
            <div className="ex-card-figures">
              {exercise.figure_images.map((src, i) => (
                <img key={i} src={src} alt={`Figuur ${i + 1}`} loading="lazy" />
              ))}
            </div>
          )}
        </div>
      )}
    </article>
  )
}
