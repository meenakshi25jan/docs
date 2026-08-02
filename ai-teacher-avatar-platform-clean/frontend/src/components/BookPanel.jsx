import { useEffect, useState } from 'react'
import { askBookTopic, listBooks, uploadBook } from '../api'

export default function BookPanel({ auth, onTeacherReply }) {
  const [books, setBooks] = useState([])
  const [selectedBook, setSelectedBook] = useState('')
  const [topic, setTopic] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [sessionId, setSessionId] = useState(null)

  useEffect(() => {
    listBooks(auth.access_token)
      .then((b) => {
        setBooks(b)
        if (b.length) setSelectedBook(b[0].id)
      })
      .catch(() => {})
  }, [auth.access_token])

  async function handleUpload(e) {
    const file = e.target.files?.[0]
    if (!file) return
    setError('')
    setBusy(true)
    try {
      const result = await uploadBook(auth.access_token, file)
      setBooks((b) => [result.book, ...b])
      setSelectedBook(result.book.id)
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
      e.target.value = ''
    }
  }

  async function handleAsk(e) {
    e.preventDefault()
    if (!selectedBook || !topic.trim()) return
    setError('')
    setBusy(true)
    try {
      const result = await askBookTopic(auth.access_token, selectedBook, topic, sessionId)
      setSessionId(result.session_id)
      onTeacherReply(result)
      setTopic('')
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="book-panel">
      <p className="panel-label">Teach me from a book</p>
      <label className="book-upload">
        📚 Upload a book / notes (.txt, .pdf)
        <input type="file" accept=".txt,.pdf,.md" onChange={handleUpload} hidden />
      </label>

      {books.length > 0 && (
        <form onSubmit={handleAsk} className="book-ask">
          <select value={selectedBook} onChange={(e) => setSelectedBook(e.target.value)}>
            {books.map((b) => (
              <option key={b.id} value={b.id}>
                {b.title}
              </option>
            ))}
          </select>
          <input
            placeholder="What topic do you want explained?"
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
          />
          <button type="submit" disabled={busy || !topic.trim()}>
            {busy ? 'Thinking…' : 'Ask Mr. David'}
          </button>
        </form>
      )}

      {error && <p className="error">{error}</p>}
    </div>
  )
}
