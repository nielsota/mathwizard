import { useState, useRef, useEffect } from 'react'
import { Link, useLocation } from 'react-router-dom'
import type { UserResponse } from '../types/api'
import { TOPICS } from '../constants/topics'
import UserMenu from './UserMenu'
import Logo from './Logo'
import './Header.css'

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
          <Logo size={30} />
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
                {TOPICS.map(topic => (
                  <Link key={topic.slug} to={`/practice/${topic.slug}`} className="mw-dropdown-item">
                    {topic.label}
                  </Link>
                ))}
              </div>
            )}
          </div>

          <UserMenu user={user} onUnauthorized={onUnauthorized} onLogout={onLogout} />
        </nav>
      </div>
    </header>
  )
}
