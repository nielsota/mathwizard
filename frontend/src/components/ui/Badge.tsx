import './Badge.css'

interface BadgeProps {
  tone?: 'easy' | 'med' | 'hard' | 'neutral'
  children: React.ReactNode
}

export default function Badge({ tone = 'neutral', children }: BadgeProps) {
  return <span className={`ui-badge ui-badge--${tone}`}>{children}</span>
}
