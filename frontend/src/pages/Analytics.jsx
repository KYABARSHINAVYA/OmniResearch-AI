import { useEffect, useState } from 'react'
import { getAnalytics } from '../api/analyticsApi'
import ToolCallsChart from '../components/ToolCallsChart'

export default function Analytics() {
  const [analytics, setAnalytics] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    getAnalytics()
      .then(setAnalytics)
      .catch((err) => setError(err.message))
  }, [])

  return (
    <div className="content-stack">
      {error ? <p className="inline-error">Using fallback data: {error}</p> : null}
      <section className="metrics-grid">
        <div className="metric-card">
          <span>Tokens</span>
          <strong>{JSON.stringify(analytics?.token_usage || 0)}</strong>
        </div>
        <div className="metric-card">
          <span>Memory hits</span>
          <strong>{JSON.stringify(analytics?.memory_hits || 0)}</strong>
        </div>
        <div className="metric-card">
          <span>Tool calls</span>
          <strong>{JSON.stringify(analytics?.tool_calls || {})}</strong>
        </div>
      </section>
      <ToolCallsChart toolCalls={analytics?.tool_calls} />
    </div>
  )
}
