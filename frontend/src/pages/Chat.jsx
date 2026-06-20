import ChatWindow from '../components/ChatWindow'

export default function Chat() {
  return (
    <div className="content-stack">
      <section className="panel page-intro">
        <h2>Research Chat</h2>
        <p>
          Route each question through fast, balanced, or deep research. Every
          answer returns workflow timing, confidence, and hallucination risk.
        </p>
      </section>
      <ChatWindow />
    </div>
  )
}
