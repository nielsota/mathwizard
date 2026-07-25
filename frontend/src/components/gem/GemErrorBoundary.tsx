import { Component, type ErrorInfo, type ReactNode } from 'react'

interface GemErrorBoundaryProps {
  fallback: ReactNode
  children: ReactNode
}

interface GemErrorBoundaryState {
  hasError: boolean
}

export default class GemErrorBoundary extends Component<
  GemErrorBoundaryProps,
  GemErrorBoundaryState
> {
  state: GemErrorBoundaryState = { hasError: false }

  static getDerivedStateFromError(): GemErrorBoundaryState {
    return { hasError: true }
  }

  componentDidCatch(_error: Error, _errorInfo: ErrorInfo): void {}

  render() {
    if (this.state.hasError) {
      return this.props.fallback
    }
    return this.props.children
  }
}
