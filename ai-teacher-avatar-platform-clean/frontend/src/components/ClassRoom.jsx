import { useEffect, useRef, useState } from 'react'
import { getLessonToday, getProfile, sendLessonMessage, setVoicePref } from '../api'
import { useSpeech } from '../useSpeech'
import TeacherPanel from './TeacherPanel'
import DailyPath from './DailyPath'
import BookPanel from './BookPanel'
import VoiceTeacher from './VoiceTeacher'
import ProfileForm from './ProfileForm'

const TABS = [
  { id: 'class', label: "Today's Class" },
  { id: 'book', label: '📚 Teach me from a book' },
  { id: 'practice', label: 'Free Practice' },
]

export default function ClassRoom({ auth, onVoiceChange }) {
  const [tab, setTab] = useState('class')
  const [lesson, setLesson] = useState(null)
  const [messages, setMessages] = useState([])
  const [busy, setBusy] = useState(false)
  const [speaking, setSpeaking] = useState(false)
  const [error, setError] = useState('')
  const [homeworkBanner, setHomeworkBanner] = useState(null)
  const [showProfileForm, setShowProfileForm] = useState(false)
  const [profile, setProfile] = useState(null)
  // Real Classroom Mode: the teacher keeps listening automatically after each
  // reply, like a live class, instead of waiting for a mic-press every turn.
  const [autoMode, setAutoMode] = useState(true)
  const autoModeRef = useRef(autoMode)
  autoModeRef.current = autoMode
  const { listen, speak, listening, supported } = useSpeech()

  useEffect(() => {
    let cancelled = false

    async function start() {
      try {
        const p = await getProfile(auth.access_token)
        if (cancelled) return
        setProfile(p)
        const needsOnboarding = !p.target_band && (!p.weaknesses || p.weaknesses.length === 0)
        if (needsOnboarding) {
          setShowProfileForm(true)
          return // wait for the student to fill the profile before starting class
        }
        await beginClass()
      } catch (err) {
        if (!cancelled) setError(err.message)
      }
    }

    async function beginClass() {
      const data = await getLessonToday(auth.access_token)
      if (cancelled) return
      setLesson(data)
      setMessages([{ role: 'assistant', text: data.prompt_text }])
      await speakReply(data.prompt_text)
      if (autoModeRef.current) runListenLoop()
    }

    start()
    return () => {
      cancelled = true
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  async function speakReply(text) {
    setSpeaking(true)
    await speak(text, auth.voice_pref)
    setSpeaking(false)
  }

  async function runListenLoop() {
    if (!supported || homeworkBanner) return
    try {
      const transcript = await listen()
      await submitAnswer(transcript)
    } catch (err) {
      // Mic errors (silence timeout, permission, etc.) shouldn't kill the class —
      // just stop the auto-loop for this turn and let the student press the button.
      if (autoModeRef.current) setError(err.message)
    }
  }

  async function submitAnswer(transcript) {
    if (!lesson) return
    setError('')
    setMessages((m) => [...m, { role: 'user', text: transcript }])
    setBusy(true)
    try {
      const result = await sendLessonMessage(auth.access_token, lesson.session_id, transcript)
      setLesson((l) => ({
        ...l,
        stage: result.stage,
        stage_index: result.stage_index,
        stage_label: result.stage_label,
        words_learned: result.words_learned,
      }))
      setMessages((m) => [
        ...m,
        { role: 'assistant', text: result.reply_text, correction: result.correction },
      ])
      setBusy(false)
      await speakReply(result.reply_text)
      if (result.lesson_complete && result.homework_text) {
        setHomeworkBanner(result.homework_text)
        return
      }
      if (autoModeRef.current) runListenLoop()
    } catch (err) {
      setError(err.message)
      setBusy(false)
    }
  }

  async function handleMicPress() {
    if (!lesson || listening || busy) return
    setError('')
    try {
      const transcript = await listen()
      await submitAnswer(transcript)
    } catch (err) {
      setError(err.message)
    }
  }

  async function handleVoiceToggle() {
    const next = auth.voice_pref === 'male' ? 'female' : 'male'
    await setVoicePref(auth.access_token, next)
    onVoiceChange(next)
  }

  function handleBookReply(result) {
    setMessages((m) => [
      ...m,
      { role: 'assistant', text: result.reply_text, meta: `From "${result.source_book}"` },
      ...(result.example ? [{ role: 'assistant', text: `Example: ${result.example}` }] : []),
    ])
    speakReply(result.reply_text)
  }

  async function handleProfileSaved(savedProfile) {
    setProfile(savedProfile)
    setShowProfileForm(false)
    const data = await getLessonToday(auth.access_token)
    setLesson(data)
    setMessages([{ role: 'assistant', text: data.prompt_text }])
    await speakReply(data.prompt_text)
    if (autoModeRef.current) runListenLoop()
  }

  if (showProfileForm) {
    return (
      <ProfileForm
        auth={auth}
        initial={profile}
        onSaved={handleProfileSaved}
        onCancel={() => {
          setShowProfileForm(false)
          handleProfileSaved(profile)
        }}
      />
    )
  }

  return (
    <div className="classroom">
      <TeacherPanel lesson={lesson} speaking={speaking} onEditProfile={() => setShowProfileForm(true)} />

      <div className="card wide classroom-main">
        <div className="topbar">
          <div className="modes">
            {TABS.map((t) => (
              <button
                key={t.id}
                className={tab === t.id ? 'mode active' : 'mode'}
                onClick={() => setTab(t.id)}
              >
                {t.label}
              </button>
            ))}
          </div>
          <button className="voice-toggle" onClick={handleVoiceToggle}>
            Teacher voice: {auth.voice_pref === 'male' ? 'Male' : 'Female'}
          </button>
        </div>

        {tab === 'class' && (
          <>
            {lesson && <DailyPath stageIndex={lesson.stage_index} />}

            {!supported && (
              <p className="error">
                Speech recognition isn't supported in this browser. Try Chrome desktop.
              </p>
            )}

            <label className="auto-mode-toggle">
              <input
                type="checkbox"
                checked={autoMode}
                onChange={(e) => setAutoMode(e.target.checked)}
              />
              Real Classroom Mode — teacher listens automatically after speaking
            </label>

            {homeworkBanner && (
              <div className="homework-banner">
                🎉 Great class today! Homework: {homeworkBanner}
              </div>
            )}

            <div className="transcript">
              {messages.map((m, i) => (
                <div key={i} className={`bubble ${m.role}`}>
                  <p>{m.text}</p>
                  {m.correction && <p className="correction">Correction: {m.correction}</p>}
                </div>
              ))}
            </div>

            {error && <p className="error">{error}</p>}

            <button
              className={`mic ${listening ? 'listening' : ''}`}
              onClick={handleMicPress}
              disabled={busy || speaking || !supported || !lesson || !!homeworkBanner}
            >
              {listening
                ? 'Listening…'
                : busy
                ? 'Thinking…'
                : speaking
                ? 'Mr. David is speaking…'
                : autoMode
                ? '🎤 Listening automatically (or press to speak now)'
                : '🎤 Hold to speak'}
            </button>
          </>
        )}

        {tab === 'book' && (
          <>
            <BookPanel auth={auth} onTeacherReply={handleBookReply} />
            <div className="transcript">
              {messages
                .filter((m) => m.meta || m.role === 'user')
                .map((m, i) => (
                  <div key={i} className={`bubble ${m.role}`}>
                    <p>{m.text}</p>
                    {m.meta && <p className="meta">{m.meta}</p>}
                  </div>
                ))}
            </div>
          </>
        )}

        {tab === 'practice' && <VoiceTeacher auth={auth} onVoiceChange={onVoiceChange} embedded />}
      </div>
    </div>
  )
}
