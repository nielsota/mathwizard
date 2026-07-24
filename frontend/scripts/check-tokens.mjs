// frontend/scripts/check-tokens.mjs
import { readdirSync, readFileSync, statSync } from "node:fs"
import { join, relative } from "node:path"

const ROOT = new URL("../src", import.meta.url).pathname
const HEX = /#[0-9a-fA-F]{3,8}\b/
const EXEMPT = new Set(["index.css"]) // defines primitives

function walk(dir) {
  const out = []
  for (const name of readdirSync(dir)) {
    const p = join(dir, name)
    if (statSync(p).isDirectory()) out.push(...walk(p))
    else if (name.endsWith(".css")) out.push(p)
  }
  return out
}

const offenders = []
for (const file of walk(ROOT)) {
  const base = file.split("/").pop()
  if (EXEMPT.has(base)) continue
  const lines = readFileSync(file, "utf8").split("\n")
  lines.forEach((line, i) => {
    if (HEX.test(line)) offenders.push(`${relative(ROOT, file)}:${i + 1}  ${line.trim()}`)
  })
}

if (offenders.length) {
  console.error(`✗ ${offenders.length} raw hex value(s) found outside index.css:\n`)
  console.error(offenders.join("\n"))
  process.exit(1)
}
console.log("✓ token compliance: no raw hex outside index.css")
