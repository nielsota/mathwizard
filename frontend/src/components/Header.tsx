import { useState, useRef, useEffect } from 'react'
import { Link, useLocation } from 'react-router-dom'
import type { UserResponse } from '../types/api'
import UserMenu from './UserMenu'
import './Header.css'

const practiceTopics = [
  { path: '/practice/unitcircle', label: 'Eenheidscirkel' },
  { path: '/practice/derivatives', label: 'Afgeleiden' },
  { path: '/practice/rootfinding', label: 'Wortels vinden' },
  { path: '/practice/parametric', label: 'Parametrisch' },
  { path: '/practice/goniometrie', label: 'Goniometrie' },
]

interface HeaderProps {
  user: UserResponse
  onLogout: () => void
  onUnauthorized: () => void
}

export default function Header({ user, onLogout, onUnauthorized }: HeaderProps) {
  const [dropdownOpen, setDropdownOpen] = useState(false)
  const dropdownRef = useRef<HTMLDivElement>(null)
  const location = useLocation()

  useEffect(() => {
    setDropdownOpen(false)
  }, [location.pathname])

  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setDropdownOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  return (
    <header className="mw-header">
      <div className="mw-header-inner">
        <Link to="/" className="mw-brand">
          <div className="mw-logo-mark">
            <svg viewBox="0 0 32 32" fill="none" width="28" height="28">
              <circle cx="16" cy="16" r="14" stroke="currentColor" strokeWidth="2" />
              <path d="M8 24 L12 10 L16 20 L20 10 L24 24" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" fill="none" />
            </svg>
          </div>
          <span className="mw-brand-name">MathWizard</span>
        </Link>

        <nav className="mw-nav">
          <div className="mw-nav-dropdown" ref={dropdownRef}>
            <button
              className={`mw-nav-link mw-dropdown-trigger ${dropdownOpen ? 'active' : ''}`}
              onClick={() => setDropdownOpen(!dropdownOpen)}
              aria-expanded={dropdownOpen}
            >
              Oefen onderwerpen
              <svg className="mw-chevron" width="14" height="14" viewBox="0 0 14 14" fill="none">
                <path d="M3.5 5.5L7 9L10.5 5.5" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </button>
            {dropdownOpen && (
              <div className="mw-dropdown-menu">
                {practiceTopics.map(t => (
                  <Link key={t.path} to={t.path} className="mw-dropdown-item">
                    {t.label}
                  </Link>
                ))}
              </div>
            )}
          </div>

          <Link
            to="/"
            className={`mw-nav-link ${location.pathname === '/' ? 'active' : ''}`}
          >
            Examenopgaven zoeken
          </Link>

          <UserMenu user={user} onUnauthorized={onUnauthorized} />

          <div className="mw-auth">
            <span className="mw-user">{user.username}</span>
            <button className="mw-logout" type="button" onClick={onLogout}>
              Uitloggen
            </button>
          </div>
        </nav>
      </div>
    </header>
  )
}
