export default function LogsPanel({ logs = [] }) {
  const entries = logs.length
    ? logs
    : [
        'Planner ready',
        'Research agent idle',
        'Graph retriever waiting',
        'Writer standing by',
      ]

  return (
    <section className="panel logs-panel">
      <div className="panel-header">
        <h2>Agent Logs</h2>
        <span>{entries.length} entries</span>
      </div>
      <div className="log-list">
        {entries.map((entry, index) => (
          <div className="log-row" key={`${entry}-${index}`}>
            <span>{String(index + 1).padStart(2, '0')}</span>
            <p>{typeof entry === 'string' ? entry : JSON.stringify(entry)}</p>
          </div>
        ))}
      </div>
    </section>
  )
}
