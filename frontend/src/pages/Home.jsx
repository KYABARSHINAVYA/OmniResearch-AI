export default function Home({ onNavigate }) {
  return (
    <div className="page-grid">
      <section className="hero-panel">
        <div>
          <p className="eyebrow">Research workflow cockpit</p>
          <h2>Run agents, inspect progress, and keep human checkpoints visible.</h2>
          <p>
            This console connects chat, workflow state, agent health, analytics,
            approvals, and persisted checkpoints in one place.
          </p>
        </div>
        <div className="hero-actions">
          <button type="button" className="primary-button" onClick={() => onNavigate('chat')}>
            Start chat
          </button>
          <button type="button" className="ghost-button" onClick={() => onNavigate('dashboard')}>
            Open dashboard
          </button>
        </div>
      </section>

      <section className="quick-grid">
        {[
          ['Dashboard', 'Live status, latency, logs, and usage.', 'dashboard'],
          ['Analytics', 'Token, memory, and tool call trends.', 'analytics'],
          ['Approval', 'Pause and approve human-in-loop runs.', 'approval'],
          ['Graph', 'Inspect the workflow path from planner to writer.', 'graph'],
        ].map(([title, body, page]) => (
          <button type="button" className="quick-card" key={title} onClick={() => onNavigate(page)}>
            <strong>{title}</strong>
            <span>{body}</span>
          </button>
        ))}
      </section>
    </div>
  )
}
