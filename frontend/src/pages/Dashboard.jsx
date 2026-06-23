import { useEffect, useState } from 'react'
import { getDashboard } from '../api/dashboardApi'
import HealthDonut from '../components/HealthDonut'
import LatencyChart from '../components/LatencyChart'
import LiveExecutionGraph from '../components/LiveExecutionGraph'
import LogsPanel from '../components/LogsPanel'
import MetricTrendCard from '../components/MetricTrendCard'
import ToolCallsChart from '../components/ToolCallsChart'

const fallbackAgents = {
  planner: 'idle',
  research: 'idle',
  rag: 'idle',
  memory: 'idle',
  graph: 'idle',
  mcp: 'idle',
  writer: 'idle',
  reviewer: 'idle',
  evaluator: 'idle',
}

export default function Dashboard() {
  const [dashboard, setDashboard] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    getDashboard()
      .then(setDashboard)
      .catch((err) => setError(err.message))
  }, [])

  const agents = dashboard?.agent_status || fallbackAgents

  return (
    <div className="content-stack">
      {error ? <p className="inline-error">Using fallback data: {error}</p> : null}
      <section className="metrics-grid">
        <MetricTrendCard label="Token usage" value={dashboard?.token_usage} accent="green" />
        <MetricTrendCard label="Memory hits" value={dashboard?.memory_hits} accent="blue" />
        <MetricTrendCard label="Tool calls" value={dashboard?.tool_calls} accent="amber" />
        <div className="metric-card signal-card">
          <span>Monitoring</span>
          <strong>Prometheus</strong>
          <small>Live metrics ready</small>
        </div>
      </section>

      <section className="dashboard-hero-grid">
        <LiveExecutionGraph agents={agents} />
        <HealthDonut agents={agents} />
      </section>

      <section className="two-column">
        <LatencyChart latencies={dashboard?.latencies} />
        <ToolCallsChart toolCalls={dashboard?.tool_calls} />
      </section>

      <LogsPanel logs={dashboard?.logs} />
    </div>
  )
}
