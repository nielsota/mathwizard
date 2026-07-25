import { useEffect, useRef } from 'react'
import {
  Color,
  Group,
  OrthographicCamera,
  Scene,
  WebGLRenderer,
} from 'three'
import {
  DEFAULT_PALETTE,
  MAX_TILT,
  REST_ROTATION,
  buildEdgeLines,
  buildGemMesh,
  buildOutlineMesh,
  type GemPalette,
} from './gemScene'

function readColor(styles: CSSStyleDeclaration, varName: string, fallback: Color): Color {
  const raw = styles.getPropertyValue(varName).trim()
  if (raw === '') return fallback
  try {
    return new Color(raw)
  } catch {
    return fallback
  }
}

function readPalette(): GemPalette {
  if (typeof document === 'undefined') return DEFAULT_PALETTE
  const styles = getComputedStyle(document.documentElement)
  return {
    facets: [
      readColor(styles, '--sky-400', DEFAULT_PALETTE.facets[0]),
      readColor(styles, '--sky-300', DEFAULT_PALETTE.facets[1]),
      readColor(styles, '--sky-200', DEFAULT_PALETTE.facets[2]),
      readColor(styles, '--peach-200', DEFAULT_PALETTE.facets[3]),
    ],
    ink: readColor(styles, '--ink-950', DEFAULT_PALETTE.ink),
  }
}

interface GemCanvasProps {
  size: number
}

export default function GemCanvas({ size }: GemCanvasProps) {
  const mountRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const mount = mountRef.current
    if (mount === null) return

    const palette = readPalette()
    const scene = new Scene()

    const frustum = 1.6
    const camera = new OrthographicCamera(-frustum, frustum, frustum, -frustum, 0.1, 10)
    camera.position.z = 4

    const renderer = new WebGLRenderer({ antialias: true, alpha: true })
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
    renderer.setSize(size, size)
    mount.appendChild(renderer.domElement)

    const gem = buildGemMesh(palette)
    const outline = buildOutlineMesh(gem.geometry, palette.ink)
    const edges = buildEdgeLines(gem.geometry, palette.ink)

    const group = new Group()
    group.add(outline)
    group.add(gem)
    group.add(edges)
    group.rotation.x = REST_ROTATION.x
    group.rotation.y = REST_ROTATION.y
    scene.add(group)

    const target = { x: REST_ROTATION.x, y: REST_ROTATION.y }

    function handlePointerMove(event: PointerEvent) {
      const rect = renderer.domElement.getBoundingClientRect()
      const nx = ((event.clientX - rect.left) / rect.width) * 2 - 1
      const ny = ((event.clientY - rect.top) / rect.height) * 2 - 1
      target.y = REST_ROTATION.y + nx * MAX_TILT
      target.x = REST_ROTATION.x + ny * MAX_TILT
    }

    function handlePointerLeave() {
      target.x = REST_ROTATION.x
      target.y = REST_ROTATION.y
    }

    const interactionSurface = mount.closest<HTMLElement>('.login-brand') ?? mount
    interactionSurface.addEventListener('pointermove', handlePointerMove)
    interactionSurface.addEventListener('pointerleave', handlePointerLeave)

    let frameId = 0
    function animate() {
      group.rotation.x += (target.x - group.rotation.x) * 0.1
      group.rotation.y += (target.y - group.rotation.y) * 0.1
      renderer.render(scene, camera)
      frameId = requestAnimationFrame(animate)
    }
    animate()

    const resizeObserver = new ResizeObserver(() => {
      renderer.setSize(size, size)
    })
    resizeObserver.observe(mount)

    return () => {
      cancelAnimationFrame(frameId)
      resizeObserver.disconnect()
      interactionSurface.removeEventListener('pointermove', handlePointerMove)
      interactionSurface.removeEventListener('pointerleave', handlePointerLeave)
      renderer.domElement.remove()
      renderer.dispose()
      gem.geometry.dispose()
      ;(gem.material as { dispose(): void }).dispose()
      ;(outline.material as { dispose(): void }).dispose()
      edges.geometry.dispose()
      ;(edges.material as { dispose(): void }).dispose()
    }
  }, [size])

  return <div ref={mountRef} className="gem-canvas" style={{ width: size, height: size }} aria-hidden="true" />
}
