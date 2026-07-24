import { Component, type ErrorInfo, type ReactNode } from 'react'

interface FigureErrorBoundaryProps {
  fallback: ReactNode
  children: ReactNode
}

interface FigureErrorBoundaryState {
  hasError: boolean
}

export default class FigureErrorBoundary extends Component<
  FigureErrorBoundaryProps,
  FigureErrorBoundaryState
> {
  state: FigureErrorBoundaryState = { hasError: false }

  static getDerivedStateFromError(): FigureErrorBoundaryState {
    return { hasError: true }
  }

  componentDidCatch(error: Error, info: ErrorInfo): void {
    console.error('Figure render failed', error, info)
  }

  render(): ReactNode {
    if (this.state.hasError) {
      return this.props.fallback
    }
    return this.props.children
  }
}
