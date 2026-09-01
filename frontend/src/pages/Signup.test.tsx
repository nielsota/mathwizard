import { describe, it, expect, vi, afterEach } from 'vitest'
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import Signup from './Signup'

function renderSignup(onLogin = vi.fn()) {
  return render(
    <MemoryRouter>
      <Signup onLogin={onLogin} />
    </MemoryRouter>,
  )
}

afterEach(() => {
  cleanup()
  vi.unstubAllGlobals()
})

describe('Signup', () => {
  it('blocks submit when passwords differ', async () => {
    const fetchMock = vi.fn()
    vi.stubGlobal('fetch', fetchMock)
    renderSignup()

    fireEvent.change(screen.getByLabelText('Gebruikersnaam'), {
      target: { value: 'ada' },
    })
    fireEvent.change(screen.getByLabelText('Wachtwoord'), {
      target: { value: 'password1' },
    })
    fireEvent.change(screen.getByLabelText('Bevestig wachtwoord'), {
      target: { value: 'password2' },
    })
    fireEvent.click(screen.getByRole('button', { name: 'Account aanmaken' }))

    expect(
      await screen.findByRole('alert'),
    ).toHaveTextContent('Wachtwoorden komen niet overeen')
    expect(fetchMock).not.toHaveBeenCalled()
  })

  it('posts signup and calls onLogin', async () => {
    const user = { id: 2, username: 'ada', role: 'student' }
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        json: async () => user,
      }),
    )
    const onLogin = vi.fn()
    renderSignup(onLogin)

    fireEvent.change(screen.getByLabelText('Gebruikersnaam'), {
      target: { value: 'ada' },
    })
    fireEvent.change(screen.getByLabelText('Wachtwoord'), {
      target: { value: 'password1' },
    })
    fireEvent.change(screen.getByLabelText('Bevestig wachtwoord'), {
      target: { value: 'password1' },
    })
    fireEvent.click(screen.getByRole('button', { name: 'Account aanmaken' }))

    await waitFor(() => {
      expect(onLogin).toHaveBeenCalledWith(user)
    })
    expect(fetch).toHaveBeenCalledWith('/auth/signup', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({
        username: 'ada',
        password: 'password1',
        password_confirm: 'password1',
      }),
    })
  })

  it('shows a duplicate-username error on 409', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: false,
        status: 409,
        json: async () => ({ detail: "Username 'ada' is already taken" }),
      }),
    )
    renderSignup()

    fireEvent.change(screen.getByLabelText('Gebruikersnaam'), {
      target: { value: 'ada' },
    })
    fireEvent.change(screen.getByLabelText('Wachtwoord'), {
      target: { value: 'password1' },
    })
    fireEvent.change(screen.getByLabelText('Bevestig wachtwoord'), {
      target: { value: 'password1' },
    })
    fireEvent.click(screen.getByRole('button', { name: 'Account aanmaken' }))

    expect(
      await screen.findByRole('alert'),
    ).toHaveTextContent('Deze gebruikersnaam is al in gebruik')
  })

  it('links back to login', () => {
    renderSignup()
    const link = screen.getByRole('link', { name: 'Inloggen' })
    expect(link).toHaveAttribute('href', '/login')
  })
})
