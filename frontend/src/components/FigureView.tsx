import { Mafs, Coordinates, Plot } from 'mafs'
import type { ReactNode } from 'react'
import 'mafs/core.css'
import { compileExpression, evaluateFinite } from '../lib/mathEval'
import FigureErrorBoundary from './FigureErrorBoundary'
import type { FigureSpec } from '../types/api'
import './FigureView.css'

const DEFAULT_Y: [number, number] = [-10, 10]
const DEFAULT_COLOR = '#2f5fed'

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
    plots.push(
      <Plot.OfX
        key={`${element.type}-${index}`}
        y={(x: number) => evaluateFinite(compiled, x)}
        color={element.color ?? DEFAULT_COLOR}
      />,
    )
  }

  return (
    <FigureErrorBoundary fallback={fallback}>
      <div className="figure-view">
        <Mafs viewBox={{ x: spec.viewport.x, y }} preserveAspectRatio={false}>
          {spec.show_grid && <Coordinates.Cartesian />}
          {plots}
        </Mafs>
      </div>
    </FigureErrorBoundary>
  )
}
