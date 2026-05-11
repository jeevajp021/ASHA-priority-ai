import React, { useState } from 'react'
import { Routes, Route, Link } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import NewVisit from './pages/NewVisit'
import Incentives from './pages/Incentives'
import { login, saveSession, clearSession, getToken, getWorkerName } from './api'

function LoginScreen({ onLogin }) {
  const [creds, setCreds] = useState({ username: '', password: '' })
  const [err, setErr] = useState('')
  const [loading, setLoading] = useState(false)

  const handleLogin = async () => {
    setLoading(true); setErr('')
    try {
      const res = await login(creds)
      saveSession(res.data)
      onLogin()
    } catch {
      setErr('Invalid username or password')
    }
    setLoading(false)
  }

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="bg-white rounded-2xl shadow p-8 w-full max-w-sm">
        <h1 className="text-xl font-bold text-green-700 mb-6 text-center">🩺 ASHA-Priority AI</h1>
        <label className="text-xs text-gray-500">Username</label>
        <input className="w-full border rounded-lg px-3 py-2 mb-3 text-sm mt-1"
          value={creds.username} onChange={e => setCreds({...creds, username: e.target.value})} />
        <label className="text-xs text-gray-500">Password</label>
        <input type="password" className="w-full border rounded-lg px-3 py-2 mb-4 text-sm mt-1"
          value={creds.password} onChange={e => setCreds({...creds, password: e.target.value})}
          onKeyDown={e => e.key === 'Enter' && handleLogin()} />
        {err && <p className="text-red-500 text-xs mb-3">{err}</p>}
        <button onClick={handleLogin} disabled={loading}
          className="w-full bg-green-700 text-white py-2 rounded-xl font-semibold hover:bg-green-800">
          {loading ? 'Signing in...' : 'Sign In'}
        </button>
      </div>
    </div>
  )
}

export default function App() {
  const [authed, setAuthed] = useState(!!getToken())

  if (!authed) return <LoginScreen onLogin={() => setAuthed(true)} />

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-green-700 text-white px-6 py-4 flex gap-6 items-center shadow">
        <span className="font-bold text-lg">🩺 ASHA-Priority AI</span>
        <Link to="/" className="hover:underline text-sm">Dashboard</Link>
        <Link to="/visit" className="hover:underline text-sm">New Visit</Link>
        <Link to="/incentives" className="hover:underline text-sm">Incentives</Link>
        <span className="ml-auto text-xs opacity-75 mr-3">{getWorkerName()}</span>
        <button onClick={() => { clearSession(); setAuthed(false) }}
          className="text-xs bg-green-800 hover:bg-green-900 px-3 py-1 rounded-lg">
          Sign Out
        </button>
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