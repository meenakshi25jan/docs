'use client';

import { useState } from 'react';
import Link from 'next/link';
import { api } from '@/lib/api';
import { useVoice } from '@/hooks/useVoice';

const SCENARIOS = [
  { id: 'job_interview', label: 'Job Interview' },
  { id: 'restaurant', label: 'Restaurant Order' },
  { id: 'travel', label: 'Travel & Tourism' },
  { id: 'business_meeting', label: 'Business Meeting' },
];

interface Message {
  role: string;
  content: string;
  corrections?: Array<{ text?: string; correction?: string; note?: string }>;
}

export default function ConversationPage() {
  const [scenario, setScenario] = useState('job_interview');
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [started, setStarted] = useState(false);
  const [autoSpeak, setAutoSpeak] = useState(true);
  const { listen, speak, listening, sttSupported, ttsSupported } = useVoice();

  function addAssistantMessage(content: string, metadata?: Record<string, unknown>) {
    const corrections = (metadata?.grammar_corrections as Message['corrections']) || [];
    setMessages(prev => [...prev, { role: 'assistant', content, corrections }]);
    if (autoSpeak && ttsSupported) speak(content);
  }

  async function startConversation() {
    setLoading(true);
    try {
      const res = await api.conversations.start({ scenario }) as {
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

  async function submitText(userMsg: string) {
    if (!userMsg.trim() || !conversationId) return;
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

  async function sendMessage(e: React.FormEvent) {
    e.preventDefault();
    const userMsg = input.trim();
    if (!userMsg) return;
    setInput('');
    await submitText(userMsg);
  }

  function handleVoiceInput() {
    listen(
      (text) => {
        setInput(text);
        submitText(text);
      },
      (msg) => alert(msg)
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <header className="bg-white border-b px-6 py-4 flex items-center justify-between">
        <Link href="/dashboard/student" className="text-blue-600 font-bold">← AI English Teacher</Link>
        <div className="flex items-center gap-4 text-sm text-gray-500">
          {ttsSupported && (
            <label className="flex items-center gap-2 cursor-pointer">
              <input type="checkbox" checked={autoSpeak} onChange={e => setAutoSpeak(e.target.checked)} />
              Auto-play voice
            </label>
          )}
          <span>AI Role-Play Practice</span>
        </div>
      </header>

      <main className="flex-1 max-w-2xl mx-auto w-full px-4 py-6 flex flex-col">
        {!started ? (
          <div className="bg-white rounded-xl border p-6">
            <h1 className="text-xl font-bold mb-2">Choose a Scenario</h1>
            <p className="text-sm text-gray-500 mb-4">
              Practice speaking with text or voice {sttSupported ? '(mic supported)' : '(use Chrome for voice)'}.
            </p>
            <div className="grid grid-cols-2 gap-3 mb-6">
              {SCENARIOS.map(s => (
                <button key={s.id} onClick={() => setScenario(s.id)}
                  className={`p-4 rounded-lg border text-left ${scenario === s.id ? 'border-blue-600 bg-blue-50' : 'hover:bg-gray-50'}`}>
                  {s.label}
                </button>
              ))}
            </div>
            <button onClick={startConversation} disabled={loading}
              className="w-full bg-blue-600 text-white py-3 rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50">
              {loading ? 'Starting...' : 'Start Conversation'}
            </button>
          </div>
        ) : (
          <>
            <div className="flex-1 overflow-y-auto space-y-4 mb-4">
              {messages.map((msg, i) => (
                <div key={i} className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'}`}>
                  <div className={`max-w-[85%] px-4 py-3 rounded-2xl text-sm ${
                    msg.role === 'user' ? 'bg-blue-600 text-white' : 'bg-white border'
                  }`}>
                    <p>{msg.content}</p>
                    {msg.role === 'assistant' && ttsSupported && (
                      <button type="button" onClick={() => speak(msg.content)}
                        className="mt-2 text-xs text-blue-600 hover:underline">
                        🔊 Play again
                      </button>
                    )}
                  </div>
                  {msg.corrections && msg.corrections.length > 0 && (
                    <div className="mt-1 max-w-[85%] text-xs bg-amber-50 border border-amber-200 rounded-lg px-3 py-2 text-amber-900">
                      <p className="font-medium mb-1">Grammar tip</p>
                      {msg.corrections.map((c, j) => (
                        <p key={j}>
                          {c.text && c.correction ? (
                            <><span className="line-through">{c.text}</span> → <strong>{c.correction}</strong></>
                          ) : null}
                          {c.note ? <span className="block text-amber-700">{c.note}</span> : null}
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
                  className={`px-4 py-3 rounded-lg border font-medium ${listening ? 'bg-red-50 border-red-300 text-red-600' : 'hover:bg-gray-50'}`}
                  title="Speak your answer">
                  {listening ? '🎙️...' : '🎤'}
                </button>
              )}
              <input value={input} onChange={e => setInput(e.target.value)}
                className="flex-1 border rounded-lg px-4 py-3" placeholder="Type or tap mic to speak..." disabled={loading} />
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
