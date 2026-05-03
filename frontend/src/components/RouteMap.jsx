import React, { useEffect, useState } from 'react'
import { MapContainer, TileLayer, Marker, Polyline, Popup } from 'react-leaflet'
import { getRoute } from '../api'
import 'leaflet/dist/leaflet.css'
import L from 'leaflet'

// Fix Leaflet default icon
delete L.Icon.Default.prototype._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
})

// Inline SVG pin: numbered with triage colour
const makeStopIcon = (index, triage) => {
  const fill = triage === 'RED' ? '#ef4444' : triage === 'YELLOW' ? '#f59e0b' : '#22c55e'
  const label = index === 0 ? 'S' : String(index)
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="28" height="36" viewBox="0 0 28 36">
    <path d="M14 0C6.27 0 0 6.27 0 14c0 9.33 14 22 14 22S28 23.33 28 14C28 6.27 21.73 0 14 0z" fill="${fill}"/>
    <circle cx="14" cy="14" r="9" fill="white"/>
    <text x="14" y="19" text-anchor="middle" font-size="10" font-weight="bold" fill="${fill}" font-family="sans-serif">${label}</text>
  </svg>`
  return L.divIcon({
    html: svg,
    className: '',
    iconSize: [28, 36],
    iconAnchor: [14, 36],
    popupAnchor: [0, -36],
  })
}

export default function RouteMap() {
  const [routeData, setRouteData] = useState(null)

  useEffect(() => {
    getRoute(1).then(r => setRouteData(r.data)).catch(console.error)
  }, [])

  if (!routeData) return <div className="text-center py-10 text-gray-400">Loading route...</div>

  const positions = routeData.route.map(p => [p.lat, p.lng])
  const center = positions[0] || [21.14, 79.08]
  const last = routeData.route.length - 1

  return (
    <div className="bg-white rounded-2xl shadow p-4">
      <h2 className="text-lg font-semibold text-gray-700 mb-3">Today's Optimised Route</h2>
      <p className="text-sm text-gray-500 mb-3">
        {routeData.total_patients} patients · Est. {routeData.estimated_minutes} min walk
      </p>
      {/* Legend */}
      <div className="flex gap-4 text-xs text-gray-500 mb-2">
        <span><span style={{color:'#ef4444'}}>●</span> RED – urgent</span>
        <span><span style={{color:'#f59e0b'}}>●</span> YELLOW – moderate</span>
        <span><span style={{color:'#22c55e'}}>●</span> GREEN – routine</span>
        <span className="ml-auto font-medium">S = Start · numbers = visit order</span>
      </div>
      <MapContainer center={center} zoom={13} style={{ height: '350px', borderRadius: '12px' }}>
        <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
        {routeData.route.map((p, i) => (
          <Marker key={i} position={[p.lat, p.lng]} icon={makeStopIcon(i, p.triage)}>
            <Popup>
              <strong>{i === 0 ? '🟢 START — ' : ''}{p.name}</strong><br />
              Stop #{i + 1} of {routeData.total_patients}<br />
              Triage: <span style={{ color: p.triage === 'RED' ? 'red' : p.triage === 'YELLOW' ? 'orange' : 'green', fontWeight: 'bold' }}>
                {p.triage}
              </span><br />
              Score: {p.priority_score?.toFixed(3)}
              {i === last ? <><br/><em>🏁 Final stop</em></> : null}
            </Popup>
          </Marker>
        ))}
        {positions.length > 1 && (
          <Polyline positions={positions} color="#3b82f6" weight={3} dashArray="6 4" />
        )}
      </MapContainer>
    </div>
  )
}