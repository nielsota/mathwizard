import { useState } from 'react'
import type { FormEvent } from 'react'
import type { LoginRequest, UserResponse } from '../types/api'
import { Card, Button, Input } from '../components/ui'
import Logo from '../components/Logo'
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
        <aside className="login-brand" aria-hidden="true">
          <p className="login-kicker">Beveiligde sessie</p>
          <div className="login-brand-mark">
            <Logo showWordmark={false} size={96} />
          </div>
          <p className="login-brand-word">MathWizard</p>
          <p className="login-brand-tagline">Toegang tot je oefenruimte</p>
        </aside>

        <Card hard className="login-card">
          <h1 id="login-title" className="login-title">Welkom terug</h1>
          <p className="login-subtitle">
            Log in om oefenopgaven en je MathWizard werkruimte te openen.
          </p>

          <form className="login-form" onSubmit={handleSubmit} aria-busy={loading}>
            <Input
              id="login-username"
              label="Gebruikersnaam"
              value={username}
              onChange={e => setUsername(e.target.value)}
              autoComplete="username"
              required
            />

            <Input
              id="login-password"
              label="Wachtwoord"
              type="password"
              value={password}
              onChange={e => setPassword(e.target.value)}
              autoComplete="current-password"
              required
            />

            {error && (
              <div className="login-error" role="alert">
                {error}
              </div>
            )}

            <Button variant="primary" fullWidth type="submit" disabled={loading} aria-busy={loading}>
              {loading ? 'Sessie openen...' : 'Sessie openen'}
            </Button>
          </form>
        </Card>
      </section>
    </div>
  )
}
