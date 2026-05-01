import React, { useEffect, useState } from 'react'
import { getPatients } from '../api'
import RouteMap from '../components/RouteMap'

export default function Dashboard() {
  const [patients, setPatients] = useState([])

  useEffect(() => { getPatients().then(r => setPatients(r.data)) }, [])

  const counts = { RED: 0, YELLOW: 0, GREEN: 0 }
  patients.forEach(p => { if (p.triage) counts[p.triage]++ })

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-800">Good morning, Sunita 👋</h1>
      <div className="grid grid-cols-3 gap-4">
        {[['🔴 High Risk', counts.RED, 'red'], ['🟡 Moderate', counts.YELLOW, 'yellow'], ['🟢 Routine', counts.GREEN, 'green']].map(([label, val, color]) => (
          <div key={label} className={`bg-${color}-50 border border-${color}-200 rounded-xl p-4 text-center`}>
            <p className="text-3xl font-bold text-gray-800">{val}</p>
            <p className="text-sm text-gray-500 mt-1">{label}</p>
          </div>
        ))}
      </div>
      <RouteMap />
    </div>
  )
}