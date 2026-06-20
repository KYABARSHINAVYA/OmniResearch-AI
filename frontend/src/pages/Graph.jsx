const nodes = [
  ['planner', 'Plan question'],
  ['research', 'Collect sources'],
  ['rag', 'Graph RAG'],
  ['memory', 'Persist memory'],
  ['writer', 'Draft answer'],
  ['reviewer', 'Review output'],
]

export default function Graph() {
  return (
    <div className="content-stack">
      <section className="panel page-intro">
        <h2>Workflow Graph</h2>
        <p>Current frontend view of the backend LangGraph-style research pipeline.</p>
      </section>
      <section className="graph-canvas" aria-label="Workflow graph">
        {nodes.map(([id, label], index) => (
          <div className="graph-step" key={id}>
            <div className="graph-node">
              <strong>{id}</strong>
              <span>{label}</span>
            </div>
            {index < nodes.length - 1 ? <div className="graph-edge" aria-hidden="true" /> : null}
          </div>
        ))}
      </section>
    </div>
  )
}
