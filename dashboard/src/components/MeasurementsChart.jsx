import { CartesianGrid, Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'

const time = (iso) => new Date(iso).toLocaleTimeString('fr-FR')

export default function MeasurementsChart({ measurements }) {
  // L'API renvoie le plus récent en premier : on remet dans l'ordre chronologique
  const data = [...measurements].reverse().map((m) => ({ ...m, time: time(m.timestamp) }))

  if (data.length === 0) return <p className="empty">Aucune donnée pour le moment.</p>

  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={data} margin={{ top: 8, right: 16, bottom: 0, left: -8 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="var(--grid)" />
        <XAxis dataKey="time" tick={{ fontSize: 12 }} minTickGap={24} />
        <YAxis domain={[0, 100]} tick={{ fontSize: 12 }} />
        <Tooltip />
        <Legend />
        <Line type="monotone" dataKey="temperature" name="Température (°C)" stroke="#e8590c" dot={false} strokeWidth={2} isAnimationActive={false} />
        <Line type="monotone" dataKey="humidity" name="Humidité (%)" stroke="#1c7ed6" dot={false} strokeWidth={2} isAnimationActive={false} />
        <Line type="monotone" dataKey="smoke" name="Fumée (%)" stroke="#868e96" dot={false} strokeWidth={2} isAnimationActive={false} />
      </LineChart>
    </ResponsiveContainer>
  )
}
