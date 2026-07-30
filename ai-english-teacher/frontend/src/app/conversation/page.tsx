'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { api } from '@/lib/api';
import { useVoice } from '@/hooks/useVoice';

interface Persona {
  id: string;
  label: string;
  description: string;
}

interface Scenario {
  id: string;
  label: string;
}

interface Message {
  role: string;
  content: string;
  corrections?: Array<{ wrong?: string; correct?: string; text?: string; correction?: string }>;
  voiceScores?: { overall?: number; fluency?: number; pronunciation?: number };
  teachingMode?: string;
}

interface LessonReport {
  scores: Record<string, number>;
  estimates: {
    cefr_level?: string;
    ielts_speaking_estimate?: number | string;
    pte_speaking_estimate?: number | string;
    confidence?: number;
    label?: string;
  };
  recurring_mistakes: Array<{ error: string; correction: string; category: string }>;
  executive_summary?: string;
  recommendations?: string[];
}

export default function ConversationPage() {
  const [personas, setPersonas] = useState<Persona[]>([]);
  const [scenarios, setScenarios] = useState<Scenario[]>([]);
  const [personaId, setPersonaId] = useState('conversation_partner');
  const [scenario, setScenario] = useState('job_interview');
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [started, setStarted] = useState(false);
  const [autoSpeak, setAutoSpeak] = useState(true);
  const [voiceFirst, setVoiceFirst] = useState(true);
  const [lessonReport, setLessonReport] = useState<LessonReport | null>(null);
  const [showReport, setShowReport] = useState(false);
  const { listen, speak, listening, sttSupported, ttsSupported } = useVoice();

  useEffect(() => {
    api.voice.personas().then((res) => {
      const data = res as { personas: Persona[]; scenarios: Scenario[] };
      setPersonas(data.personas);
      setScenarios(data.scenarios);
    }).catch(() => {
      setScenarios([
        { id: 'job_interview', label: 'Job Interview' },
        { id: 'restaurant', label: 'Restaurant Order' },
        { id: 'travel', label: 'Travel & Tourism' },
        { id: 'business_meeting', label: 'Business Meeting' },
      ]);
    });
  }, []);

  function addAssistantMessage(content: string, metadata?: Record<string, unknown>) {
    const corrections = (metadata?.corrections as Message['corrections'])
      || (metadata?.grammar_corrections as Message['corrections']) || [];
    const voiceScores = metadata?.voice_scores as Message['voiceScores'];
    const teachingMode = metadata?.teaching_mode as string | undefined;
    setMessages(prev => [...prev, { role: 'assistant', content, corrections, voiceScores, teachingMode }]);
    if (autoSpeak && ttsSupported) speak(content);
  }

  async function startConversation() {
    setLoading(true);
    setLessonReport(null);
    setShowReport(false);
    try {
      const res = await api.conversations.start({ scenario, persona_id: personaId }) as {
        id: string;
        initial_message: { content: string };
      };
      setConversationId(res.id);
      setMessages([{ role: 'assistant', content: res.initial_message.content }]);
      if (autoSpeak && ttsSupported) speak(res.initial_message.content);
      setStarted(true);
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to start. Please login first.');
    } finally {
      setLoading(false);
    }
  }

  async function submitVoiceTurn(userMsg: string) {
    if (!userMsg.trim() || !conversationId) return;
    setLoading(true);
    setMessages(prev => [...prev, { role: 'user', content: userMsg.trim() }]);
    try {
      const res = await api.conversations.voiceTurn(conversationId, {
        transcript: userMsg.trim(),
        persona_id: personaId,
      }) as {
        response: string;
        teaching_mode?: string;
        corrections?: Message['corrections'];
        voice_scores?: Message['voiceScores'];
        assistant_message: { content: string; metadata?: Record<string, unknown> };
      };
      addAssistantMessage(res.response, {
        corrections: res.corrections,
        voice_scores: res.voice_scores,
        teaching_mode: res.teaching_mode,
        ...res.assistant_message.metadata,
      });
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Voice turn failed');
    } finally {
      setLoading(false);
    }
  }

  async function submitText(userMsg: string) {
    if (!userMsg.trim() || !conversationId) return;
    if (voiceFirst) {
      await submitVoiceTurn(userMsg);
      return;
    }
    setLoading(true);
    setMessages(prev => [...prev, { role: 'user', content: userMsg.trim() }]);
    try {
      const res = await api.conversations.sendMessage(conversationId, userMsg.trim()) as {
        assistant_message: { content: string; metadata?: Record<string, unknown> };
      };
      addAssistantMessage(res.assistant_message.content, res.assistant_message.metadata);
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to send message');
    } finally {
      setLoading(false);
    }
  }

  async function endLesson() {
    if (!conversationId) return;
    setLoading(true);
    try {
      const report = await api.conversations.lessonReport(conversationId) as LessonReport;
      setLessonReport(report);
      setShowReport(true);
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Could not generate lesson report');
    } finally {
      setLoading(false);
    }
  }

  async function sendMessage(e: React.FormEvent) {
    e.preventDefault();
    const userMsg = input.trim();
    if (!userMsg) return;
    setInput('');
    await submitText(userMsg);
  }

  function handleVoiceInput() {
    listen(
      async (text) => {
        setInput(text);
        await submitText(text);
      },
      (msg) => alert(msg)
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <header className="bg-white border-b px-6 py-4 flex items-center justify-between">
        <Link href="/dashboard/student" className="text-blue-600 font-bold">← AI English Teacher</Link>
        <div className="flex items-center gap-4 text-sm text-gray-500">
          <Link href="/grammar-class" className="text-blue-600 hover:underline">Grammar Class</Link>
          {started && (
            <button onClick={endLesson} disabled={loading}
              className="text-blue-600 hover:underline disabled:opacity-50">
              End lesson & report
            </button>
          )}
          {ttsSupported && (
            <label className="flex items-center gap-2 cursor-pointer">
              <input type="checkbox" checked={autoSpeak} onChange={e => setAutoSpeak(e.target.checked)} />
              Auto-play voice
            </label>
          )}
          <label className="flex items-center gap-2 cursor-pointer">
            <input type="checkbox" checked={voiceFirst} onChange={e => setVoiceFirst(e.target.checked)} />
            Voice-first mode
          </label>
        </div>
      </header>

      <main className="flex-1 max-w-2xl mx-auto w-full px-4 py-6 flex flex-col">
        {!started ? (
          <div className="bg-white rounded-xl border p-6">
            <h1 className="text-xl font-bold mb-2">Voice-First English Lesson</h1>
            <p className="text-sm text-gray-500 mb-4">
              Speak naturally with your AI teacher. The system listens, analyzes your speech,
              and responds like a real classroom teacher.
            </p>

            <h2 className="text-sm font-semibold text-gray-700 mb-2">Teacher persona</h2>
            <div className="grid grid-cols-1 gap-2 mb-4">
              {(personas.length ? personas : [{ id: 'conversation_partner', label: 'Conversation Partner', description: '' }]).map(p => (
                <button key={p.id} onClick={() => setPersonaId(p.id)}
                  className={`p-3 rounded-lg border text-left text-sm ${personaId === p.id ? 'border-blue-600 bg-blue-50' : 'hover:bg-gray-50'}`}>
                  <span className="font-medium">{p.label}</span>
                  {p.description && <span className="block text-gray-500 text-xs mt-0.5">{p.description}</span>}
                </button>
              ))}
            </div>

            <h2 className="text-sm font-semibold text-gray-700 mb-2">Scenario</h2>
            <div className="grid grid-cols-2 gap-3 mb-6">
              {scenarios.map(s => (
                <button key={s.id} onClick={() => setScenario(s.id)}
                  className={`p-3 rounded-lg border text-left text-sm ${scenario === s.id ? 'border-blue-600 bg-blue-50' : 'hover:bg-gray-50'}`}>
                  {s.label}
                </button>
              ))}
            </div>
            <button onClick={startConversation} disabled={loading}
              className="w-full bg-blue-600 text-white py-3 rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50">
              {loading ? 'Starting...' : 'Start Voice Lesson'}
            </button>
          </div>
        ) : (
          <>
            {showReport && lessonReport && (
              <div className="mb-4 bg-white border rounded-xl p-4 text-sm space-y-2">
                <h2 className="font-bold text-lg">Lesson Report</h2>
                <p className="text-gray-600">{lessonReport.executive_summary}</p>
                <div className="grid grid-cols-2 gap-2 text-xs">
                  {Object.entries(lessonReport.scores).map(([k, v]) => (
                    <div key={k} className="bg-gray-50 rounded px-2 py-1">
                      {k.replace(/_/g, ' ')}: <strong>{v}</strong>
                    </div>
                  ))}
                </div>
                {lessonReport.estimates?.cefr_level && (
                  <p className="text-xs text-gray-500">
                    Estimated CEFR: {String(lessonReport.estimates.cefr_level)} ·
                    IELTS Speaking (estimate): {String(lessonReport.estimates.ielts_speaking_estimate)}
                  </p>
                )}
                {lessonReport.recommendations?.length && (
                  <ul className="text-xs text-gray-700 list-disc pl-4">
                    {lessonReport.recommendations.slice(0, 3).map((r, i) => <li key={i}>{r}</li>)}
                  </ul>
                )}
              </div>
            )}
            <div className="flex-1 overflow-y-auto space-y-4 mb-4">
              {messages.map((msg, i) => (
                <div key={i} className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'}`}>
                  <div className={`max-w-[85%] px-4 py-3 rounded-2xl text-sm ${
                    msg.role === 'user' ? 'bg-blue-600 text-white' : 'bg-white border'
                  }`}>
                    <p>{msg.content}</p>
                    {msg.voiceScores && (
                      <p className="mt-1 text-xs opacity-80">
                        Score {msg.voiceScores.overall} · Fluency {msg.voiceScores.fluency} · Pronunciation {msg.voiceScores.pronunciation}
                      </p>
                    )}
                    {msg.teachingMode && msg.teachingMode !== 'none' && (
                      <p className="mt-1 text-xs opacity-70">Teaching: {msg.teachingMode}</p>
                    )}
                    {msg.role === 'assistant' && ttsSupported && (
                      <button type="button" onClick={() => speak(msg.content)}
                        className="mt-2 text-xs text-blue-600 hover:underline">
                        Play again
                      </button>
                    )}
                  </div>
                  {msg.corrections && msg.corrections.length > 0 && (
                    <div className="mt-1 max-w-[85%] text-xs bg-amber-50 border border-amber-200 rounded-lg px-3 py-2 text-amber-900">
                      <p className="font-medium mb-1">Correction</p>
                      {msg.corrections.map((c, j) => (
                        <p key={j}>
                          {(c.wrong || c.text) && (c.correct || c.correction) ? (
                            <><span className="line-through">{c.wrong || c.text}</span> → <strong>{c.correct || c.correction}</strong></>
                          ) : null}
                        </p>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
            <form onSubmit={sendMessage} className="flex gap-2 items-center">
              {sttSupported && (
                <button type="button" onClick={handleVoiceInput} disabled={loading || listening}
                  className={`px-4 py-3 rounded-lg border font-medium ${listening ? 'bg-red-50 border-red-300 text-red-600 animate-pulse' : 'hover:bg-gray-50'}`}
                  title="Speak your answer">
                  {listening ? 'Listening...' : 'Mic'}
                </button>
              )}
              <input value={input} onChange={e => setInput(e.target.value)}
                className="flex-1 border rounded-lg px-4 py-3" placeholder="Speak or type your answer..." disabled={loading} />
              <button type="submit" disabled={loading || !input.trim()}
                className="bg-blue-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50">
                Send
              </button>
            </form>
          </>
        )}
      </main>
    </div>
  );
}
