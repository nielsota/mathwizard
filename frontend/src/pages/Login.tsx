import { useState } from 'react'
import type { FormEvent } from 'react'
import type { LoginRequest, UserResponse } from '../types/api'
import './Login.css'

interface LoginProps {
  onLogin: (user: UserResponse) => void
}

export default function Login({ onLogin }: LoginProps) {
  const [username, setUsername] = useState('root')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault()
    setLoading(true)
    setError('')

    const payload: LoginRequest = { username, password }

    try {
      const response = await fetch('/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(payload),
      })

      if (!response.ok) {
        throw new Error('Ongeldige gebruikersnaam of wachtwoord')
      }

      const user: UserResponse = await response.json()
      onLogin(user)
    } catch {
      setError('Ongeldige gebruikersnaam of wachtwoord')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="login-page">
      <section className="login-shell" aria-labelledby="login-title">
        <div className="login-proof" aria-hidden="true">
          <p className="login-kicker">MathWizard</p>
          <div className="login-integral">∫</div>
          <p className="login-equation">f&apos;(x) = lim Δx→0</p>
          <p className="login-proofline">Toegang tot je oefenruimte</p>
          <div className="login-axis login-axis--x" />
          <div className="login-axis login-axis--y" />
        </div>

        <div className="login-card">
          <p className="login-eyebrow">Beveiligde sessie</p>
          <h1 id="login-title" className="login-title">Welkom terug</h1>
          <p className="login-subtitle">
            Log in om oefenopgaven, examenmateriaal en je MathWizard werkruimte te openen.
          </p>

          <form className="login-form" onSubmit={handleSubmit}>
            <label className="login-label">
              Gebruikersnaam
              <input
                className="login-input"
                value={username}
                onChange={e => setUsername(e.target.value)}
                autoComplete="username"
                required
              />
            </label>

            <label className="login-label">
              Wachtwoord
              <input
                className="login-input"
                type="password"
                value={password}
                onChange={e => setPassword(e.target.value)}
                autoComplete="current-password"
                required
              />
            </label>

            {error && <div className="login-error">{error}</div>}

            <button className="login-button" type="submit" disabled={loading}>
              <span>{loading ? 'Sessie openen...' : 'Sessie openen'}</span>
              <span aria-hidden="true">→</span>
            </button>
          </form>
        </div>
      </section>
    </div>
  )
}
