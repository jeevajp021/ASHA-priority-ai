import axios from 'axios'

const BASE = '/api'

// ── Token helpers ──────────────────────────────────────────
export const saveSession = (data) => {
  sessionStorage.setItem('asha_token', data.access_token)
  sessionStorage.setItem('asha_role', data.role)
  sessionStorage.setItem('asha_name', data.worker_name)
  sessionStorage.setItem('asha_id', data.worker_id)
}
export const clearSession = () => sessionStorage.clear()
export const getToken = () => sessionStorage.getItem('asha_token')
export const getRole = () => sessionStorage.getItem('asha_role')
export const getWorkerName = () => sessionStorage.getItem('asha_name')

const authHeader = () => ({ headers: { 'x-auth-token': getToken() } })

// ── Auth ───────────────────────────────────────────────────
export const login = (data) => axios.post(`${BASE}/login`, data)

// ── Patients ───────────────────────────────────────────────
export const getPatients = (filters = {}) => {
  const params = new URLSearchParams()
  if (filters.triage) params.append('triage', filters.triage)
  if (filters.record_status) params.append('record_status', filters.record_status)
  return axios.get(`${BASE}/patients?${params.toString()}`, authHeader())
}
export const createPatient = (data) => axios.post(`${BASE}/patients`, data, authHeader())
export const updatePatientStatus = (patientId, status) =>
  axios.patch(`${BASE}/patients/${patientId}/status?record_status=${status}`, {}, authHeader())

// ── Clinical ───────────────────────────────────────────────
export const predictRisk = (patientId) =>
  axios.post(`${BASE}/predict`, { patient_id: patientId }, authHeader())
export const getRoute = (ashaId) => axios.get(`${BASE}/route/${ashaId}`, authHeader())
export const getIncentives = (ashaId) => axios.get(`${BASE}/incentives/${ashaId}`, authHeader())
export const logVisit = (data) => axios.post(`${BASE}/visits`, data, authHeader())