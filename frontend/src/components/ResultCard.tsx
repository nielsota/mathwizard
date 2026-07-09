import { MathJax } from 'better-react-mathjax'
import type { FetchResponse } from '../types/api'
import './ResultCard.css'

interface ResultCardProps {
  result: FetchResponse
}

export default function ResultCard({ result }: ResultCardProps) {
  const { formatted, figure_images, record_id, score } = result

  return (
    <article className="result-card">
      <div className="result-meta">
        <span className="result-pill">
          <span className="result-pill-label">ID</span>
          {record_id}
        </span>
        <span className="result-pill result-pill--score">
          <span className="result-pill-label">Score</span>
          {typeof score === 'number' ? score.toFixed(3) : score}
        </span>
      </div>

      <MathJax dynamic>
        <div className="result-section">
          <h3 className="result-section-title">Opgave</h3>
          <div className="result-stem">{formatted.stem}</div>
        </div>

        {formatted.parts.length > 0 && (
          <div className="result-section">
            <h3 className="result-section-title">Onderdelen</h3>
            <ol className="result-parts" type="a">
              {formatted.parts.map((p, i) => (
                <li key={i}>{p.text}</li>
              ))}
            </ol>
          </div>
        )}
      </MathJax>

      {figure_images.length > 0 && (
        <div className="result-section">
          <h3 className="result-section-title">Figuren</h3>
          <div className="result-figures">
            {figure_images.map((url, i) => (
              <img key={i} src={url} alt={`Figuur ${i + 1}`} loading="lazy" />
            ))}
          </div>
        </div>
      )}
    </article>
  )
}
