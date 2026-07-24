interface LogoProps {
  showWordmark?: boolean
  size?: number
}

export default function Logo({ showWordmark = true, size = 32 }: LogoProps) {
  return (
    <span className="mw-logo">
      <svg
        className="mw-logo-mark"
        width={size}
        height={size}
        viewBox="0 0 100 100"
        role="img"
        aria-label="MathWizard"
      >
        <g stroke="var(--color-outline)" strokeWidth="5" strokeLinejoin="round" fill="none">
          <path d="M50 6 L92 50 L50 94 L8 50 Z" fill="var(--sky-400)" />
          <path d="M50 6 L92 50 L8 50 Z" fill="var(--sky-300)" />
          <path d="M20 50 L80 50 L68 62 L32 62 Z" fill="var(--peach-200)" />
        </g>
      </svg>
      {showWordmark && <span className="mw-logo-word">MathWizard</span>}
    </span>
  )
}
