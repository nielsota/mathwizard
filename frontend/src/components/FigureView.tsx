import { Mafs, Coordinates, Plot } from 'mafs'
import { compile } from 'mathjs'
import 'mafs/core.css'
import type { FigureSpec } from '../types/api'
import './FigureView.css'

const DEFAULT_Y: [number, number] = [-10, 10]

// House palette. Color AND line style vary per curve so multiple plots stay
// distinguishable without relying on color alone (accessibility).
const CURVE_STYLES: { color: string; style: 'solid' | 'dashed' }[] = [
  { color: 'var(--sky-600)', style: 'solid' },
  { color: 'var(--peach-400)', style: 'dashed' },
  { color: 'var(--ink-600)', style: 'dashed' },
]

interface FigureViewProps {
  spec: FigureSpec
}

export default function FigureView({ spec }: FigureViewProps) {
  const y = spec.viewport.y ?? DEFAULT_Y

  let plots: React.ReactNode
  try {
    plots = spec.elements.map((element, i) => {
      const node = compile(element.fn)
      const fn = (x: number) => node.evaluate({ x }) as number
      const preset = CURVE_STYLES[i % CURVE_STYLES.length]
      return (
        <Plot.OfX
          key={i}
          y={fn}
          color={element.color ?? preset.color}
          style={preset.style}
          weight={2.5}
        />
      )
    })
  } catch {
    return <div className="figure-error">Kon figuur niet tekenen</div>
  }

  return (
    <div className="figure-view">
      <Mafs viewBox={{ x: spec.viewport.x, y }} preserveAspectRatio={false}>
        {spec.show_grid && <Coordinates.Cartesian />}
        {plots}
      </Mafs>
    </div>
  )
}
