import { useEffect, useRef, useState } from 'react'
import { useLocation } from 'react-router-dom'
import type {
  MyTeacherResponse,
  StudentsResponse,
  UserResponse,
} from '../types/api'
import './UserMenu.css'

interface UserMenuProps {
  user: UserResponse
  onUnauthorized: () => void
}

type FetchState<T> =
  | { status: 'idle' }
  | { status: 'loading' }
  | { status: 'error'; message: string }
  | { status: 'ready'; data: T }

function initials(name: string): string {
  return name.slice(0, 2).toUpperCase()
}

function StudentsContent({ onUnauthorized }: { onUnauthorized: () => void }) {
  const [state, setState] = useState<FetchState<StudentsResponse>>({ status: 'idle' })

  useEffect(() => {
    let active = true
    async function load() {
      setState({ status: 'loading' })
      try {
        const resp = await fetch('/api/v1/roster/students', { credentials: 'include' })
        if (!active) return
        if (resp.status === 401) {
          onUnauthorized()
          return
        }
        if (!resp.ok) {
          setState({ status: 'error', message: 'Kon leerlingen niet laden.' })
          return
        }
        const data: StudentsResponse = await resp.json()
        setState({ status: 'ready', data })
      } catch {
        if (active) setState({ status: 'error', message: 'Kon leerlingen niet laden.' })
      }
    }
    load()
    return () => {
      active = false
    }
  }, [onUnauthorized])

  if (state.status === 'loading' || state.status === 'idle') {
    return <p className="mw-um-hint">Laden...</p>
  }
  if (state.status === 'error') {
    return <p className="mw-um-hint mw-um-hint--error">{state.message}</p>
  }
  if (state.data.students.length === 0) {
    return <p className="mw-um-hint">Nog geen leerlingen toegewezen.</p>
  }
  return (
    <ul className="mw-um-list">
      {state.data.students.map(student => (
        <li key={student.id} className="mw-um-person">
          <span className="mw-um-avatar">{initials(student.username)}</span>
          <span className="mw-um-person-name">{student.username}</span>
        </li>
      ))}
    </ul>
  )
}

function MyTeacherContent({ onUnauthorized }: { onUnauthorized: () => void }) {
  const [state, setState] = useState<FetchState<MyTeacherResponse>>({ status: 'idle' })

  useEffect(() => {
    let active = true
    async function load() {
      setState({ status: 'loading' })
      try {
        const resp = await fetch('/api/v1/roster/my-teacher', { credentials: 'include' })
        if (!active) return
        if (resp.status === 401) {
          onUnauthorized()
          return
        }
        if (!resp.ok) {
          setState({ status: 'error', message: 'Kon docent niet laden.' })
          return
        }
        const data: MyTeacherResponse = await resp.json()
        setState({ status: 'ready', data })
      } catch {
        if (active) setState({ status: 'error', message: 'Kon docent niet laden.' })
      }
    }
    load()
    return () => {
      active = false
    }
  }, [onUnauthorized])

  if (state.status === 'loading' || state.status === 'idle') {
    return <p className="mw-um-hint">Laden...</p>
  }
  if (state.status === 'error') {
    return <p className="mw-um-hint mw-um-hint--error">{state.message}</p>
  }
  return (
    <div className="mw-um-person mw-um-person--highlight">
      <span className="mw-um-avatar mw-um-avatar--teacher">
        {initials(state.data.teacher.username)}
      </span>
      <span className="mw-um-person-name">{state.data.teacher.username}</span>
    </div>
  )
}

interface RosterCardProps {
  title: string
  subtitle: string
  icon: React.ReactNode
  children: React.ReactNode
}

function RosterCard({ title, subtitle, icon, children }: RosterCardProps) {
  const [expanded, setExpanded] = useState(false)
  return (
    <div className={`mw-um-card ${expanded ? 'mw-um-card--open' : ''}`}>
      <button
        type="button"
        className="mw-um-card-head"
        onClick={() => setExpanded(prev => !prev)}
        aria-expanded={expanded}
      >
        <span className="mw-um-card-icon">{icon}</span>
        <span className="mw-um-card-text">
          <span className="mw-um-card-title">{title}</span>
          <span className="mw-um-card-subtitle">{subtitle}</span>
        </span>
        <svg className="mw-um-card-chevron" width="14" height="14" viewBox="0 0 14 14" fill="none">
          <path d="M3.5 5.5L7 9L10.5 5.5" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
      </button>
      {expanded && <div className="mw-um-card-body">{children}</div>}
    </div>
  )
}

const studentsIcon = (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
    <circle cx="9" cy="8" r="3.2" stroke="currentColor" strokeWidth="1.8" />
    <path d="M3.5 19c0-3 2.5-5 5.5-5s5.5 2 5.5 5" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
    <path d="M16.5 6.5a2.6 2.6 0 010 5M18 19c0-2.4-1-4.2-2.6-5" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
  </svg>
)

const teacherIcon = (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
    <circle cx="12" cy="8" r="3.4" stroke="currentColor" strokeWidth="1.8" />
    <path d="M5 20c0-3.4 3.1-6 7-6s7 2.6 7 6" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
  </svg>
)

export default function UserMenu({ user, onUnauthorized }: UserMenuProps) {
  const [open, setOpen] = useState(false)
  const menuRef = useRef<HTMLDivElement>(null)
  const location = useLocation()

  useEffect(() => {
    setOpen(false)
  }, [location.pathname])

  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        setOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  return (
    <div className="mw-nav-dropdown mw-usermenu" ref={menuRef}>
      <button
        type="button"
        className={`mw-nav-link mw-dropdown-trigger ${open ? 'active' : ''}`}
        onClick={() => setOpen(prev => !prev)}
        aria-expanded={open}
        aria-label="Menu"
      >
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
          <rect x="1.5" y="1.5" width="5.5" height="5.5" rx="1.5" stroke="currentColor" strokeWidth="1.6" />
          <rect x="9" y="1.5" width="5.5" height="5.5" rx="1.5" stroke="currentColor" strokeWidth="1.6" />
          <rect x="1.5" y="9" width="5.5" height="5.5" rx="1.5" stroke="currentColor" strokeWidth="1.6" />
          <rect x="9" y="9" width="5.5" height="5.5" rx="1.5" stroke="currentColor" strokeWidth="1.6" />
        </svg>
        Menu
        <svg className="mw-chevron" width="14" height="14" viewBox="0 0 14 14" fill="none">
          <path d="M3.5 5.5L7 9L10.5 5.5" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
      </button>
      {open && (
        <div className="mw-dropdown-menu mw-usermenu-panel">
          <p className="mw-um-eyebrow">
            {user.role === 'teacher' ? 'Docent' : 'Leerling'}
          </p>
          {user.role === 'teacher' ? (
            <RosterCard
              title="Mijn leerlingen"
              subtitle="Bekijk je leerlingen"
              icon={studentsIcon}
            >
              <StudentsContent onUnauthorized={onUnauthorized} />
            </RosterCard>
          ) : (
            <RosterCard
              title="Mijn docent"
              subtitle="Bekijk je docent"
              icon={teacherIcon}
            >
              <MyTeacherContent onUnauthorized={onUnauthorized} />
            </RosterCard>
          )}
        </div>
      )}
    </div>
  )
}
