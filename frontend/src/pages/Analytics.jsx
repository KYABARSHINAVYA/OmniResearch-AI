import { useEffect, useState } from 'react'
import { getAnalytics } from '../api/analyticsApi'
import MetricTrendCard from '../components/MetricTrendCard'
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
        <MetricTrendCard label="Tokens" value={analytics?.token_usage} accent="green" />
        <MetricTrendCard label="Memory hits" value={analytics?.memory_hits} accent="blue" />
        <MetricTrendCard label="Tool calls" value={analytics?.tool_calls} accent="amber" />
      </section>
      <ToolCallsChart toolCalls={analytics?.tool_calls} />
    </div>
  )
}
