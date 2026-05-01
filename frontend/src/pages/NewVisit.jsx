import React from 'react'
import PatientForm from '../components/PatientForm'

export default function NewVisit() {
  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-800 mb-4">Log Patient Visit</h1>
      <PatientForm />
    </div>
  )
}