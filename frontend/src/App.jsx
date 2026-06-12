import { useState, useRef, useEffect } from 'react'

const API = '/api/chat'

export default function App() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [toolRunning, setToolRunning] = useState(null)
  const bottomRef = useRef(null)

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, toolRunning])

  async function sendMessage() {
    const text = input.trim()
    if (!text || loading) return
    setInput('')

    const userMsg = { role: 'user', content: text }
    const updated = [...messages, userMsg]
    setMessages(updated)
    setLoading(true)

    try {
      const res = await fetch(API, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ messages: updated }),
      })
      const data = await res.json()

      // Show tool calls as intermediary messages
      const newEntries = [...updated]
      if (data.tool_calls?.length) {
        setToolRunning(data.tool_calls[0])
        for (const tc of data.tool_calls) {
          newEntries.push({
            role: 'assistant',
            content: '',
            isTool: true,
            toolCall: tc,
          })
        }
      }
      // Final LLM response
      setToolRunning(null)
      newEntries.push({ role: 'assistant', content: data.response })
      setMessages(newEntries)
    } catch (err) {
      setMessages([...updated, {
        role: 'assistant',
        content: `Error: ${err.message}`,
        isError: true,
      }])
    } finally {
      setLoading(false)
      setToolRunning(null)
    }
  }

  function handleKeyDown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  // -- Render --
  return (
    <div className="h-full flex flex-col bg-netai-bg text-netai-text font-mono">
      {/* -- Header -- */}
      <header className="flex items-center justify-between px-6 py-3 border-b border-netai-border bg-netai-surface">
        <div className="flex items-center gap-3">
          <span className="text-xl font-bold text-netai-accent">NetAI</span>
          <span className="text-sm text-netai-dim">Console</span>
        </div>
        <div className="flex items-center gap-2">
          <span className={`inline-block w-2 h-2 rounded-full ${loading ? 'bg-netai-tool animate-pulse' : 'bg-netai-success'}`} />
          <span className="text-xs text-netai-dim">{loading ? 'thinking...' : 'ready'}</span>
        </div>
      </header>

      {/* -- Messages -- */}
      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-3">
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-netai-dim">
            <p className="text-2xl mb-2">{'>'}_</p>
            <p className="text-sm">NetAI Console — ask me anything about the network</p>
            <p className="text-xs mt-1 text-netai-muted">try: ping 8.8.8.8</p>
          </div>
        )}

        {messages.map((msg, i) => {
          if (msg.isTool) {
            return (
              <div key={i} className="flex justify-start">
                <div className="max-w-[80%] bg-netai-surface border border-netai-tool/30 rounded-lg px-4 py-2 text-sm">
                  <div className="flex items-center gap-2 text-netai-tool mb-1">
                    <span className="text-xs">⚡</span>
                    <span className="font-semibold">{msg.toolCall.name}</span>
                  </div>
                  <pre className="text-netai-dim text-xs whitespace-pre-wrap">
                    {JSON.stringify(msg.toolCall.arguments, null, 2)}
                  </pre>
                  <details className="mt-1">
                    <summary className="text-netai-muted text-xs cursor-pointer hover:text-netai-dim">
                      result preview
                    </summary>
                    <pre className="text-netai-dim text-xs whitespace-pre-wrap mt-1 max-h-40 overflow-y-auto">
                      {msg.toolCall.result_preview}
                    </pre>
                  </details>
                </div>
              </div>
            )
          }

          const isUser = msg.role === 'user'
          return (
            <div key={i} className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
              <div
                className={`max-w-[80%] rounded-lg px-4 py-2 ${
                  msg.isError
                    ? 'bg-red-900/30 border border-netai-error/50 text-netai-error'
                    : isUser
                      ? 'bg-netai-accent/20 border border-netai-accent/30'
                      : 'bg-netai-surface border border-netai-border'
                }`}
              >
                {!isUser && !msg.isError && (
                  <div className="flex items-center gap-1.5 mb-1">
                    <span className="text-netai-accent2 text-xs">◆</span>
                    <span className="text-netai-accent2 text-xs font-semibold">NetAI</span>
                  </div>
                )}
                <p className="text-sm whitespace-pre-wrap leading-relaxed">{msg.content}</p>
              </div>
            </div>
          )
        })}

        {/* -- Tool spinner -- */}
        {loading && toolRunning && (
          <div className="flex justify-start">
            <div className="bg-netai-surface border border-netai-tool/30 rounded-lg px-4 py-3">
              <div className="flex items-center gap-3">
                <span className="inline-block w-2 h-2 bg-netai-tool rounded-full animate-ping" />
                <span className="text-netai-tool text-sm font-semibold">{toolRunning.name}</span>
                <span className="text-netai-dim text-xs">running...</span>
              </div>
              <pre className="text-netai-dim text-xs mt-1 whitespace-pre-wrap">
                {JSON.stringify(toolRunning.arguments, null, 2)}
              </pre>
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* -- Input -- */}
      <div className="border-t border-netai-border bg-netai-surface px-4 py-3">
        <div className="flex gap-2 max-w-4xl mx-auto">
          <input
            className="flex-1 bg-netai-bg border border-netai-border rounded-lg px-4 py-2.5 text-sm text-netai-text placeholder-netai-muted outline-none focus:border-netai-accent transition-colors"
            placeholder="Ask about a host, ping an IP, check a web service..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={loading}
          />
          <button
            className={`px-5 py-2.5 rounded-lg font-semibold text-sm transition-all ${
              loading
                ? 'bg-netai-muted text-netai-dim cursor-not-allowed'
                : 'bg-netai-accent text-white hover:bg-blue-600 active:scale-95'
            }`}
            onClick={sendMessage}
            disabled={loading}
          >
            {loading ? '...' : 'Send'}
          </button>
        </div>
      </div>
    </div>
  )
}
