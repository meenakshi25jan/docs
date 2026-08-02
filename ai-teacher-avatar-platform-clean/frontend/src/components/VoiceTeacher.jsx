import { useState } from 'react'
import { sendAgentMessage, setVoicePref } from '../api'
import { useSpeech } from '../useSpeech'

const MODES = [
  { id: 'grammar', label: 'Grammar' },
  { id: 'conversation', label: 'Conversation' },
  { id: 'assessment', label: 'Band Score' },
]

export default function VoiceTeacher({ auth, onVoiceChange, embedded = false }) {
  const [mode, setMode] = useState('grammar')
  const [sessionId, setSessionId] = useState(null)
  const [messages, setMessages] = useState([])
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const { listen, speak, listening, supported } = useSpeech()

  async function handleMicPress() {
    setError('')
    try {
      const transcript = await listen()
      setMessages((m) => [...m, { role: 'user', text: transcript }])
      setBusy(true)
      const result = await sendAgentMessage(auth.access_token, mode, transcript, sessionId)
      setSessionId(result.session_id)
      setMessages((m) => [
        ...m,
        {
          role: 'assistant',
          text: result.reply_text,
          correction: result.correction,
          level: result.level,
          bandScore: result.band_score,
        },
      ])
      speak(result.reply_text, auth.voice_pref)
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  async function handleVoiceToggle() {
    const next = auth.voice_pref === 'male' ? 'female' : 'male'
    await setVoicePref(auth.access_token, next)
    onVoiceChange(next)
  }

  const content = (
    <>
      <div className="topbar">
        <div className="modes">
          {MODES.map((m) => (
            <button
              key={m.id}
              className={mode === m.id ? 'mode active' : 'mode'}
              onClick={() => {
                setMode(m.id)
                setSessionId(null)
                setMessages([])
              }}
            >
              {m.label}
            </button>
          ))}
        </div>
        {!embedded && (
          <button className="voice-toggle" onClick={handleVoiceToggle}>
            Teacher voice: {auth.voice_pref === 'male' ? 'Male' : 'Female'}
          </button>
        )}
      </div>

      {!supported && (
        <p className="error">
          Speech recognition isn't supported in this browser. Try Chrome desktop.
        </p>
      )}

      <div className="transcript">
        {messages.map((m, i) => (
          <div key={i} className={`bubble ${m.role}`}>
            <p>{m.text}</p>
            {m.correction && <p className="correction">Correction: {m.correction}</p>}
            {m.level && <p className="meta">Grammar level: {m.level}</p>}
            {m.bandScore != null && <p className="meta">Band score: {m.bandScore}</p>}
          </div>
        ))}
      </div>

      {error && <p className="error">{error}</p>}

      <button
        className={`mic ${listening ? 'listening' : ''}`}
        onClick={handleMicPress}
        disabled={busy || !supported}
      >
        {listening ? 'Listening…' : busy ? 'Thinking…' : '🎤 Hold to speak'}
      </button>
    </>
  )

  return embedded ? content : <div className="card wide">{content}</div>
}
