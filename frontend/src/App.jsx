import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import './App.css'
import Navbar from './component/Navbar'
import LandingPage from './component/pages/LandingPage'
import GamePage from './component/pages/GamePage'
import AboutPage from './component/pages/AboutPage'
import PlayPage from './component/pages/PlayPage'

function App() {
  return (
    <Router>
      <div className="min-h-screen">
        <Navbar />
        <main>
          <Routes>
            <Route path="/" element={<LandingPage />} />
            <Route path="/game" element={<GamePage />} />
            <Route path="/about" element={<AboutPage />} />
            <Route path="/play" element={<PlayPage />} />
          </Routes>
        </main>
      </div>
    </Router>
  )
}

export default App
