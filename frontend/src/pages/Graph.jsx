const parallelAgents = [
  ['research', 'Collect sources'],
  ['rag', 'Retrieve documents'],
  ['memory', 'Recall memory'],
  ['graph', 'Query knowledge graph'],
  ['mcp', 'Call MCP tools'],
]

const WorkflowNode = ({ id, label, variant }) => (
  <div className={`graph-node ${variant || ''}`}>
    <strong>{id}</strong>
    <span>{label}</span>
  </div>
)

export default function Graph() {
  return (
    <div className="content-stack">
      <section className="panel page-intro">
        <h2>Workflow Graph</h2>
        <p>Planner fans out independent agents in parallel before Writer and Reviewer.</p>
      </section>
      <section className="graph-canvas" aria-label="Workflow graph">
        <div className="graph-flow">
          <WorkflowNode id="planner" label="Plan question" variant="primary" />
          <div className="graph-edge down" aria-hidden="true" />
          <div className="parallel-stage">
            {parallelAgents.map(([id, label]) => (
              <WorkflowNode id={id} label={label} variant="parallel" key={id} />
            ))}
          </div>
          <div className="graph-edge down" aria-hidden="true" />
          <WorkflowNode id="writer" label="Draft answer from merged context" variant="primary" />
          <div className="graph-edge down" aria-hidden="true" />
          <WorkflowNode id="reviewer" label="Review output" variant="primary" />
        </div>
      </section>
    </div>
  )
}
