import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import Login from './Login'

describe('Login', () => {
  it('links to signup and does not prefill a username', () => {
    render(
      <MemoryRouter>
        <Login onLogin={vi.fn()} />
      </MemoryRouter>,
    )

    expect(screen.getByLabelText('Gebruikersnaam')).toHaveValue('')
    const link = screen.getByRole('link', { name: 'Account aanmaken' })
    expect(link).toHaveAttribute('href', '/signup')
  })
})
