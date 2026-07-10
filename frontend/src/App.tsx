import { Routes, Route } from 'react-router-dom'
import Header from './components/Header'
import ExamSearch from './pages/ExamSearch'
import Practice from './pages/Practice'
import './App.css'

function App() {
  return (
    <>
      <Header />
      <main>
        <Routes>
          <Route path="/" element={<ExamSearch />} />
          <Route path="/practice/:topic" element={<Practice />} />
        </Routes>
      </main>
    </>
  )
}

export default App
