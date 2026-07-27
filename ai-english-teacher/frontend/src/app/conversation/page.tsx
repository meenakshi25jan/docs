'use client';

import { useState } from 'react';
import Link from 'next/link';
import { api } from '@/lib/api';

const SCENARIOS = [
  { id: 'job_interview', label: 'Job Interview' },
  { id: 'restaurant', label: 'Restaurant Order' },
  { id: 'travel', label: 'Travel & Tourism' },
  { id: 'business_meeting', label: 'Business Meeting' },
];

interface Message {
  role: string;
  content: string;
}

export default function ConversationPage() {
  const [scenario, setScenario] = useState('job_interview');
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [started, setStarted] = useState(false);

  async function startConversation() {
    setLoading(true);
    try {
      const res = await api.conversations.start({ scenario }) as {
        id: string;
        initial_message: { content: string };
      };
      setConversationId(res.id);
      setMessages([{ role: 'assistant', content: res.initial_message.content }]);
      setStarted(true);
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to start. Please login first.');
    } finally {
      setLoading(false);
    }
  }

  async function sendMessage(e: React.FormEvent) {
    e.preventDefault();
    if (!input.trim() || !conversationId) return;
    setLoading(true);
    const userMsg = input.trim();
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: userMsg }]);
    try {
      const res = await api.conversations.sendMessage(conversationId, userMsg) as {
        assistant_message: { content: string };
      };
      setMessages(prev => [...prev, { role: 'assistant', content: res.assistant_message.content }]);
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to send message');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <header className="bg-white border-b px-6 py-4 flex items-center justify-between">
        <Link href="/dashboard/student" className="text-blue-600 font-bold">← AI English Teacher</Link>
        <span className="text-sm text-gray-500">AI Role-Play Practice</span>
      </header>

      <main className="flex-1 max-w-2xl mx-auto w-full px-4 py-6 flex flex-col">
        {!started ? (
          <div className="bg-white rounded-xl border p-6">
            <h1 className="text-xl font-bold mb-4">Choose a Scenario</h1>
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
                <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`max-w-[80%] px-4 py-3 rounded-2xl text-sm ${
                    msg.role === 'user' ? 'bg-blue-600 text-white' : 'bg-white border'
                  }`}>
                    {msg.content}
                  </div>
                </div>
              ))}
            </div>
            <form onSubmit={sendMessage} className="flex gap-2">
              <input value={input} onChange={e => setInput(e.target.value)}
                className="flex-1 border rounded-lg px-4 py-3" placeholder="Type your response..." disabled={loading} />
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
