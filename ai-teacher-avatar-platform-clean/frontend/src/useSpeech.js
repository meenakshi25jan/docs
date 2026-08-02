import { useCallback, useRef, useState } from 'react'

// Wraps the browser's Web Speech API: SpeechRecognition (STT) + speechSynthesis (TTS).
// Works best in Chrome desktop. This is the v1 shortcut described in ARCHITECTURE.md —
// swap for a server-side STT/TTS pipeline (Whisper + a TTS engine) for cross-browser/mobile.
export function useSpeech() {
  const [listening, setListening] = useState(false)
  const [supported] = useState(
    () => 'webkitSpeechRecognition' in window || 'SpeechRecognition' in window
  )
  const recognitionRef = useRef(null)

  const listen = useCallback(() => {
    return new Promise((resolve, reject) => {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
      if (!SpeechRecognition) {
        reject(new Error('Speech recognition is not supported in this browser. Try Chrome.'))
        return
      }
      const recognition = new SpeechRecognition()
      recognitionRef.current = recognition
      recognition.lang = 'en-US'
      recognition.interimResults = false
      recognition.maxAlternatives = 1

      recognition.onstart = () => setListening(true)
      recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript
        resolve(transcript)
      }
      recognition.onerror = (event) => reject(new Error(event.error))
      recognition.onend = () => setListening(false)

      recognition.start()
    })
  }, [])

  const stopListening = useCallback(() => {
    recognitionRef.current?.stop()
  }, [])

  const speak = useCallback((text, voicePref) => {
    return new Promise((resolve) => {
      if (!('speechSynthesis' in window)) {
        resolve()
        return
      }
      window.speechSynthesis.cancel()
      const utterance = new SpeechSynthesisUtterance(text)
      const voices = window.speechSynthesis.getVoices()

      // Simple heuristic voice-gender match — browser voice metadata isn't standardized,
      // so this is best-effort. Good enough for v1; revisit if you move TTS server-side.
      const femaleHints = ['female', 'zira', 'samantha', 'victoria', 'susan', 'karen']
      const maleHints = ['male', 'david', 'daniel', 'alex', 'fred', 'george']
      const hints = voicePref === 'male' ? maleHints : femaleHints
      const match = voices.find((v) =>
        hints.some((h) => v.name.toLowerCase().includes(h))
      )
      if (match) utterance.voice = match
      utterance.lang = 'en-US'
      utterance.onend = () => resolve()
      utterance.onerror = () => resolve()
      window.speechSynthesis.speak(utterance)
    })
  }, [])

  return { listen, stopListening, speak, listening, supported }
}
