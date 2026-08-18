import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { MathJaxContext } from 'better-react-mathjax'
import './index.css'
import App from './App'

const mathJaxConfig = {
  tex: {
    inlineMath: [['\\(', '\\)'], ['$', '$']],
    displayMath: [['\\[', '\\]'], ['$$', '$$']],
  },
  output: {
    font: 'mathjax-fira',
  },
  startup: {
    typeset: false,
  },
}

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <MathJaxContext version={4} config={mathJaxConfig}>
      <BrowserRouter>
        <App />
      </BrowserRouter>
    </MathJaxContext>
  </StrictMode>,
)
