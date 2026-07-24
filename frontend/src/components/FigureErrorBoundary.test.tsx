import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import FigureErrorBoundary from './FigureErrorBoundary'

function Boom(): never {
  throw new Error('boom')
}

describe('FigureErrorBoundary', () => {
  it('renders children when nothing throws', () => {
    render(
      <FigureErrorBoundary fallback={<div>fallback</div>}>
        <div>content</div>
      </FigureErrorBoundary>,
    )
    expect(screen.getByText('content')).toBeInTheDocument()
  })

  it('renders the fallback when a child throws', () => {
    render(
      <FigureErrorBoundary fallback={<div>fallback</div>}>
        <Boom />
      </FigureErrorBoundary>,
    )
    expect(screen.getByText('fallback')).toBeInTheDocument()
  })
})
