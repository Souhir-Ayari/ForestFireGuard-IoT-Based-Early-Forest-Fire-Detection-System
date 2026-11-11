import { useEffect, useState } from 'react'
import { fetchAlerts, fetchHealth, fetchMeasurements } from './api'
import StatCard from './components/StatCard'
import RiskBadge from './components/RiskBadge'
import MeasurementsChart from './components/MeasurementsChart'
import AlertsList from './components/AlertsList'
import HistoryTable from './components/HistoryTable'

const REFRESH_MS = 2000

export default function App() {
  const [health, setHealth] = useState(null)
  const [measurements, setMeasurements] = useState([])
  const [alerts, setAlerts] = useState([])
  const [error, setError] = useState(null)

  useEffect(() => {
    let active = true
    async function refresh() {
      try {
        const [h, m, a] = await Promise.all([fetchHealth(), fetchMeasurements(), fetchAlerts()])
        if (!active) return
        setHealth(h)
        setMeasurements(m)
        setAlerts(a)
        setError(null)
      } catch (e) {
        if (active) setError(`Serveur injoignable (${e.message})`)
      }
    }
    refresh()
    const id = setInterval(refresh, REFRESH_MS)
    return () => {
      active = false
      clearInterval(id)
    }
  }, [])

  const latest = measurements[0]

  return (
    <div className="app">
      <header className="header">
        <div>
          <h1>🌲 ForestFireGuard</h1>
          <p className="subtitle">Détection précoce des incendies de forêt — IoT &amp; IA</p>
        </div>
        <div className="status">
          {error ? (
            <span className="pill pill-error">{error}</span>
          ) : health ? (
            <>
              <span className="pill">API ✓</span>
              <span className={`pill ${health.mqtt.connected ? '' : 'pill-warn'}`}>
                MQTT {health.mqtt.connected ? '✓' : '✗'}
              </span>
              <span className="pill">BD : {health.storage}</span>
              <span className={`pill ${health.ai_model_loaded ? '' : 'pill-warn'}`}>
                IA {health.ai_model_loaded ? '✓' : '✗'}
              </span>
            </>
          ) : (
            <span className="pill">Connexion…</span>
          )}
        </div>
      </header>

      <section className="cards">
        <StatCard label="Température" value={latest?.temperature} unit="°C" />
        <StatCard label="Humidité" value={latest?.humidity} unit="%" />
        <StatCard label="Fumée / gaz" value={latest?.smoke} unit="%" />
        <div className="card">
          <span className="card-label">Flamme</span>
          {latest ? (
            <span className={`badge badge-flame ${latest.flame ? 'risk-high' : 'risk-low'}`}>
              {latest.flame ? '🔥 détectée' : 'aucune'}
            </span>
          ) : (
            <span className="card-value">—</span>
          )}
        </div>
        <div className="card">
          <span className="card-label">Niveau de risque</span>
          {latest ? <RiskBadge level={latest.risk.level} label={latest.risk.label} large /> : <span className="card-value">—</span>}
          {latest?.risk.reasons.length > 0 && (
            <span className="card-hint">{latest.risk.reasons.join(' · ')}</span>
          )}
        </div>
      </section>

      <section className="grid">
        <div className="panel panel-wide">
          <h2>Évolution des mesures</h2>
          <MeasurementsChart measurements={measurements} />
        </div>
        <div className="panel">
          <h2>Alertes</h2>
          <AlertsList alerts={alerts} />
        </div>
      </section>

      <section className="panel">
        <h2>Historique</h2>
        <HistoryTable measurements={measurements.slice(0, 15)} />
      </section>

      <footer className="footer">
        {latest ? `Dernière mesure : ${new Date(latest.timestamp).toLocaleString('fr-FR')} (${latest.device_id})` : 'En attente de mesures…'}
      </footer>
    </div>
  )
}
