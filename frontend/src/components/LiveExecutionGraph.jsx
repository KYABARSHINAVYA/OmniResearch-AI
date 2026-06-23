const executionSteps = [
  ['planner', 'Plan', 'Break down the request'],
  ['research', 'Search', 'Collect source material'],
  ['rag', 'Retrieve', 'Find document context'],
  ['graph', 'Connect', 'Map relationships'],
  ['writer', 'Write', 'Draft the response'],
  ['reviewer', 'Review', 'Check quality'],
]

function normalizeStatus(status) {
  const value = String(status || 'idle').toLowerCase()

  if (value.includes('run')) return 'running'
  if (value.includes('complete') || value.includes('success')) return 'completed'
  if (value.includes('fail') || value.includes('error')) return 'failed'
  return 'idle'
}

export default function LiveExecutionGraph({ agents = {} }) {
  const activeIndex = executionSteps.findIndex(([key]) => normalizeStatus(agents[key]) === 'running')
  const currentIndex = activeIndex >= 0 ? activeIndex : 0

  return (
    <section className="panel live-execution-panel">
      <div className="panel-header">
        <div>
          <h2>Live Execution</h2>
          <span>Current agent path from planning to reviewed output</span>
        </div>
      </div>

      <div className="execution-graph" aria-label="Live execution graph">
        {executionSteps.map(([key, label, detail], index) => {
          const status = normalizeStatus(agents[key])
          const isCurrent = index === currentIndex && status === 'idle'
          const state = isCurrent ? 'queued' : status

          return (
            <div className={`execution-node ${state}`} key={key}>
              <span className="execution-dot" />
              <strong>{label}</strong>
              <small>{detail}</small>
            </div>
          )
        })}
      </div>
    </section>
  )
}
