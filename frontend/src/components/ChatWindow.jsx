import { useState } from 'react'
import { runAutonomousResearch, sendMessage } from '../api/chatApi'

export default function ChatWindow() {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      text: 'Ask a research question and I will route it through the OmniResearch workflow.',
    },
  ])
  const [input, setInput] = useState('')
  const [mode, setMode] = useState('balanced')
  const [reportTopic, setReportTopic] = useState('')
  const [isSending, setIsSending] = useState(false)
  const [error, setError] = useState('')

  const handleSend = async (event) => {
    event?.preventDefault()
    const question = input.trim()
    if (!question || isSending) return

    setMessages((current) => [...current, { role: 'user', text: question }])
    setInput('')
    setIsSending(true)
    setError('')

    try {
      const response = await sendMessage({ question, mode })
      setMessages((current) => [
        ...current,
        {
          role: 'assistant',
          text: response.answer || 'No answer returned.',
          plan: response.plan,
          evaluation: response.evaluation,
          timings: response.timings,
        },
      ])
    } catch (err) {
      setError(err.message)
      setMessages((current) => [
        ...current,
        {
          role: 'assistant',
          text: 'The backend did not respond. Check that FastAPI is running on the configured API URL.',
        },
      ])
    } finally {
      setIsSending(false)
    }
  }

  const handleReport = async () => {
    const topic = reportTopic.trim() || input.trim()
    if (!topic || isSending) return

    setIsSending(true)
    setError('')
    try {
      const response = await runAutonomousResearch(topic)
      setMessages((current) => [
        ...current,
        {
          role: 'assistant',
          text: response.answer,
          evaluation: response.evaluation,
          reportPath: response.report_path,
        },
      ])
      setReportTopic('')
    } catch (err) {
      setError(err.message)
    } finally {
      setIsSending(false)
    }
  }

  return (
    <section className="chat-window">
      <div className="messages">
        {messages.map((message, index) => (
          <article className={`message ${message.role}`} key={`${message.role}-${index}`}>
            <span>{message.role}</span>
            <p>{message.text}</p>
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
    </section>
  )
}
