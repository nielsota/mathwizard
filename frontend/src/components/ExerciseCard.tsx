import { useState } from 'react'
import { MathJax } from 'better-react-mathjax'
import type { PracticeExercise } from '../types/api'
import './ExerciseCard.css'

interface ExerciseCardProps {
  exercise: PracticeExercise
}

export default function ExerciseCard({ exercise }: ExerciseCardProps) {
  const [expanded, setExpanded] = useState(false)

  return (
    <article className={`ex-card ${expanded ? 'ex-card--expanded' : ''}`}>
      <header className="ex-card-header" onClick={() => setExpanded(!expanded)}>
        <div className="ex-card-title-row">
          <span className="ex-card-number">Opgave {exercise.number}</span>
          {exercise.title && <span className="ex-card-title">{exercise.title}</span>}
        </div>
        <div className="ex-card-meta">
          {exercise.max_marks && (
            <span className="ex-badge ex-badge--marks">
              {exercise.max_marks}p
            </span>
          )}
          <span className={`ex-badge ${exercise.calculator_allowed ? 'ex-badge--calc' : 'ex-badge--no-calc'}`}>
            {exercise.calculator_allowed ? 'Rekenmachine' : 'Zonder rekenmachine'}
          </span>
          <button
            className="ex-card-toggle"
            aria-label={expanded ? 'Inklappen' : 'Uitklappen'}
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
        <div className="ex-card-body">
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
