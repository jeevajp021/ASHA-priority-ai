import axios from 'axios'

const BASE = '/api'

export const getPatients = () => axios.get(`${BASE}/patients`)
export const createPatient = (data) => axios.post(`${BASE}/patients`, data)
export const predictRisk = (patientId) => axios.post(`${BASE}/predict`, { patient_id: patientId })
export const getRoute = (ashaId) => axios.get(`${BASE}/route/${ashaId}`)
export const getIncentives = (ashaId) => axios.get(`${BASE}/incentives/${ashaId}`)
export const logVisit = (data) => axios.post(`${BASE}/visits`, data)