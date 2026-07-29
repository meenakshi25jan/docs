'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { api, getAccessToken } from '@/lib/api';

export default function AssessmentPage() {
  const [assessmentId, setAssessmentId] = useState<string | null>(null);
  const [answers, setAnswers] = useState({
    grammar: 'She has been working here for five years.',
    vocabulary: 'The implementation of sustainable practices is crucial for environmental preservation.',
    writing: 'Technology has significantly transformed modern education by providing access to vast resources.',
  });
  const [results, setResults] = useState<Record<string, unknown> | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!getAccessToken()) {
      window.location.href = '/login?expired=1';
    }
  }, []);

  async function startAssessment() {
    setLoading(true);
    try {
      const res = await api.assessments.create({ assessment_type: 'full' }) as { id: string };
      setAssessmentId(res.id);
      setResults(null);
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to start. Please login first.');
    } finally {
      setLoading(false);
    }
  }

  async function submitAssessment() {
    if (!assessmentId) return;
    setLoading(true);
    try {
      const res = await api.assessments.submit(assessmentId, [
        { skill: 'grammar', question_id: 'g1', response: answers.grammar },
        { skill: 'vocabulary', question_id: 'v1', response: answers.vocabulary },
        { skill: 'writing', question_id: 'w1', response: answers.writing },
      ]);
      setResults(res as Record<string, unknown>);
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Submit failed');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b px-6 py-4">
        <Link href="/dashboard/student" className="text-blue-600 font-bold">← AI English Teacher</Link>
      </header>

      <main className="max-w-2xl mx-auto px-4 py-8">
        <h1 className="text-2xl font-bold mb-6">English Placement Assessment</h1>

        {!assessmentId ? (
          <div className="bg-white rounded-xl border p-6">
            <p className="text-gray-600 mb-4">Test your grammar, vocabulary, and writing skills. Get CEFR, IELTS, and PTE estimates.</p>
            <button onClick={startAssessment} disabled={loading}
              className="bg-blue-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50">
              {loading ? 'Starting...' : 'Start Assessment'}
            </button>
          </div>
        ) : !results ? (
          <div className="bg-white rounded-xl border p-6 space-y-6">
            <div>
              <label className="block text-sm font-medium mb-2">Grammar — Correct this sentence:</label>
              <p className="text-sm text-gray-500 mb-2">&quot;She have been working here for five year.&quot;</p>
              <textarea className="w-full border rounded-lg p-3 h-20" value={answers.grammar}
                onChange={e => setAnswers({ ...answers, grammar: e.target.value })} />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Vocabulary — Use &quot;nevertheless&quot; in a sentence:</label>
              <textarea className="w-full border rounded-lg p-3 h-20" value={answers.vocabulary}
                onChange={e => setAnswers({ ...answers, vocabulary: e.target.value })} />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Writing — Write about technology in education (2-3 sentences):</label>
              <textarea className="w-full border rounded-lg p-3 h-24" value={answers.writing}
                onChange={e => setAnswers({ ...answers, writing: e.target.value })} />
            </div>
            <button onClick={submitAssessment} disabled={loading}
              className="w-full bg-blue-600 text-white py-3 rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50">
              {loading ? 'AI is scoring...' : 'Submit for AI Scoring'}
            </button>
          </div>
        ) : (
          <div className="bg-white rounded-xl border p-6">
            <h2 className="text-xl font-bold mb-4 text-green-600">Assessment Complete!</h2>
            <pre className="bg-gray-50 rounded-lg p-4 text-sm overflow-auto">
              {JSON.stringify(results, null, 2)}
            </pre>
            <Link href="/dashboard/student" className="inline-block mt-4 text-blue-600">View Dashboard →</Link>
          </div>
        )}
      </main>
    </div>
  );
}
