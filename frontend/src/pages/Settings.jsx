import { useEffect, useState } from 'react'
import { API_BASE_URL } from '../api/client'
import { getArchitecture, getLlmStatus } from '../api/dashboardApi'

export default function Settings() {
  const [architecture, setArchitecture] = useState({})
  const [llm, setLlm] = useState({})

  useEffect(() => {
    getArchitecture().then(setArchitecture).catch(() => setArchitecture({}))
    getLlmStatus().then(setLlm).catch(() => setLlm({}))
  }, [])

  return (
    <div className="content-stack">
      <section className="panel settings-grid">
        <div>
          <h2>Backend</h2>
          <p>API base URL</p>
        </div>
        <code>{API_BASE_URL}</code>
      </section>
      <section className="panel settings-grid">
        <div>
          <h2>LLM Routing</h2>
          <p>GPT, Gemini, DeepSeek, and Ollama are selected by task and available keys.</p>
        </div>
        <code>{JSON.stringify(llm.available || [])}</code>
      </section>
      <section className="panel">
        <div className="panel-header">
          <div>
            <h2>Architecture</h2>
            <span>Vector + graph + memory stack</span>
          </div>
        </div>
        <div className="architecture-grid">
          {Object.entries(architecture).map(([key, value]) => (
            <div key={key} className="architecture-item">
              <strong>{key}</strong>
              <span>{value}</span>
            </div>
          ))}
        </div>
      </section>
    </div>
  )
}
