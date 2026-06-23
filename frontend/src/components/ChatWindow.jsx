import { useEffect, useMemo, useState } from 'react'
import { getResearchHistory, runAutonomousResearch, sendMessage } from '../api/chatApi'

const welcomeMessage = {
  role: 'assistant',
  text: 'Ask a research question and I will route it through the OmniResearch workflow.',
}

export default function ChatWindow({
  currentResearch,
  researchHistory,
  onArchiveResearch,
  onNewResearch,
  onResearchChange,
  onSelectResearch,
}) {
  const messages = currentResearch?.messages?.length ? currentResearch.messages : [welcomeMessage]
  const [input, setInput] = useState('')
  const [mode, setMode] = useState('balanced')
  const [reportTopic, setReportTopic] = useState('')
  const [isSending, setIsSending] = useState(false)
  const [error, setError] = useState('')
  const [savedHistory, setSavedHistory] = useState([])
  const [historyOpen, setHistoryOpen] = useState(false)

  const historyItems = useMemo(() => {
    const localItems = researchHistory.map((item) => ({ ...item, source: 'local' }))
    const savedItems = savedHistory.map((item) => ({ ...item, source: 'saved' }))
    return [...localItems, ...savedItems]
  }, [researchHistory, savedHistory])

  useEffect(() => {
    let active = true

    getResearchHistory()
      .then((response) => {
        if (!active) return
        setSavedHistory(response.items || [])
      })
      .catch(() => {
        if (active) setSavedHistory([])
      })

    return () => {
      active = false
    }
  }, [])

  const updateMessages = (updater) => {
    onResearchChange((current) => {
      const currentMessages = current?.messages?.length ? current.messages : [welcomeMessage]
      const nextMessages =
        typeof updater === 'function' ? updater(currentMessages) : updater

      return {
        ...(current || {}),
        id: current?.id || `research-${Date.now()}`,
        title: current?.title || '',
        updatedAt: new Date().toISOString(),
        messages: nextMessages,
      }
    })
  }

  const handleNewResearch = () => {
    onArchiveResearch()
    onNewResearch()
    setInput('')
    setReportTopic('')
    setError('')
    setHistoryOpen(false)
  }

  const handleSelectResearch = (item) => {
    onSelectResearch(item)
    setHistoryOpen(false)
  }

  const handleSend = async (event) => {
    event?.preventDefault()
    const question = input.trim()
    if (!question || isSending) return

    const thinkingId = `thinking-${Date.now()}`

    updateMessages((current) => [
      ...current,
      { role: 'user', text: question },
      { id: thinkingId, role: 'assistant', text: 'Thinking...', thinking: true },
    ])
    setInput('')
    setIsSending(true)
    setError('')

    try {
      const response = await sendMessage({ question, mode })
      updateMessages((current) =>
        current.map((message) =>
          message.id === thinkingId
            ? {
                role: 'assistant',
                text: response.answer || 'No answer returned.',
                plan: response.plan,
                evaluation: response.evaluation,
                timings: response.timings,
              }
            : message
        )
      )
      getResearchHistory()
        .then((historyResponse) => setSavedHistory(historyResponse.items || []))
        .catch(() => {})
    } catch (err) {
      setError(err.message)
      updateMessages((current) =>
        current.map((message) =>
          message.id === thinkingId
            ? {
                role: 'assistant',
                text: 'The backend did not respond. Check that FastAPI is running on the configured API URL.',
              }
            : message
        )
      )
    } finally {
      setIsSending(false)
    }
  }

  const handleReport = async () => {
    const topic = reportTopic.trim() || input.trim()
    if (!topic || isSending) return

    const thinkingId = `report-thinking-${Date.now()}`

    updateMessages((current) => [
      ...current,
      { id: thinkingId, role: 'assistant', text: 'Preparing report...', thinking: true },
    ])
    setIsSending(true)
    setError('')
    try {
      const response = await runAutonomousResearch(topic)
      updateMessages((current) =>
        current.map((message) =>
          message.id === thinkingId
            ? {
                role: 'assistant',
                text: response.answer,
                evaluation: response.evaluation,
                reportPath: response.report_path,
              }
            : message
        )
      )
      setReportTopic('')
    } catch (err) {
      setError(err.message)
      updateMessages((current) =>
        current.map((message) =>
          message.id === thinkingId
            ? {
                role: 'assistant',
                text: 'The report could not be generated. Check the backend logs for details.',
              }
            : message
        )
      )
    } finally {
      setIsSending(false)
    }
  }

  return (
    <section className={`research-workspace${historyOpen ? ' history-open' : ''}`}>
      <button
        type="button"
        className="history-fab"
        onClick={() => setHistoryOpen((open) => !open)}
        aria-label={historyOpen ? 'Close research history' : 'Open research history'}
        aria-expanded={historyOpen}
        title="Research history"
      >
        <span className="history-fab-icon" aria-hidden="true">
          <i />
          <i />
          <i />
        </span>
        {historyItems.length ? <strong>{historyItems.length}</strong> : null}
      </button>

      {historyOpen ? (
        <button
          type="button"
          className="history-scrim"
          onClick={() => setHistoryOpen(false)}
          aria-label="Close research history"
        />
      ) : null}

      <aside className="research-history panel" aria-label="Research history">
        <div className="panel-header compact">
          <div>
            <h2>Research history</h2>
            <p>{historyItems.length} saved threads</p>
          </div>
          <button type="button" className="ghost-button" onClick={handleNewResearch}>
            New research
          </button>
        </div>
        <div className="history-list">
          {historyItems.length ? (
            historyItems.map((item) => (
              <button
                type="button"
                className="history-item"
                key={`${item.source}-${item.id}`}
                onClick={() => handleSelectResearch(item)}
              >
                <strong>{item.title || item.question || 'Untitled research'}</strong>
                <span>
                  {item.source === 'saved'
                    ? 'Saved answer'
                    : new Date(item.updatedAt).toLocaleString()}
                </span>
              </button>
            ))
          ) : (
            <p className="history-empty">Completed research will appear here.</p>
          )}
        </div>
      </aside>

      <div className="chat-window">
        <div className="messages">
          {messages.map((message, index) => (
            <article
              className={`message ${message.role}${message.thinking ? ' thinking' : ''}`}
              key={message.id || `${message.role}-${index}`}
            >
              <span>{message.role}</span>
              <p>{message.text}</p>
              {message.thinking ? <div className="thinking-dots" aria-hidden="true"><i /><i /><i /></div> : null}
              {message.evaluation ? (
                <div className="evaluation-strip">
                  <strong>{Math.round((message.evaluation.confidence || 0) * 100)}% confidence</strong>
                  <span>{message.evaluation.hallucination_risk || 'unknown'} hallucination risk</span>
                </div>
              ) : null}
              {message.timings ? (
                <div className="timing-grid">
                  {Object.entries(message.timings).map(([agent, value]) => (
                    <span key={agent}>{agent}: {Number(value).toFixed(2)}s</span>
                  ))}
                </div>
              ) : null}
              {message.reportPath ? <code>{message.reportPath}</code> : null}
              {message.plan ? <pre>{JSON.stringify(message.plan, null, 2)}</pre> : null}
            </article>
          ))}
        </div>

        {error ? <p className="inline-error">{error}</p> : null}

        <form className="composer" onSubmit={handleSend}>
          <select value={mode} onChange={(event) => setMode(event.target.value)} aria-label="Research mode">
            <option value="fast">Fast</option>
            <option value="balanced">Balanced</option>
            <option value="deep">Deep</option>
          </select>
          <input
            value={input}
            onChange={(event) => setInput(event.target.value)}
            placeholder="Ask about a topic, paper, repository, or workflow..."
          />
          <button type="submit" disabled={isSending}>
            {isSending ? 'Sending' : 'Send'}
          </button>
        </form>
        <div className="report-bar">
          <input
            value={reportTopic}
            onChange={(event) => setReportTopic(event.target.value)}
            placeholder="Autonomous report topic..."
          />
          <button type="button" className="ghost-button" onClick={handleReport} disabled={isSending}>
            Generate report
          </button>
        </div>
      </div>
    </section>
  )
}
