'use client';

import Link from 'next/link';
import { useCallback, useEffect, useState } from 'react';
import { api } from '@/lib/api';
import { useVoice } from '@/hooks/useVoice';

interface Grade {
  grade: number;
  label: string;
  age: string;
  cefr: string;
  lesson_count: number;
}

interface Lesson {
  id: string;
  title: string;
  rule: string;
}

interface Correction {
  wrong?: string;
  correct?: string;
  tip?: string;
  text?: string;
  correction?: string;
}

interface TeacherReply {
  response?: string;
  rule_explained?: string;
  corrections?: Correction[];
  practice_prompt?: string;
  encouragement?: string;
  score_comment?: string;
}

export default function GrammarClassPage() {
  const [grades, setGrades] = useState<Grade[]>([]);
  const [grade, setGrade] = useState<number>(8);
  const [lessons, setLessons] = useState<Lesson[]>([]);
  const [lessonId, setLessonId] = useState<string>('');
  const [intro, setIntro] = useState<TeacherReply | null>(null);
  const [lastReply, setLastReply] = useState<TeacherReply | null>(null);
  const [grammarScore, setGrammarScore] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);
  const [textInput, setTextInput] = useState('');
  const { listen, speak, listening, sttSupported, ttsSupported } = useVoice();

  const speakSlow = useCallback((text: string) => {
    if (!ttsSupported || !text) return;
    window.speechSynthesis.cancel();
    const u = new SpeechSynthesisUtterance(text);
    u.lang = 'en-US';
    u.rate = 0.85;
    window.speechSynthesis.speak(u);
  }, [ttsSupported]);

  useEffect(() => {
    api.grammar.grades().then((data) => setGrades(data as Grade[])).catch(() => {});
  }, []);

  useEffect(() => {
    if (!grade) return;
    api.grammar.lessons(grade).then((data) => {
      const res = data as { lessons: Lesson[] };
      setLessons(res.lessons);
      if (res.lessons[0]) setLessonId(res.lessons[0].id);
    }).catch(() => {});
  }, [grade]);

  async function startLesson() {
    if (!lessonId) return;
    setLoading(true);
    setLastReply(null);
    setGrammarScore(null);
    try {
      const res = await api.grammar.intro(grade, lessonId) as { intro: TeacherReply };
      setIntro(res.intro);
      if (res.intro?.response) speakSlow(res.intro.response);
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Could not start lesson');
    } finally {
      setLoading(false);
    }
  }

  async function submitPractice(spoken: string) {
    if (!spoken.trim() || !lessonId) return;
    setLoading(true);
    try {
      const res = await api.grammar.practice({
        grade,
        lesson_id: lessonId,
        transcript: spoken.trim(),
      }) as {
        grammar_score: number;
        teacher: TeacherReply;
        errors: Correction[];
      };
      setGrammarScore(res.grammar_score);
      setLastReply(res.teacher);
      const toSpeak = [res.teacher?.response, res.teacher?.encouragement].filter(Boolean).join(' ');
      if (toSpeak) speakSlow(toSpeak);
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Practice failed');
    } finally {
      setLoading(false);
    }
  }

  function handleMic() {
    listen(
      (text) => {
        setTextInput(text);
        submitPractice(text);
      },
      (msg) => alert(msg)
    );
  }

  const activeLesson = lessons.find((l) => l.id === lessonId);

  return (
    <div className="min-h-screen bg-gradient-to-b from-amber-50 to-orange-50">
      <header className="bg-white border-b px-4 py-3 flex items-center justify-between">
        <Link href="/dashboard/student" className="text-blue-600 font-bold">← Grammar Class</Link>
        <span className="text-sm text-gray-500">Grades 5–12 · Voice teacher</span>
      </header>

      <main className="max-w-2xl mx-auto p-4 space-y-6">
        <section className="bg-white rounded-2xl p-5 shadow-sm border">
          <h1 className="text-2xl font-bold text-gray-900 mb-1">📚 Grammar AI Teacher</h1>
          <p className="text-gray-600 text-sm mb-4">
            Speak or type — get gentle corrections and mini lessons. Best in Chrome with microphone.
          </p>

          <label className="block text-sm font-medium mb-1">Your grade</label>
          <select
            className="w-full border rounded-lg p-2 mb-4"
            value={grade}
            onChange={(e) => setGrade(Number(e.target.value))}
          >
            {grades.map((g) => (
              <option key={g.grade} value={g.grade}>
                {g.label} (ages {g.age})
              </option>
            ))}
          </select>

          <label className="block text-sm font-medium mb-1">Grammar topic</label>
          <select
            className="w-full border rounded-lg p-2 mb-4"
            value={lessonId}
            onChange={(e) => setLessonId(e.target.value)}
          >
            {lessons.map((l) => (
              <option key={l.id} value={l.id}>{l.title}</option>
            ))}
          </select>

          {activeLesson && (
            <p className="text-sm bg-amber-50 border border-amber-100 rounded-lg p-3 mb-4">
              <strong>Rule:</strong> {activeLesson.rule}
            </p>
          )}

          <button
            type="button"
            onClick={startLesson}
            disabled={loading || !lessonId}
            className="w-full py-3 bg-amber-500 text-white rounded-xl font-semibold hover:bg-amber-600 disabled:opacity-50"
          >
            {loading ? 'Loading...' : '▶ Start voice lesson'}
          </button>
        </section>

        {intro && (
          <section className="bg-white rounded-2xl p-5 shadow-sm border border-blue-100">
            <h2 className="font-semibold text-blue-800 mb-2">Teacher says</h2>
            <p className="text-gray-800 mb-2">{intro.response}</p>
            {intro.rule_explained && (
              <p className="text-sm text-gray-600 bg-gray-50 p-3 rounded-lg">{intro.rule_explained}</p>
            )}
            {intro.practice_prompt && (
              <p className="mt-3 text-sm font-medium text-amber-700">Try: {intro.practice_prompt}</p>
            )}
          </section>
        )}

        <section className="bg-white rounded-2xl p-5 shadow-sm border">
          <h2 className="font-semibold mb-3">Your turn — speak or type</h2>
          <div className="flex gap-2 mb-3">
            <input
              className="flex-1 border rounded-lg px-3 py-2"
              placeholder="Type a sentence..."
              value={textInput}
              onChange={(e) => setTextInput(e.target.value)}
              disabled={loading}
            />
            <button
              type="button"
              onClick={() => submitPractice(textInput)}
              disabled={loading}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg"
            >
              Send
            </button>
          </div>
          <button
            type="button"
            onClick={handleMic}
            disabled={loading || listening}
            className={`w-full py-4 rounded-xl text-lg font-bold ${
              listening ? 'bg-red-500 text-white animate-pulse' : 'bg-green-500 text-white hover:bg-green-600'
            }`}
          >
            {listening ? '🎤 Listening...' : '🎤 Tap to speak'}
          </button>
          {!sttSupported && (
            <p className="text-xs text-gray-500 mt-2">Use Chrome or Edge for voice input.</p>
          )}
        </section>

        {lastReply && (
          <section className="bg-white rounded-2xl p-5 shadow-sm border border-green-100">
            <div className="flex justify-between items-center mb-2">
              <h2 className="font-semibold text-green-800">Feedback</h2>
              {grammarScore != null && (
                <span className="text-sm bg-green-100 text-green-800 px-2 py-1 rounded-full">
                  Grammar: {Math.round(grammarScore)}/100
                </span>
              )}
            </div>
            <p className="text-gray-800 mb-3">{lastReply.response}</p>
            {lastReply.corrections && lastReply.corrections.length > 0 && (
              <ul className="space-y-2 mb-3">
                {lastReply.corrections.map((c, i) => (
                  <li key={i} className="text-sm bg-red-50 border border-red-100 rounded-lg p-2">
                    ❌ {(c.wrong || c.text) ?? 'error'} → ✅ {(c.correct || c.correction) ?? 'fix'}
                    {c.tip && <span className="block text-gray-600 mt-1">💡 {c.tip}</span>}
                  </li>
                ))}
              </ul>
            )}
            {lastReply.practice_prompt && (
              <p className="text-sm font-medium text-amber-700">Next: {lastReply.practice_prompt}</p>
            )}
            {lastReply.encouragement && (
              <p className="text-sm text-green-700 mt-2">🌟 {lastReply.encouragement}</p>
            )}
          </section>
        )}
      </main>
    </div>
  );
}
