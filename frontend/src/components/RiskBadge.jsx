import React from 'react'

const config = {
  RED:    { bg: 'bg-red-100',    border: 'border-red-500',    text: 'text-red-800',    label: '🔴 HIGH RISK — Visit within 2 hrs + ANM escalation' },
  YELLOW: { bg: 'bg-yellow-100', border: 'border-yellow-500', text: 'text-yellow-800', label: '🟡 MODERATE — Visit within 48 hrs' },
  GREEN:  { bg: 'bg-green-100',  border: 'border-green-500',  text: 'text-green-800',  label: '🟢 ROUTINE — Standard tracking schedule' },
}

export default function RiskBadge({ triage, score, factors }) {
  if (!triage) return null
  const c = config[triage]
  return (
    <div className={`${c.bg} ${c.border} border-2 rounded-xl p-5 mt-4`}>
      <p className={`${c.text} text-xl font-bold`}>{c.label}</p>
      <p className="text-gray-600 mt-1 text-sm">Priority Score: <strong>{score?.toFixed(3)}</strong></p>
      {factors && (
        <ul className="mt-2 text-xs text-gray-500 list-disc list-inside">
          {factors.map((f, i) => <li key={i}>{f}</li>)}
        </ul>
      )}
    </div>
  )
}