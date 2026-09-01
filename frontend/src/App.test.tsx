import { afterEach, describe, expect, it, vi } from 'vitest'
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter, useLocation } from 'react-router-dom'
import App from './App'

function LocationProbe() {
  const location = useLocation()
  return (
    <output data-testid="location">
      {JSON.stringify({ pathname: location.pathname, state: location.state })}
    </output>
  )
}

afterEach(() => {
  cleanup()
  vi.unstubAllGlobals()
})

describe('App routing', () => {
  it('preserves the requested route when navigating from login to signup', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: false,
        status: 401,
      }),
    )

    render(
      <MemoryRouter
        initialEntries={[
          {
            pathname: '/login',
            state: { from: { pathname: '/practice/derivatives' } },
          },
        ]}
      >
        <App />
        <LocationProbe />
      </MemoryRouter>,
    )

    fireEvent.click(
      await screen.findByRole('link', { name: 'Account aanmaken' }),
    )

    await waitFor(() => {
      expect(screen.getByTestId('location')).toHaveTextContent(
        JSON.stringify({
          pathname: '/signup',
          state: { from: { pathname: '/practice/derivatives' } },
        }),
      )
    })
  })

  it('redirects an authenticated user away from signup', async () => {
    const user = { id: 2, username: 'ada', role: 'student' }
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        json: async () => user,
      }),
    )

    render(
      <MemoryRouter initialEntries={['/signup']}>
        <App />
        <LocationProbe />
      </MemoryRouter>,
    )

    expect(
      await screen.findByRole('heading', {
        name: 'Waar wil je mee aan de slag?',
      }),
    ).toBeInTheDocument()
    expect(screen.getByTestId('location')).toHaveTextContent(
      JSON.stringify({ pathname: '/', state: null }),
    )
  })
})
