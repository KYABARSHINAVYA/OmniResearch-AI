import { useMemo, useState } from 'react'
import Navbar from './components/Navbar'
import Sidebar from './components/Sidebar'
import Home from './pages/Home'
import Chat from './pages/Chat'
import Dashboard from './pages/Dashboard'
import Analytics from './pages/Analytics'
import Checkpoints from './pages/Checkpoints'
import Approval from './pages/Approval'
import Graph from './pages/Graph'
import Settings from './pages/Settings'
import './App.css'

const pages = {
  home: Home,
  chat: Chat,
  dashboard: Dashboard,
  analytics: Analytics,
  checkpoints: Checkpoints,
  approval: Approval,
  graph: Graph,
  settings: Settings,
}

function getInitialPage() {
  const hash = window.location.hash.replace('#/', '')
  return pages[hash] ? hash : 'home'
}

export default function App() {
  const [activePage, setActivePage] = useState(getInitialPage)

  const ActivePage = useMemo(() => pages[activePage] || Home, [activePage])

  const handleNavigate = (page) => {
    setActivePage(page)
    window.history.replaceState(null, '', `#/${page}`)
  }

  return (
    <div className="app-shell">
      <Sidebar activePage={activePage} onNavigate={handleNavigate} />
      <main className="main-shell">
        <Navbar activePage={activePage} onNavigate={handleNavigate} />
        <ActivePage onNavigate={handleNavigate} />
      </main>
    </div>
  )
}
