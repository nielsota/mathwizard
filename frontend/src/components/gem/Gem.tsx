import { Suspense, lazy, useMemo } from 'react'
import Logo from '../Logo'
import { canRender3D } from './capabilities'
import GemErrorBoundary from './GemErrorBoundary'
import './Gem.css'

const GemCanvas = lazy(() => import('./GemCanvas'))

interface GemProps {
  size?: number
}

export default function Gem({ size = 96 }: GemProps) {
  const enable3D = useMemo(() => canRender3D(), [])
  const fallback = <Logo showWordmark={false} size={size} />

  if (!enable3D) return fallback

  return (
    <div className="gem" style={{ width: size, height: size }}>
      <GemErrorBoundary fallback={fallback}>
        <Suspense fallback={fallback}>
          <GemCanvas size={size} />
        </Suspense>
      </GemErrorBoundary>
    </div>
  )
}
