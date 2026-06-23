const pageTitles = {
  home: 'Mission Control',
  chat: 'Research Chat',
  dashboard: 'Live Dashboard',
  analytics: 'Analytics',
  checkpoints: 'Checkpoints',
  approval: 'Human Approval',
  graph: 'Workflow Graph',
  settings: 'Settings',
}

export default function Navbar({ activePage, onNavigate, onLogout }) {
  return (
    <header className="topbar">
      <div>
        <p className="eyebrow">OmniResearch AI</p>
        <h1>{pageTitles[activePage] || 'Mission Control'}</h1>
      </div>
      <div className="topbar-actions">
        <button type="button" className="ghost-button" onClick={() => onNavigate('analytics')}>
          Metrics
        </button>
        <button type="button" className="primary-button" onClick={() => onNavigate('chat')}>
          New research
        </button>
        <button type="button" className="ghost-button quiet-button" onClick={onLogout}>
          Logout
        </button>
      </div>
    </header>
  )
}
