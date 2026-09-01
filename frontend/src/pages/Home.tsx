import type { KeyboardEvent } from 'react'
import { useNavigate } from 'react-router-dom'
import { TOPICS } from '../constants/topics'
import type { UserResponse } from '../types/api'
import { Card } from '../components/ui'
import './Home.css'

interface HomeProps {
  user: UserResponse
}

export default function Home({ user }: HomeProps) {
  const navigate = useNavigate()

  const handleCardKeyDown = (event: KeyboardEvent<HTMLDivElement>, to: string) => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault()
      navigate(to)
    }
  }

  return (
    <div className="page-enter home">
      <Card band hard className="home-hero">
        <p className="home-eyebrow">Welkom terug, {user.username}</p>
        <h1 className="home-title">Waar wil je mee aan de slag?</h1>
        <p className="home-lede">
          Kies een onderwerp en oefen gericht met opgaven uit de databank.
        </p>
      </Card>

      <section className="home-section">
        <div className="home-section-head">
          <h2 className="home-section-title">Oefen onderwerpen</h2>
          <p className="home-section-sub">Kies een onderwerp om gericht te oefenen</p>
        </div>

        <div className="home-topic-grid">
          {TOPICS.map((topic, index) => (
            <Card
              key={topic.slug}
              role="button"
              tabIndex={0}
              className="home-topic-card"
              style={{ animationDelay: `${0.06 * index}s` }}
              onClick={() => navigate(`/practice/${topic.slug}`)}
              onKeyDown={event => handleCardKeyDown(event, `/practice/${topic.slug}`)}
            >
              <span className="home-topic-icon" aria-hidden="true">{topic.icon}</span>
              <span className="home-topic-label">{topic.label}</span>
              <span className="home-topic-sub">{topic.subtitle}</span>
              <span className="home-topic-arrow" aria-hidden="true">
                <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
                  <path d="M4 9h10M10 5l4 4-4 4" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
              </span>
            </Card>
          ))}
        </div>
      </section>
    </div>
  )
}
