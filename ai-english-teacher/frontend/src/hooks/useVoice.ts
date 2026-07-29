'use client';

import { useCallback, useEffect, useState } from 'react';

type SpeechRecognitionCtor = new () => SpeechRecognition;

declare global {
  interface Window {
    webkitSpeechRecognition?: SpeechRecognitionCtor;
    SpeechRecognition?: SpeechRecognitionCtor;
  }
}

export function useVoice() {
  const [sttSupported, setSttSupported] = useState(false);
  const [listening, setListening] = useState(false);

  useEffect(() => {
    setSttSupported(
      typeof window !== 'undefined' &&
        !!(window.SpeechRecognition || window.webkitSpeechRecognition)
    );
  }, []);

  const listen = useCallback((onResult: (text: string) => void, onError?: (msg: string) => void) => {
    const Ctor = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!Ctor) {
      onError?.('Speech recognition not supported in this browser. Try Chrome or Edge.');
      return;
    }
    const recognition = new Ctor();
    recognition.lang = 'en-US';
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;
    setListening(true);
    recognition.onresult = (event: SpeechRecognitionEvent) => {
      const text = event.results[0]?.[0]?.transcript?.trim();
      if (text) onResult(text);
      setListening(false);
    };
    recognition.onerror = () => {
      onError?.('Could not hear you. Check microphone permissions and try again.');
      setListening(false);
    };
    recognition.onend = () => setListening(false);
    recognition.start();
  }, []);

  const speak = useCallback((text: string) => {
    if (typeof window === 'undefined' || !window.speechSynthesis) return;
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'en-US';
    utterance.rate = 0.95;
    window.speechSynthesis.speak(utterance);
  }, []);

  return {
    listen,
    speak,
    listening,
    sttSupported,
    ttsSupported: typeof window !== 'undefined' && !!window.speechSynthesis,
  };
}
