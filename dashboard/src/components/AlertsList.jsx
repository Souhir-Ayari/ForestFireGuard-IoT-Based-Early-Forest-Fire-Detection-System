import RiskBadge from './RiskBadge'

export default function AlertsList({ alerts }) {
  if (alerts.length === 0) return <p className="empty">Aucune alerte ✅</p>

  return (
    <ul className="alerts">
      {alerts.map((a) => (
        <li key={a.id} className="alert">
          <div className="alert-head">
            <RiskBadge level={a.level} label={a.label} />
            <span className="muted">{new Date(a.timestamp).toLocaleTimeString('fr-FR')} · {a.device_id}</span>
          </div>
          <p>{a.message}</p>
        </li>
      ))}
    </ul>
  )
}
