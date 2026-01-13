import { useState } from 'react'
import './App.css'
import Navbar from './component/Navbar'
import Homepage from './component/Homepage'

function App() {
  const [count, setCount] = useState(0)

  return (
    <>
      <div className="container mx-auto">
        <Homepage />
      </div>
    </>
  )
}

export default App
