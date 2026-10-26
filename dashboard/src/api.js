const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

async function get(path) {
  const res = await fetch(`${API_URL}${path}`)
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`)
  return res.json()
}

export const fetchHealth = () => get('/api/health')
export const fetchMeasurements = (limit = 60) => get(`/api/measurements?limit=${limit}`)
export const fetchAlerts = (limit = 20) => get(`/api/alerts?limit=${limit}`)
