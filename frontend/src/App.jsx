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

const currentResearchKey = 'omniresearch_current_research'
const researchHistoryKey = 'omniresearch_research_history'
const welcomeMessage = {
  role: 'assistant',
  text: 'Ask a research question and I will route it through the OmniResearch workflow.',
}

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

function createResearch() {
  return {
    id: `research-${Date.now()}`,
    title: '',
    updatedAt: new Date().toISOString(),
    messages: [welcomeMessage],
  }
}

function readStoredJson(key, fallback) {
  try {
    const value = localStorage.getItem(key)
    return value ? JSON.parse(value) : fallback
  } catch {
    return fallback
  }
}

function hasResearchContent(research) {
  return Boolean(
    research?.messages?.some((message) => message.role === 'user' || message.reportPath),
  )
}

function researchTitle(research) {
  return (
    research?.title ||
    research?.messages?.find((message) => message.role === 'user')?.text ||
    'Untitled research'
  )
}

export default function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(() =>
    Boolean(localStorage.getItem('omniresearch_token')),
  )
  const [authPage, setAuthPage] = useState(getInitialAuthPage)
  const [activePage, setActivePage] = useState(getInitialPage)
  const [currentResearch, setCurrentResearch] = useState(() =>
    readStoredJson(currentResearchKey, createResearch()),
  )
  const [researchHistory, setResearchHistory] = useState(() =>
    readStoredJson(researchHistoryKey, []),
  )

  const ActivePage = useMemo(() => appPages[activePage] || Home, [activePage])

  const updateCurrentResearch = (updater) => {
    setCurrentResearch((current) => {
      const next = typeof updater === 'function' ? updater(current) : updater
      const withTitle = {
        ...next,
        title: next.title || researchTitle(next),
      }
      localStorage.setItem(currentResearchKey, JSON.stringify(withTitle))
      return withTitle
    })
  }

  const archiveCurrentResearch = () => {
    setCurrentResearch((current) => {
      if (!hasResearchContent(current)) return current

      const archived = {
        ...current,
        title: researchTitle(current),
        updatedAt: new Date().toISOString(),
      }

      setResearchHistory((history) => {
        const withoutDuplicate = history.filter((item) => item.id !== archived.id)
        const nextHistory = [archived, ...withoutDuplicate].slice(0, 30)
        localStorage.setItem(researchHistoryKey, JSON.stringify(nextHistory))
        return nextHistory
      })

      return current
    })
  }

  const startNewResearch = () => {
    const next = createResearch()
    setCurrentResearch(next)
    localStorage.setItem(currentResearchKey, JSON.stringify(next))
  }

  const selectResearch = (research) => {
    archiveCurrentResearch()

    const selected =
      research.source === 'saved'
        ? {
            id: `saved-${research.id}`,
            title: research.question,
            updatedAt: new Date().toISOString(),
            messages: [
              { role: 'user', text: research.question },
              { role: 'assistant', text: research.answer },
            ],
          }
        : research

    updateCurrentResearch(selected)
  }

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
    archiveCurrentResearch()
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
        <ActivePage
          onNavigate={handleNavigate}
          currentResearch={currentResearch}
          researchHistory={researchHistory}
          onArchiveResearch={archiveCurrentResearch}
          onNewResearch={startNewResearch}
          onResearchChange={updateCurrentResearch}
          onSelectResearch={selectResearch}
        />
      </main>
    </div>
  )
}
