import { useState } from 'react'
import { approveWorkflow, requestPause } from '../api/dashboardApi'

export default function Approval() {
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')

  const runAction = async (action) => {
    setError('')
    try {
      setResult(await action())
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <div className="content-stack">
      <section className="panel approval-panel">
        <div>
          <h2>Human Approval</h2>
          <p>Pause the workflow for review or approve the pending checkpoint.</p>
        </div>
        <div className="button-row">
          <button type="button" className="ghost-button" onClick={() => runAction(requestPause)}>
            Pause
          </button>
          <button type="button" className="primary-button" onClick={() => runAction(approveWorkflow)}>
            Approve
          </button>
        </div>
      </section>
      {error ? <p className="inline-error">{error}</p> : null}
      <section className="panel">
        <div className="panel-header">
          <h2>Approval Response</h2>
          <span>{result ? 'Updated' : 'No action yet'}</span>
        </div>
        <pre className="code-block">{JSON.stringify(result || {}, null, 2)}</pre>
      </section>
    </div>
  )
}
