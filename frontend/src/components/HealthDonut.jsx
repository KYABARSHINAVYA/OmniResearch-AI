function countStatuses(agents = {}) {
  return Object.values(agents).reduce(
    (counts, status) => {
      const normalized = String(status || '').toLowerCase()

      if (normalized.includes('run')) counts.running += 1
      else if (normalized.includes('complete') || normalized.includes('success')) counts.completed += 1
      else if (normalized.includes('fail') || normalized.includes('error')) counts.failed += 1
      else counts.idle += 1

      return counts
    },
    { running: 0, completed: 0, failed: 0, idle: 0 },
  )
}

export default function HealthDonut({ agents = {} }) {
  const counts = countStatuses(agents)
  const total = Object.values(counts).reduce((sum, value) => sum + value, 0) || 1
  const running = Math.round((counts.running / total) * 100)
  const completed = Math.round((counts.completed / total) * 100)
  const failed = Math.round((counts.failed / total) * 100)

  return (
    <section className="panel health-panel">
      <div className="panel-header">
        <div>
          <h2>Agent Health</h2>
          <span>{total} agents tracked</span>
        </div>
      </div>

      <div className="health-summary">
        <div
          className="donut-chart"
          style={{
            '--running': `${running}%`,
            '--completed': `${running + completed}%`,
            '--failed': `${running + completed + failed}%`,
          }}
          aria-label={`${running}% running agents`}
        >
          <strong>{running}%</strong>
          <span>Running</span>
        </div>

        <div className="legend-list">
          <span className="legend-item running">Running {counts.running}</span>
          <span className="legend-item completed">Completed {counts.completed}</span>
          <span className="legend-item failed">Failed {counts.failed}</span>
          <span className="legend-item idle">Idle {counts.idle}</span>
        </div>
      </div>
    </section>
  )
}
