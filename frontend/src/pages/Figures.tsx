import { MathJax } from 'better-react-mathjax'
import FigureView from '../components/FigureView'
import { Card } from '../components/ui'
import { useFigures } from '../hooks/useFigures'
import { expressionToTeX } from '../lib/mathEval'
import './Figures.css'

interface FiguresProps {
  onUnauthorized: () => void
}

export default function Figures({ onUnauthorized }: FiguresProps) {
  const { figures, loading, error } = useFigures(onUnauthorized)

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
          {figures.map((figure) => {
            const equation = figure.spec.elements
              .map((element) => expressionToTeX(element.fn))
              .filter((tex): tex is string => tex !== null)
              .map((tex) => `y = ${tex}`)
              .join(', ')
            return (
              <Card key={figure.id} className="figures-card">
                <h2 className="figures-card-title">
                  {figure.title}
                  {equation && (
                    <span className="figures-card-eq">
                      <MathJax inline dynamic>{`\\( ${equation} \\)`}</MathJax>
                    </span>
                  )}
                </h2>
                <FigureView spec={figure.spec} />
              </Card>
            )
          })}
        </div>
      )}
    </div>
  )
}
