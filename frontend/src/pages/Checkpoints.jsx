import { useEffect, useState } from 'react'
import { getCheckpoint } from '../api/dashboardApi'

export default function Checkpoints() {
  const [checkpoint, setCheckpoint] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    getCheckpoint()
      .then(setCheckpoint)
      .catch((err) => setError(err.message))
  }, [])

  return (
    <div className="content-stack">
      {error ? <p className="inline-error">Checkpoint endpoint unavailable: {error}</p> : null}
      <section className="panel">
        <div className="panel-header">
          <h2>Latest Checkpoint</h2>
          <span>{checkpoint ? 'Loaded' : 'Waiting'}</span>
        </div>
        <pre className="code-block">
          {JSON.stringify(
            checkpoint || {
              status: 'No checkpoint loaded',
              file: 'backend/checkpoint.json',
            },
            null,
            2,
          )}
        </pre>
      </section>
    </div>
  )
}
