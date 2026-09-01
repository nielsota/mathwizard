import { useState } from 'react'
import type { FormEvent } from 'react'
import { Link } from 'react-router-dom'
import type { SignupRequest, UserResponse } from '../types/api'
import { Card, Button, Input } from '../components/ui'
import Logo from '../components/Logo'
import './Login.css'

interface SignupProps {
  onLogin: (user: UserResponse) => void
}

export default function Signup({ onLogin }: SignupProps) {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [passwordConfirm, setPasswordConfirm] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault()
    setError('')

    if (password !== passwordConfirm) {
      setError('Wachtwoorden komen niet overeen')
      return
    }

    setLoading(true)
    const payload: SignupRequest = {
      username,
      password,
      password_confirm: passwordConfirm,
    }

    try {
      const response = await fetch('/auth/signup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(payload),
      })

      if (response.status === 409) {
        setError('Deze gebruikersnaam is al in gebruik')
        return
      }

      if (!response.ok) {
        setError('Kon account niet aanmaken')
        return
      }

      const user: UserResponse = await response.json()
      onLogin(user)
    } catch {
      setError('Kon account niet aanmaken')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="login-page">
      <section className="login-shell" aria-labelledby="signup-title">
        <aside className="login-brand" aria-hidden="true">
          <p className="login-kicker">Nieuw account</p>
          <div className="login-brand-mark">
            <Logo showWordmark={false} size={96} />
          </div>
          <p className="login-brand-word">MathWizard</p>
          <p className="login-brand-tagline">Toegang tot je oefenruimte</p>
        </aside>

        <Card hard className="login-card">
          <h1 id="signup-title" className="login-title">Account aanmaken</h1>
          <p className="login-subtitle">
            Maak een leerlingaccount om oefenopgaven en je MathWizard werkruimte te openen.
          </p>

          <form className="login-form" onSubmit={handleSubmit} aria-busy={loading}>
            <Input
              id="signup-username"
              label="Gebruikersnaam"
              value={username}
              onChange={e => setUsername(e.target.value)}
              autoComplete="username"
              required
            />

            <Input
              id="signup-password"
              label="Wachtwoord"
              type="password"
              value={password}
              onChange={e => setPassword(e.target.value)}
              autoComplete="new-password"
              minLength={8}
              maxLength={64}
              required
            />

            <Input
              id="signup-password-confirm"
              label="Bevestig wachtwoord"
              type="password"
              value={passwordConfirm}
              onChange={e => setPasswordConfirm(e.target.value)}
              autoComplete="new-password"
              minLength={8}
              maxLength={64}
              required
            />

            {error && (
              <div className="login-error" role="alert">
                {error}
              </div>
            )}

            <Button variant="primary" fullWidth type="submit" disabled={loading} aria-busy={loading}>
              {loading ? 'Account aanmaken...' : 'Account aanmaken'}
            </Button>
          </form>

          <p className="login-switch">
            Al een account? <Link to="/login">Inloggen</Link>
          </p>
        </Card>
      </section>
    </div>
  )
}
