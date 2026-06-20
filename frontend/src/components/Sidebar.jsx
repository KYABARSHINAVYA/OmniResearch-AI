const navItems = [
  { id: 'home', label: 'Home', icon: 'H' },
  { id: 'chat', label: 'Chat', icon: 'C' },
  { id: 'dashboard', label: 'Dashboard', icon: 'D' },
  { id: 'analytics', label: 'Analytics', icon: 'A' },
  { id: 'checkpoints', label: 'Checkpoints', icon: 'K' },
  { id: 'approval', label: 'Approval', icon: 'P' },
  { id: 'graph', label: 'Graph', icon: 'G' },
  { id: 'settings', label: 'Settings', icon: 'S' },
]

export default function Sidebar({ activePage, onNavigate }) {
  return (
    <aside className="sidebar">
      <div className="brand">
        <div className="brand-mark">OR</div>
        <div>
          <strong>OmniResearch</strong>
          <span>Agent Console</span>
        </div>
      </div>

      <nav className="side-nav" aria-label="Primary">
        {navItems.map((item) => (
          <button
            key={item.id}
            type="button"
            className={activePage === item.id ? 'nav-item active' : 'nav-item'}
            onClick={() => onNavigate(item.id)}
          >
            <span className="nav-icon" aria-hidden="true">
              {item.icon}
            </span>
            <span>{item.label}</span>
          </button>
        ))}
      </nav>
    </aside>
  )
}
