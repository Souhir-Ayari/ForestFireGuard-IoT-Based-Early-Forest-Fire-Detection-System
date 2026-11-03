export default function StatCard({ label, value, unit }) {
  return (
    <div className="card">
      <span className="card-label">{label}</span>
      <span className="card-value">
        {value ?? '—'}
        {value != null && <small> {unit}</small>}
      </span>
    </div>
  )
}
