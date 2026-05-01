import React from 'react'
import { Routes, Route, Link } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import NewVisit from './pages/NewVisit'
import Incentives from './pages/Incentives'

export default function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-green-700 text-white px-6 py-4 flex gap-6 items-center shadow">
        <span className="font-bold text-lg">🩺 ASHA-Priority AI</span>
        <Link to="/" className="hover:underline text-sm">Dashboard</Link>
        <Link to="/visit" className="hover:underline text-sm">New Visit</Link>
        <Link to="/incentives" className="hover:underline text-sm">Incentives</Link>
        <span className="ml-auto text-xs opacity-75">ASHA ID: 1 | Block: Gondia</span>
      </nav>
      <main className="max-w-4xl mx-auto px-4 py-6">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/visit" element={<NewVisit />} />
          <Route path="/incentives" element={<Incentives />} />
        </Routes>
      </main>
    </div>
  )
}