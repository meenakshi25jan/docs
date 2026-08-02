import { useState } from 'react'
import { setProfile } from '../api'

const WEAKNESS_OPTIONS = [
  'Past tense',
  'Pronunciation',
  'Vocabulary',
  'Articles (a/an/the)',
  'Prepositions',
  'Sentence structure',
  'Listening speed',
  'Confidence speaking',
]

export default function ProfileForm({ auth, initial, onSaved, onCancel }) {
  const [level, setLevel] = useState(initial?.level || 'Intermediate')
  const [targetBand, setTargetBand] = useState(initial?.target_band ?? '')
  const [nativeLanguage, setNativeLanguage] = useState(initial?.native_language || '')
  const [weaknesses, setWeaknesses] = useState(initial?.weaknesses || [])
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

  function toggleWeakness(w) {
    setWeaknesses((cur) => (cur.includes(w) ? cur.filter((x) => x !== w) : [...cur, w]))
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setBusy(true)
    try {
      const saved = await setProfile(auth.access_token, {
        level,
        target_band: targetBand === '' ? null : Number(targetBand),
        native_language: nativeLanguage,
        weaknesses,
      })
      onSaved(saved)
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="profile-overlay">
      <form className="card profile-form" onSubmit={handleSubmit}>
        <h2>Tell Mr. David about yourself</h2>
        <p className="panel-sub">This helps your teacher personalize every lesson.</p>

        <label className="field-label">Current level</label>
        <select value={level} onChange={(e) => setLevel(e.target.value)}>
          <option>Beginner</option>
          <option>Intermediate</option>
          <option>Advanced</option>
        </select>

        <label className="field-label">Target band score (optional, e.g. IELTS 7.0)</label>
        <input
          type="number"
          min="1"
          max="9"
          step="0.5"
          placeholder="7.0"
          value={targetBand}
          onChange={(e) => setTargetBand(e.target.value)}
        />

        <label className="field-label">Native language (optional)</label>
        <input
          placeholder="e.g. Hindi"
          value={nativeLanguage}
          onChange={(e) => setNativeLanguage(e.target.value)}
        />

        <label className="field-label">What do you struggle with?</label>
        <div className="weakness-grid">
          {WEAKNESS_OPTIONS.map((w) => (
            <button
              type="button"
              key={w}
              className={weaknesses.includes(w) ? 'weakness-chip active' : 'weakness-chip'}
              onClick={() => toggleWeakness(w)}
            >
              {w}
            </button>
          ))}
        </div>

        {error && <p className="error">{error}</p>}

        <div className="profile-actions">
          {onCancel && (
            <button type="button" className="link" onClick={onCancel}>
              Cancel
            </button>
          )}
          <button type="submit" disabled={busy}>
            {busy ? 'Saving…' : 'Save and start class'}
          </button>
        </div>
      </form>
    </div>
  )
}
