import React, { useState } from 'react'
import { createPatient, predictRisk, logVisit } from '../api'
import RiskBadge from './RiskBadge'

const FIELD = (label, name, type='number', placeholder='') => ({ label, name, type, placeholder })
const FIELDS = [
  FIELD('Age (years)', 'age'),
  FIELD('Gestational Age (weeks)', 'gestational_age'),
  FIELD('Systolic BP (mmHg)', 'bp_systolic'),
  FIELD('Diastolic BP (mmHg)', 'bp_diastolic'),
  FIELD('Haemoglobin (g/dL)', 'haemoglobin'),
  FIELD('Previous High-Risk Pregnancies', 'prev_hrp'),
  FIELD('Latitude', 'lat', 'number', '21.1458'),
  FIELD('Longitude', 'lng', 'number', '79.0882'),
]

export default function PatientForm() {
  const [form, setForm] = useState({})
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [name, setName] = useState('')

  const handleChange = (e) => setForm({ ...form, [e.target.name]: parseFloat(e.target.value) })

  const handleSubmit = async () => {
    setLoading(true)
    try {
      const patient = await createPatient({ name, asha_id: 1, ...form })
      const pid = patient.data.id
      await logVisit({ patient_id: pid, asha_id: 1, lat: form.lat, lng: form.lng })
      const risk = await predictRisk(pid)
      setResult(risk.data)
    } catch (err) {
      alert('Error: ' + (err.response?.data?.detail || err.message))
    }
    setLoading(false)
  }

  return (
    <div className="bg-white rounded-2xl shadow p-6">
      <h2 className="text-lg font-semibold text-gray-700 mb-4">New Patient Visit</h2>
      <div className="mb-3">
        <label className="text-sm text-gray-600">Patient Name</label>
        <input className="w-full border rounded-lg px-3 py-2 mt-1 text-sm" value={name}
          onChange={e => setName(e.target.value)} placeholder="Meena Devi" />
      </div>
      <div className="grid grid-cols-2 gap-3">
        {FIELDS.map(f => (
          <div key={f.name}>
            <label className="text-xs text-gray-500">{f.label}</label>
            <input name={f.name} type={f.type} placeholder={f.placeholder}
              className="w-full border rounded-lg px-3 py-2 text-sm mt-1"
              onChange={handleChange} />
          </div>
        ))}
      </div>
      <button onClick={handleSubmit} disabled={loading}
        className="mt-5 w-full bg-green-700 hover:bg-green-800 text-white font-semibold py-3 rounded-xl transition">
        {loading ? 'Analysing...' : 'Assess Risk & Log Visit'}
      </button>
      {result && <RiskBadge triage={result.triage} score={result.priority_score} factors={result.risk_factors} />}
    </div>
  )
}