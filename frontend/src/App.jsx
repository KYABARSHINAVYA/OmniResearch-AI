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
import Login from './pages/Login'
import Register from './pages/Register'
import './App.css'

const appPages = {
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
  return appPages[hash] ? hash : 'home'
}

function getInitialAuthPage() {
  const hash = window.location.hash.replace('#/', '')
  return hash === 'register' ? 'register' : 'login'
}

export default function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(() =>
    Boolean(localStorage.getItem('omniresearch_token')),
  )
  const [authPage, setAuthPage] = useState(getInitialAuthPage)
  const [activePage, setActivePage] = useState(getInitialPage)

  const ActivePage = useMemo(() => appPages[activePage] || Home, [activePage])

  const handleNavigate = (page) => {
    if (!isAuthenticated && page !== 'login' && page !== 'register') {
      setAuthPage('login')
      window.history.replaceState(null, '', '#/login')
      return
    }

    if (page === 'login' || page === 'register') {
      setAuthPage(page)
      window.history.replaceState(null, '', `#/${page}`)
      return
    }

    setActivePage(page)
    window.history.replaceState(null, '', `#/${page}`)
  }

  const handleLogin = () => {
    setIsAuthenticated(true)
    setActivePage('home')
    window.history.replaceState(null, '', '#/home')
  }

  const handleLogout = () => {
    localStorage.removeItem('omniresearch_token')
    setIsAuthenticated(false)
    setAuthPage('login')
    window.history.replaceState(null, '', '#/login')
  }

  if (!isAuthenticated) {
    const AuthPage = authPage === 'register' ? Register : Login

    return (
      <main className="auth-page">
        <AuthPage onNavigate={handleNavigate} onLogin={handleLogin} />
      </main>
    )
  }

  return (
    <div className="app-shell">
      <Sidebar activePage={activePage} onNavigate={handleNavigate} />
      <main className="main-shell">
        <Navbar activePage={activePage} onNavigate={handleNavigate} onLogout={handleLogout} />
        <ActivePage onNavigate={handleNavigate} />
      </main>
    </div>
  )
}
