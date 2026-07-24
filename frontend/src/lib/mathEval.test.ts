import { describe, it, expect } from 'vitest'
import { compileExpression, evaluateFinite } from './mathEval'

describe('compileExpression', () => {
  it('compiles a valid expression', () => {
    expect(compileExpression('x^2')).not.toBeNull()
  })

  it('returns null for invalid syntax', () => {
    expect(compileExpression('x^^2')).toBeNull()
  })
})

describe('evaluateFinite', () => {
  it('evaluates a finite value', () => {
    const compiled = compileExpression('x^2')
    expect(compiled).not.toBeNull()
    expect(evaluateFinite(compiled!, 3)).toBe(9)
  })

  it('returns NaN for a non-finite result (division by zero)', () => {
    const compiled = compileExpression('1/x')
    expect(Number.isNaN(evaluateFinite(compiled!, 0))).toBe(true)
  })

  it('returns NaN for a non-numeric result (complex root)', () => {
    const compiled = compileExpression('sqrt(x)')
    expect(Number.isNaN(evaluateFinite(compiled!, -1))).toBe(true)
  })
})
