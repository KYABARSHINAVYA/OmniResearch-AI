function normalizeLatency(latencies) {
  if (Array.isArray(latencies)) {
    return latencies.map((value, index) => ({
      label: `Run ${index + 1}`,
      value: Number(value?.value ?? value?.latency ?? value) || 0,
    }))
  }

  if (latencies && typeof latencies === 'object') {
    return Object.entries(latencies).map(([label, value]) => ({
      label,
      value: Number(value) || 0,
    }))
  }

  return [
    { label: 'Plan', value: 220 },
    { label: 'Research', value: 540 },
    { label: 'RAG', value: 410 },
    { label: 'Write', value: 310 },
  ]
}

export default function LatencyChart({ latencies }) {
  const data = normalizeLatency(latencies)
  const max = Math.max(...data.map((item) => item.value), 1)

  return (
    <section className="panel chart-panel">
      <div className="panel-header">
        <h2>Latency</h2>
        <span>ms</span>
      </div>
      <div className="bar-chart">
        {data.map((item) => (
          <div className="bar-row" key={item.label}>
            <span>{item.label}</span>
            <div className="bar-track">
              <div className="bar-fill latency" style={{ width: `${(item.value / max) * 100}%` }} />
            </div>
            <strong>{item.value}</strong>
          </div>
        ))}
      </div>
    </section>
  )
}
