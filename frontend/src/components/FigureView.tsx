import { Mafs, Coordinates, Plot } from 'mafs'
import { compile } from 'mathjs'
import 'mafs/core.css'
import type { FigureSpec } from '../types/api'
import './FigureView.css'

const DEFAULT_Y: [number, number] = [-10, 10]
const DEFAULT_COLOR = '#2f5fed'

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
      return <Plot.OfX key={i} y={fn} color={element.color ?? DEFAULT_COLOR} />
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
