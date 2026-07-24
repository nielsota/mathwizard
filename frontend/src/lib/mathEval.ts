import { compile, type EvalFunction } from 'mathjs'

export function compileExpression(expr: string): EvalFunction | null {
  try {
    return compile(expr)
  } catch {
    return null
  }
}

export function evaluateFinite(compiled: EvalFunction, x: number): number {
  try {
    const result: unknown = compiled.evaluate({ x })
    return typeof result === 'number' && Number.isFinite(result) ? result : NaN
  } catch {
    return NaN
  }
}
