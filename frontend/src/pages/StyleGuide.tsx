import { Button, Card, Input, Badge } from '../components/ui'
import Logo from '../components/Logo'
import './StyleGuide.css'

export default function StyleGuide() {
  return (
    <div className="styleguide page-enter">
      <header className="styleguide__hero">
        <Logo size={72} />
      </header>

      <section>
        <h2>Buttons</h2>
        <div className="styleguide__row">
          <Button variant="primary">Start oefening</Button>
          <Button variant="secondary">Bekijk uitleg</Button>
          <Button variant="ghost">Later</Button>
          <Button variant="primary" disabled>Uitgeschakeld</Button>
        </div>
      </section>

      <section>
        <h2>Badges</h2>
        <div className="styleguide__row">
          <Badge tone="easy">Makkelijk</Badge>
          <Badge tone="med">Gemiddeld</Badge>
          <Badge tone="hard">Moeilijk</Badge>
          <Badge tone="neutral">Nieuw</Badge>
        </div>
      </section>

      <section>
        <h2>Cards & inputs</h2>
        <div className="styleguide__grid">
          <Card band hard>
            <h3>Afgeleiden</h3>
            <p>Signature card: ink outline, peach band, hard shadow.</p>
            <Button variant="primary">Start</Button>
          </Card>
          <Card>
            <Input label="Onderwerp" placeholder="bv. afgeleiden…" />
            <div style={{ height: 'var(--space-4)' }} />
            <Button variant="primary" fullWidth>Zoeken</Button>
          </Card>
        </div>
      </section>
    </div>
  )
}
