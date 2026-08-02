import { useState } from 'react'
import Login from './components/Login'
import ClassRoom from './components/ClassRoom'

export default function App() {
  const [auth, setAuth] = useState(null)

  return (
    <div className={auth ? 'app app-classroom' : 'app'}>
      {!auth && <h1>AI English Teacher</h1>}
      {!auth ? (
        <Login onAuthed={setAuth} />
      ) : (
        <ClassRoom
          auth={auth}
          onVoiceChange={(v) => setAuth({ ...auth, voice_pref: v })}
        />
      )}
    </div>
  )
}
