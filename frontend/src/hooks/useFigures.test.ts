import { describe, it, expect, vi, afterEach } from 'vitest'
import { renderHook, waitFor } from '@testing-library/react'
import { useFigures } from './useFigures'

function jsonResponse(body: unknown, status = 200): Response {
  return {
    ok: status >= 200 && status < 300,
    status,
    json: async () => body,
  } as Response
}

const SPEC = {
  viewport: { x: [-5, 5] },
  show_grid: true,
  x_label: 'x',
  y_label: 'y',
  elements: [],
}

afterEach(() => {
  vi.restoreAllMocks()
})

const noop = () => {}

describe('useFigures', () => {
  it('loads the list then each detail', async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(jsonResponse({ figures: [{ id: 1, slug: 's', title: 't' }] }))
      .mockResolvedValueOnce(jsonResponse({ id: 1, slug: 's', title: 't', spec: SPEC }))
    vi.stubGlobal('fetch', fetchMock)

    const { result } = renderHook(() => useFigures(noop))

    await waitFor(() => expect(result.current.loading).toBe(false))
    expect(result.current.figures).toHaveLength(1)
    expect(result.current.error).toBe('')
  })

  it('calls onUnauthorized on a 401 list response', async () => {
    const onUnauthorized = vi.fn()
    vi.stubGlobal('fetch', vi.fn().mockResolvedValueOnce(jsonResponse(null, 401)))

    renderHook(() => useFigures(onUnauthorized))

    await waitFor(() => expect(onUnauthorized).toHaveBeenCalledTimes(1))
  })

  it('sets error when the list fetch fails', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValueOnce(jsonResponse(null, 500)))

    const { result } = renderHook(() => useFigures(noop))

    await waitFor(() => expect(result.current.loading).toBe(false))
    expect(result.current.error).toContain('500')
  })
})
