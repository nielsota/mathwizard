import { compile, parse, OperatorNode, type EvalFunction } from 'mathjs'

export function compileExpression(expr: string): EvalFunction | null {
  try {
    return compile(expr)
  } catch {
    return null
  }
}

export function expressionToTeX(expr: string): string | null {
  try {
    const node = parse(expr).transform((n) => {
      if (n instanceof OperatorNode && n.op === '*' && !n.implicit) {
        return new OperatorNode('*', 'multiply', n.args, true)
      }
      return n
    })
    return node.toTex({ implicit: 'hide' })
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
