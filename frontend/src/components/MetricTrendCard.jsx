function normalizeValue(value) {
  if (Array.isArray(value)) {
    return value.reduce((sum, item) => sum + (Number(item?.value ?? item?.count ?? item) || 0), 0)
  }

  if (value && typeof value === 'object') {
    return Object.values(value).reduce((sum, item) => sum + (Number(item) || 0), 0)
  }

  return Number(value) || 0
}

function makeTrend(total) {
  const base = Math.max(total, 1)
  return [0.35, 0.48, 0.42, 0.62, 0.58, 0.75, 0.9].map((ratio) => Math.max(4, Math.round(base * ratio)))
}

export default function MetricTrendCard({ label, value, accent = 'green' }) {
  const total = normalizeValue(value)
  const trend = makeTrend(total)
  const max = Math.max(...trend, 1)
  const points = trend
    .map((item, index) => {
      const x = (index / (trend.length - 1)) * 100
      const y = 42 - (item / max) * 34
      return `${x},${y}`
    })
    .join(' ')

  return (
    <div className={`metric-card trend-card ${accent}`}>
      <span>{label}</span>
      <strong>{total.toLocaleString()}</strong>
      <svg viewBox="0 0 100 46" role="img" aria-label={`${label} trend`}>
        <polyline points={points} fill="none" stroke="currentColor" strokeWidth="4" />
      </svg>
    </div>
  )
}
