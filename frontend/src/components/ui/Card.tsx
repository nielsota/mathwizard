import './Card.css'

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  band?: boolean
  hard?: boolean
}

export default function Card({ band = false, hard = false, className = '', children, ...rest }: CardProps) {
  return (
    <div className={`ui-card ${hard ? 'ui-card--hard' : ''} ${className}`} {...rest}>
      {band && <div className="ui-card__band" />}
      {children}
    </div>
  )
}
