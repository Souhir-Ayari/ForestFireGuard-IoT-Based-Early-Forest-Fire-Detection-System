const CLASSES = ['risk-low', 'risk-medium', 'risk-high']

export default function RiskBadge({ level, label, large = false }) {
  return <span className={`badge ${CLASSES[level]} ${large ? 'badge-large' : ''}`}>{label}</span>
}
