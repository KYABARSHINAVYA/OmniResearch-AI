const statusLabels = {
  running: 'Running',
  completed: 'Completed',
  failed: 'Failed',
  idle: 'Idle',
}

export default function AgentStatusCard({ agent, status = 'idle', detail }) {
  return (
    <article className="agent-card">
      <div>
        <h3>{agent}</h3>
        <p>{detail || 'Waiting for workflow signal'}</p>
      </div>
      <span className={`status-pill ${status}`}>{statusLabels[status] || status}</span>
    </article>
  )
}
