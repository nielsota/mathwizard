import { useNavigate } from 'react-router-dom'
import { TOPICS } from '../constants/topics'
import type { UserResponse } from '../types/api'
import './Home.css'

interface HomeProps {
  user: UserResponse
}

export default function Home({ user }: HomeProps) {
  const navigate = useNavigate()

  return (
    <div className="page-enter home">
      <header className="home-hero">
        <p className="home-eyebrow">Welkom terug, {user.username}</p>
        <h1 className="home-title">Waar wil je mee aan de slag?</h1>
        <p className="home-lede">
          Oefen gericht per onderwerp of doorzoek de examenbank met AI-zoeken.
        </p>
      </header>

      <section className="home-section">
        <div className="home-section-head">
          <h2 className="home-section-title">Oefen onderwerpen</h2>
          <p className="home-section-sub">Kies een onderwerp om gericht te oefenen</p>
        </div>

        <div className="home-topic-grid">
          {TOPICS.map((topic, index) => (
            <button
              key={topic.slug}
              type="button"
              className="home-topic-card"
              style={{ animationDelay: `${0.06 * index}s` }}
              onClick={() => navigate(`/practice/${topic.slug}`)}
            >
              <span className="home-topic-icon" aria-hidden="true">{topic.icon}</span>
              <span className="home-topic-label">{topic.label}</span>
              <span className="home-topic-sub">{topic.subtitle}</span>
              <span className="home-topic-arrow" aria-hidden="true">
                <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
                  <path d="M4 9h10M10 5l4 4-4 4" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
              </span>
            </button>
          ))}
        </div>
      </section>

      <section className="home-section">
        <button
          type="button"
          className="home-search-lane"
          onClick={() => navigate('/search')}
        >
          <div className="home-search-accent" aria-hidden="true">
            <svg viewBox="0 0 200 200" fill="none" width="200" height="200">
              <circle cx="100" cy="100" r="80" stroke="var(--blue-light)" strokeWidth="1" opacity="0.5" />
              <circle cx="100" cy="100" r="50" stroke="var(--blue-light)" strokeWidth="1" opacity="0.35" />
              <line x1="20" y1="100" x2="180" y2="100" stroke="var(--peach)" strokeWidth="1" opacity="0.4" />
              <line x1="100" y1="20" x2="100" y2="180" stroke="var(--peach)" strokeWidth="1" opacity="0.4" />
              <path d="M30 170 Q100 40 170 170" stroke="var(--blue)" strokeWidth="1.5" opacity="0.25" fill="none" />
            </svg>
          </div>

          <div className="home-search-body">
            <span className="home-search-kicker">Examenbank</span>
            <span className="home-search-title">Examenopgaven zoeken</span>
            <span className="home-search-desc">
              Beschrijf een opgave en vind met AI de meest relevante examenopgaven.
            </span>
          </div>

          <span className="home-search-cta">
            Zoeken
            <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
              <path d="M4 9h10M10 5l4 4-4 4" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </span>
        </button>
      </section>
    </div>
  )
}
