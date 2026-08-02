const API_BASE = 'http://localhost:8000'

function authHeaders(token) {
  return token ? { Authorization: `Bearer ${token}` } : {}
}

export async function register(email, password, displayName) {
  const res = await fetch(`${API_BASE}/api/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password, display_name: displayName }),
  })
  if (!res.ok) throw new Error((await res.json()).detail || 'Registration failed')
  return res.json()
}

export async function login(email, password) {
  const res = await fetch(`${API_BASE}/api/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  })
  if (!res.ok) throw new Error((await res.json()).detail || 'Login failed')
  return res.json()
}

export async function setVoicePref(token, voicePref) {
  const res = await fetch(`${API_BASE}/api/auth/voice-pref`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json', ...authHeaders(token) },
    body: JSON.stringify({ voice_pref: voicePref }),
  })
  if (!res.ok) throw new Error('Could not save voice preference')
  return res.json()
}

export async function sendAgentMessage(token, mode, text, sessionId) {
  const res = await fetch(`${API_BASE}/api/agent/message`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...authHeaders(token) },
    body: JSON.stringify({ mode, text, session_id: sessionId || null }),
  })
  if (!res.ok) throw new Error((await res.json()).detail || 'Agent request failed')
  return res.json()
}

// --- Student profile memory ---------------------------------------------

export async function getProfile(token) {
  const res = await fetch(`${API_BASE}/api/profile`, { headers: authHeaders(token) })
  if (!res.ok) throw new Error('Could not load profile')
  return res.json()
}

export async function setProfile(token, profile) {
  const res = await fetch(`${API_BASE}/api/profile`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json', ...authHeaders(token) },
    body: JSON.stringify(profile),
  })
  if (!res.ok) throw new Error('Could not save profile')
  return res.json()
}

// --- Teacher / lesson flow ---------------------------------------------

export async function getLessonToday(token) {
  const res = await fetch(`${API_BASE}/api/lesson/today`, {
    headers: authHeaders(token),
  })
  if (!res.ok) throw new Error((await res.json()).detail || "Couldn't start today's class")
  return res.json()
}

export async function sendLessonMessage(token, sessionId, text) {
  const res = await fetch(`${API_BASE}/api/lesson/message`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...authHeaders(token) },
    body: JSON.stringify({ session_id: sessionId, text }),
  })
  if (!res.ok) throw new Error((await res.json()).detail || 'Lesson request failed')
  return res.json()
}

// --- Books (upload + teach-from-book) -----------------------------------

export async function uploadBook(token, file) {
  const formData = new FormData()
  formData.append('file', file)
  const res = await fetch(`${API_BASE}/api/books/upload`, {
    method: 'POST',
    headers: authHeaders(token),
    body: formData,
  })
  if (!res.ok) throw new Error((await res.json()).detail || 'Upload failed')
  return res.json()
}

export async function listBooks(token) {
  const res = await fetch(`${API_BASE}/api/books/`, { headers: authHeaders(token) })
  if (!res.ok) throw new Error((await res.json()).detail || 'Could not load books')
  return res.json()
}

export async function askBookTopic(token, bookId, topic, sessionId) {
  const res = await fetch(`${API_BASE}/api/books/topic`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...authHeaders(token) },
    body: JSON.stringify({ book_id: bookId, topic, session_id: sessionId || null }),
  })
  if (!res.ok) throw new Error((await res.json()).detail || 'Could not explain that topic')
  return res.json()
}
