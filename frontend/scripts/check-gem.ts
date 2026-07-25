import {
  DEFAULT_PALETTE,
  OUTLINE_SCALE,
  applyFacetColors,
  buildEdgeLines,
  buildGemGeometry,
  buildGemMesh,
  buildOutlineMesh,
} from '../src/components/gem/gemScene.ts'

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

const mesh = buildGemMesh(DEFAULT_PALETTE)
check('gem mesh built', mesh.geometry !== undefined && mesh.material !== undefined)

const outline = buildOutlineMesh(geometry, DEFAULT_PALETTE.ink)
check('outline scaled outward', outline.scale.x === OUTLINE_SCALE && OUTLINE_SCALE > 1)

const edges = buildEdgeLines(geometry, DEFAULT_PALETTE.ink)
check('edge lines built', edges.geometry !== undefined)

if (failures > 0) {
  console.error(`\ncheck-gem: ${failures} failure(s)`)
  process.exit(1)
}
console.log('\ncheck-gem: all checks passed')
