import {
  BackSide,
  BufferGeometry,
  Color,
  EdgesGeometry,
  Float32BufferAttribute,
  LineBasicMaterial,
  LineSegments,
  Mesh,
  MeshBasicMaterial,
  OctahedronGeometry,
} from 'three'

export const REST_ROTATION = { x: -0.18, y: 0.5 }
export const MAX_TILT = 0.26
export const OUTLINE_SCALE = 1.03

export interface GemPalette {
  facets: Color[]
  ink: Color
}

// Fallback values (used under Node / when CSS vars are missing). These mirror
// the logo palette tokens; the running app overrides them from CSS custom
// properties, so these are the ONLY raw color values in TS.
export const DEFAULT_PALETTE: GemPalette = {
  facets: [
    new Color('#9bbee6'), // --sky-400
    new Color('#bad6f0'), // --sky-300
    new Color('#d2e5f7'), // --sky-200
    new Color('#fbe3c6'), // --peach-200
  ],
  ink: new Color('#111318'), // --ink-950
}

export function buildGemGeometry(): BufferGeometry {
  const geometry = new OctahedronGeometry(1, 0)
  geometry.scale(1, 1.35, 1)
  return geometry
}

export function applyFacetColors(geometry: BufferGeometry, facets: Color[]): void {
  const position = geometry.getAttribute('position')
  const vertexCount = position.count
  const colors = new Float32Array(vertexCount * 3)
  const triangleCount = vertexCount / 3
  for (let t = 0; t < triangleCount; t += 1) {
    const facet = facets[t % facets.length]
    for (let v = 0; v < 3; v += 1) {
      const offset = (t * 3 + v) * 3
      colors[offset] = facet.r
      colors[offset + 1] = facet.g
      colors[offset + 2] = facet.b
    }
  }
  geometry.setAttribute('color', new Float32BufferAttribute(colors, 3))
}

export function buildGemMesh(palette: GemPalette): Mesh {
  const geometry = buildGemGeometry()
  applyFacetColors(geometry, palette.facets)
  const material = new MeshBasicMaterial({ vertexColors: true })
  return new Mesh(geometry, material)
}

export function buildOutlineMesh(geometry: BufferGeometry, ink: Color): Mesh {
  const material = new MeshBasicMaterial({ color: ink, side: BackSide })
  const mesh = new Mesh(geometry, material)
  mesh.scale.setScalar(OUTLINE_SCALE)
  return mesh
}

export function buildEdgeLines(geometry: BufferGeometry, ink: Color): LineSegments {
  const edges = new EdgesGeometry(geometry, 1)
  return new LineSegments(edges, new LineBasicMaterial({ color: ink }))
}
