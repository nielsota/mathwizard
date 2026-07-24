import './Input.css'

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string
}

export default function Input({ label, className = '', id, ...rest }: InputProps) {
  return (
    <div className="ui-field">
      {label && <label className="ui-field__label" htmlFor={id}>{label}</label>}
      <input id={id} className={`ui-input ${className}`} {...rest} />
    </div>
  )
}
