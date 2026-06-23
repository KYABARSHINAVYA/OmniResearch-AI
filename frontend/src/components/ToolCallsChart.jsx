function normalizeTools(toolCalls) {
  if (Array.isArray(toolCalls)) {
    return toolCalls.map((item, index) => ({
      label: item?.tool || item?.name || `Tool ${index + 1}`,
      value: Number(item?.count ?? item?.value ?? item) || 0,
    }))
  }

  if (toolCalls && typeof toolCalls === 'object') {
    return Object.entries(toolCalls).map(([label, value]) => ({
      label,
      value: Number(value) || 0,
    }))
  }

  return [
    { label: 'Search', value: 12 },
    { label: 'Memory', value: 8 },
    { label: 'Graph', value: 6 },
    { label: 'Writer', value: 4 },
  ]
}

export default function ToolCallsChart({ toolCalls }) {
  const data = normalizeTools(toolCalls)
  const total = data.reduce((sum, item) => sum + item.value, 0) || 1

  return (
    <section className="panel chart-panel analytics-chart-panel">
      <div className="panel-header">
        <div>
          <h2>Tool Calls</h2>
          <p>Which tools are doing the work</p>
        </div>
        <span className="chart-total">{total} total</span>
      </div>
      <div className="tool-chart">
        {data.map((item, index) => {
          const percentage = Math.round((item.value / total) * 100)

          return (
            <div className={`tool-row tool-row-${(index % 4) + 1}`} key={item.label}>
              <div className="tool-row-heading">
                <span className="tool-rank">{index + 1}</span>
                <div>
                  <strong>{item.label}</strong>
                  <span>{item.value.toLocaleString()} calls</span>
                </div>
                <strong className="tool-percent">{percentage}%</strong>
              </div>
              <div className="bar-track">
                <div className="bar-fill tool" style={{ width: `${percentage}%` }} />
              </div>
            </div>
          )
        })}
      </div>
    </section>
  )
}
