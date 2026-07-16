import { useCallback, useEffect, useState } from 'react'
import { Navigate, Route, Routes, useLocation, useNavigate } from 'react-router-dom'
import Header from './components/Header'
import ExamSearch from './pages/ExamSearch'
import Login from './pages/Login'
import Practice from './pages/Practice'
import type { UserResponse } from './types/api'
import './App.css'

function App() {
  const [user, setUser] = useState<UserResponse | null>(null)
  const [checkingSession, setCheckingSession] = useState(true)
  const navigate = useNavigate()
  const location = useLocation()

  useEffect(() => {
    let active = true

    async function loadSession() {
      try {
        const response = await fetch('/auth/me', { credentials: 'include' })
        if (!active) return
        if (response.ok) {
          const data: UserResponse = await response.json()
          setUser(data)
        } else {
          setUser(null)
        }
      } catch {
        if (active) setUser(null)
      } finally {
        if (active) setCheckingSession(false)
      }
    }

    loadSession()
    return () => {
      active = false
    }
  }, [])

  const handleUnauthorized = useCallback(() => {
    setUser(null)
    navigate('/login', { replace: true, state: { from: location } })
  }, [location, navigate])

  async function handleLogout() {
    try {
      await fetch('/auth/logout', {
        method: 'POST',
        credentials: 'include',
      })
    } finally {
      setUser(null)
      navigate('/login')
    }
  }

  function handleLogin(nextUser: UserResponse) {
    setUser(nextUser)
    const state = location.state as { from?: { pathname?: string } } | null
    const target = state?.from?.pathname ?? '/'
    navigate(target, { replace: true })
  }

  if (checkingSession) {
    return <div className="app-loading">MathWizard laden...</div>
  }

  return (
    <>
      {user && <Header user={user} onLogout={handleLogout} onUnauthorized={handleUnauthorized} />}
      <main>
        <Routes>
          <Route
            path="/login"
            element={user ? <Navigate to="/" replace /> : <Login onLogin={handleLogin} />}
          />
          <Route
            path="/"
            element={user ? <ExamSearch onUnauthorized={handleUnauthorized} /> : <Navigate to="/login" replace state={{ from: location }} />}
          />
          <Route
            path="/practice/:topic"
            element={user ? <Practice onUnauthorized={handleUnauthorized} /> : <Navigate to="/login" replace state={{ from: location }} />}
          />
        </Routes>
      </main>
    </>
  )
}

export default App
