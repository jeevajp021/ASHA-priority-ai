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

export default function RouteMap() {
  const [routeData, setRouteData] = useState(null)

  useEffect(() => {
    getRoute(1).then(r => setRouteData(r.data)).catch(console.error)
  }, [])

  if (!routeData) return <div className="text-center py-10 text-gray-400">Loading route...</div>

  const positions = routeData.route.map(p => [p.lat, p.lng])
  const center = positions[0] || [21.14, 79.08]

  return (
    <div className="bg-white rounded-2xl shadow p-4">
      <h2 className="text-lg font-semibold text-gray-700 mb-3">Today's Optimised Route</h2>
      <p className="text-sm text-gray-500 mb-3">
        {routeData.total_patients} patients · Est. {routeData.estimated_minutes} min walk
      </p>
      <MapContainer center={center} zoom={13} style={{ height: '350px', borderRadius: '12px' }}>
        <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
        {routeData.route.map((p, i) => (
          <Marker key={i} position={[p.lat, p.lng]}>
            <Popup>
              <strong>{p.name}</strong><br />
              Priority: <span style={{ color: p.triage === 'RED' ? 'red' : p.triage === 'YELLOW' ? 'orange' : 'green' }}>
                {p.triage}
              </span><br />
              Stop #{i + 1}
            </Popup>
          </Marker>
        ))}
        {positions.length > 1 && <Polyline positions={positions} color="green" />}
      </MapContainer>
    </div>
  )
}