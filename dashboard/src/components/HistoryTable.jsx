import RiskBadge from './RiskBadge'

export default function HistoryTable({ measurements }) {
  if (measurements.length === 0) return <p className="empty">Aucune mesure.</p>

  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Heure</th>
            <th>Capteur</th>
            <th>Temp. (°C)</th>
            <th>Humidité (%)</th>
            <th>Fumée (%)</th>
            <th>Risque</th>
          </tr>
        </thead>
        <tbody>
          {measurements.map((m) => (
            <tr key={m.id}>
              <td>{new Date(m.timestamp).toLocaleTimeString('fr-FR')}</td>
              <td>{m.device_id}</td>
              <td>{m.temperature}</td>
              <td>{m.humidity}</td>
              <td>{m.smoke}</td>
              <td><RiskBadge level={m.risk.level} label={m.risk.label} /></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
