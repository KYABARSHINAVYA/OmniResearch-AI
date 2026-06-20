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
    <section className="panel chart-panel">
      <div className="panel-header">
        <h2>Tool Calls</h2>
        <span>{total} total</span>
      </div>
      <div className="tool-chart">
        {data.map((item) => (
          <div className="tool-row" key={item.label}>
            <div>
              <strong>{item.label}</strong>
              <span>{Math.round((item.value / total) * 100)}%</span>
            </div>
            <div className="bar-track">
              <div className="bar-fill tool" style={{ width: `${(item.value / total) * 100}%` }} />
            </div>
          </div>
        ))}
      </div>
    </section>
  )
}
