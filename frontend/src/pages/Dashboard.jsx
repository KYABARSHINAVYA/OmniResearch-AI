import { useEffect, useState } from 'react'
import { getDashboard } from '../api/dashboardApi'
import AgentStatusCard from '../components/AgentStatusCard'
import LatencyChart from '../components/LatencyChart'
import LogsPanel from '../components/LogsPanel'
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
        <div className="metric-card">
          <span>Token usage</span>
          <strong>{JSON.stringify(dashboard?.token_usage || 0)}</strong>
        </div>
        <div className="metric-card">
          <span>Memory hits</span>
          <strong>{JSON.stringify(dashboard?.memory_hits || 0)}</strong>
        </div>
        <div className="metric-card">
          <span>Monitoring</span>
          <strong>Prometheus</strong>
        </div>
        <div className="metric-card">
          <span>Tool families</span>
          <strong>{Object.keys(dashboard?.tool_calls || {}).length || 4}</strong>
        </div>
      </section>

      <section className="agent-grid">
        {Object.entries(agents).map(([agent, status]) => (
          <AgentStatusCard key={agent} agent={agent} status={String(status)} />
        ))}
      </section>

      <section className="two-column">
        <LatencyChart latencies={dashboard?.latencies} />
        <ToolCallsChart toolCalls={dashboard?.tool_calls} />
      </section>

      <LogsPanel logs={dashboard?.logs} />
    </div>
  )
}
