import {
  DEFAULT_PALETTE,
  OUTLINE_SCALE,
  applyFacetColors,
  buildEdgeLines,
  buildGemGeometry,
  buildGemMesh,
  buildOutlineMesh,
} from '../src/components/gem/gemScene.ts'
import { BackSide, LineBasicMaterial, MeshBasicMaterial } from 'three'

let failures = 0
function check(label: string, cond: boolean): void {
  if (!cond) {
    failures += 1
    console.error(`FAIL: ${label}`)
  } else {
    console.log(`ok: ${label}`)
  }
}

const geometry = buildGemGeometry()
const position = geometry.getAttribute('position')
check('geometry has vertices', position.count > 0)
check('geometry vertices form whole triangles', position.count % 3 === 0)

applyFacetColors(geometry, DEFAULT_PALETTE.facets)
const color = geometry.getAttribute('color')
check('facet colors applied per vertex', color !== undefined && color.count === position.count)

const facet0 = DEFAULT_PALETTE.facets[0]
const expectedRgb = new Float32Array([facet0.r, facet0.g, facet0.b])
check(
  'first vertex RGB matches facet palette',
  color !== undefined &&
    color.array[0] === expectedRgb[0] &&
    color.array[1] === expectedRgb[1] &&
    color.array[2] === expectedRgb[2],
)

const mesh = buildGemMesh(DEFAULT_PALETTE)
check('gem mesh built', mesh.geometry !== undefined && mesh.material !== undefined)
check(
  'gem material is MeshBasicMaterial with vertexColors',
  mesh.material instanceof MeshBasicMaterial && mesh.material.vertexColors === true,
)

const outline = buildOutlineMesh(geometry, DEFAULT_PALETTE.ink)
check('outline scaled outward', outline.scale.x === OUTLINE_SCALE && OUTLINE_SCALE > 1)
check(
  'outline material uses BackSide',
  outline.material instanceof MeshBasicMaterial && outline.material.side === BackSide,
)

const edges = buildEdgeLines(geometry, DEFAULT_PALETTE.ink)
check('edge lines built', edges.geometry !== undefined)
check('edge material is LineBasicMaterial', edges.material instanceof LineBasicMaterial)

if (failures > 0) {
  console.error(`\ncheck-gem: ${failures} failure(s)`)
  process.exit(1)
}
console.log('\ncheck-gem: all checks passed')
