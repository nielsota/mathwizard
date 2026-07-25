import { Mafs, Coordinates, Plot } from 'mafs'
import type { ReactNode } from 'react'
import { MathJax } from 'better-react-mathjax'
import 'mafs/core.css'
import { compileExpression, evaluateFinite, expressionToTeX } from '../lib/mathEval'
import FigureErrorBoundary from './FigureErrorBoundary'
import type { FigureSpec } from '../types/api'
import './FigureView.css'

const DEFAULT_Y: [number, number] = [-10, 10]

// House palette. Color AND line style vary per curve so multiple plots stay
// distinguishable without relying on color alone (accessibility).
const CURVE_STYLES: { color: string; style: 'solid' | 'dashed'; weight: number }[] = [
  { color: 'var(--sky-600)', style: 'solid', weight: 2.5 },
  { color: 'var(--peach-400)', style: 'dashed', weight: 2.5 },
  { color: 'var(--ink-600)', style: 'dashed', weight: 4 },
]

const fallback = <div className="figure-error">Kon figuur niet tekenen</div>

interface FigureViewProps {
  spec: FigureSpec
}

export default function FigureView({ spec }: FigureViewProps) {
  const y = spec.viewport.y ?? DEFAULT_Y

  const plots: ReactNode[] = []
  for (const [index, element] of spec.elements.entries()) {
    const compiled = compileExpression(element.fn)
    if (compiled === null) {
      return fallback
    }
    const preset = CURVE_STYLES[index % CURVE_STYLES.length]
    plots.push(
      <Plot.OfX
        key={`${element.type}-${index}`}
        y={(x: number) => evaluateFinite(compiled, x)}
        color={element.color ?? preset.color}
        style={preset.style}
        weight={preset.weight}
      />,
    )
  }

  const equations = spec.elements
    .map((element) => expressionToTeX(element.fn))
    .filter((tex): tex is string => tex !== null)

  return (
    <FigureErrorBoundary fallback={fallback}>
      <figure className="figure-view">
        <Mafs viewBox={{ x: spec.viewport.x, y }} preserveAspectRatio={false}>
          {spec.show_grid && <Coordinates.Cartesian subdivisions={2} />}
          {plots}
        </Mafs>
        {equations.length > 0 && (
          <figcaption className="figure-equation">
            {equations.map((tex, i) => (
              <MathJax key={i} inline dynamic>{`\\( y = ${tex} \\)`}</MathJax>
            ))}
          </figcaption>
        )}
      </figure>
    </FigureErrorBoundary>
  )
}
