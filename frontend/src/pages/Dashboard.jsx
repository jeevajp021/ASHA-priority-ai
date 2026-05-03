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
        {[
          ['🔴 High Risk', counts.RED,    'bg-red-50 border-red-200 text-red-800'],
          ['🟡 Moderate',  counts.YELLOW, 'bg-yellow-50 border-yellow-200 text-yellow-800'],
          ['🟢 Routine',   counts.GREEN,  'bg-green-50 border-green-200 text-green-800'],
        ].map(([label, val, cls]) => (
          <div key={label} className={`${cls} border rounded-xl p-4 text-center`}>
            <p className="text-3xl font-bold text-gray-800">{val}</p>
            <p className="text-sm text-gray-500 mt-1">{label}</p>
          </div>
        ))}
      </div>
      <RouteMap />
    </div>
  )
}