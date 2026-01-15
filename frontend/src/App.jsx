import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom'
import './App.css'
import Navbar from './component/Navbar'
import LandingPage from './component/pages/LandingPage'
import GamePage from './component/pages/GamePage'
import AboutPage from './component/pages/AboutPage'
import PlayPage from './component/pages/PlayPage'

// Layout component that conditionally renders Navbar
function Layout({ children }) {
  const location = useLocation();
  const hideNavbarPaths = ['/play']; // Add paths where navbar should be hidden
  const showNavbar = !hideNavbarPaths.includes(location.pathname);

  return (
    <div className="min-h-screen">
      {showNavbar && <Navbar />}
      <main>
        {children}
      </main>
    </div>
  );
}

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/game" element={<GamePage />} />
          <Route path="/about" element={<AboutPage />} />
          <Route path="/play" element={<PlayPage />} />
        </Routes>
      </Layout>
    </Router>
  )
}

export default App
