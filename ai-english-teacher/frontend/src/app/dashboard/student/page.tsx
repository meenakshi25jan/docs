'use client';

import { useEffect, useState } from 'react';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  RadarChart, PolarGrid, PolarAngleAxis, Radar, Legend,
} from 'recharts';

interface DashboardData {
  learner: { current_cefr: string; ielts_estimate: number; pte_estimate: number };
  skill_scores: Record<string, number>;
}

const MOCK_TREND = [
  { month: 'Jan', grammar: 60, vocabulary: 55, speaking: 50, writing: 58, ielts: 5.5 },
  { month: 'Feb', grammar: 65, vocabulary: 60, speaking: 55, writing: 62, ielts: 6.0 },
  { month: 'Mar', grammar: 70, vocabulary: 65, speaking: 60, writing: 68, ielts: 6.0 },
  { month: 'Apr', grammar: 75, vocabulary: 70, speaking: 65, writing: 72, ielts: 6.5 },
  { month: 'May', grammar: 78, vocabulary: 72, speaking: 68, writing: 75, ielts: 6.5 },
  { month: 'Jun', grammar: 80, vocabulary: 75, speaking: 70, writing: 78, ielts: 7.0 },
];

function SkillCard({ label, score, color }: { label: string; score: number; color: string }) {
  return (
    <div className="bg-white rounded-xl p-5 border shadow-sm">
      <p className="text-sm text-gray-500 mb-1">{label}</p>
      <p className="text-3xl font-bold" style={{ color }}>{score}</p>
      <div className="mt-2 h-2 bg-gray-100 rounded-full">
        <div className="h-2 rounded-full" style={{ width: `${score}%`, backgroundColor: color }} />
      </div>
    </div>
  );
}

export default function StudentDashboard() {
  const [data, setData] = useState<DashboardData | null>(null);

  useEffect(() => {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';
    fetch(`${apiUrl}/dashboard/student`, {
      headers: { Authorization: `Bearer ${localStorage.getItem('access_token') || ''}` },
    })
      .then((r) => r.ok ? r.json() : null)
      .then(setData)
      .catch(() => setData(null));
  }, []);

  const scores = data?.skill_scores || {
    grammar: 78, vocabulary: 72, writing: 75, reading: 80, listening: 70, speaking: 68,
  };

  const radarData = Object.entries(scores).map(([skill, score]) => ({ skill, score }));

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <h1 className="text-xl font-bold text-primary">AI English Teacher</h1>
          <nav className="flex gap-6 text-sm">
            <a href="/dashboard/student" className="font-medium text-primary">Dashboard</a>
            <a href="/assessment" className="text-gray-600 hover:text-primary">Assessment</a>
            <a href="/conversation" className="text-gray-600 hover:text-primary">Practice</a>
          </nav>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-8">
        <div className="mb-8">
          <h2 className="text-2xl font-bold">Student Dashboard</h2>
          <p className="text-gray-500">Track your English learning progress</p>
        </div>

        {/* Proficiency Estimates */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          <div className="bg-primary text-white rounded-xl p-6">
            <p className="text-sm opacity-80">CEFR Level</p>
            <p className="text-4xl font-bold">{data?.learner?.current_cefr || 'B2'}</p>
          </div>
          <div className="bg-indigo-600 text-white rounded-xl p-6">
            <p className="text-sm opacity-80">IELTS Estimate</p>
            <p className="text-4xl font-bold">{data?.learner?.ielts_estimate || 6.5}</p>
          </div>
          <div className="bg-violet-600 text-white rounded-xl p-6">
            <p className="text-sm opacity-80">PTE Estimate</p>
            <p className="text-4xl font-bold">{data?.learner?.pte_estimate || 58}</p>
          </div>
        </div>

        {/* Skill Scores */}
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-8">
          <SkillCard label="Grammar" score={scores.grammar} color="#3b82f6" />
          <SkillCard label="Vocabulary" score={scores.vocabulary} color="#8b5cf6" />
          <SkillCard label="Writing" score={scores.writing} color="#06b6d4" />
          <SkillCard label="Reading" score={scores.reading} color="#10b981" />
          <SkillCard label="Listening" score={scores.listening} color="#f59e0b" />
          <SkillCard label="Speaking" score={scores.speaking} color="#ef4444" />
        </div>

        {/* Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-white rounded-xl p-6 border shadow-sm">
            <h3 className="font-semibold mb-4">Skill Progress Trend</h3>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={MOCK_TREND}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis domain={[0, 100]} />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="grammar" stroke="#3b82f6" strokeWidth={2} />
                <Line type="monotone" dataKey="vocabulary" stroke="#8b5cf6" strokeWidth={2} />
                <Line type="monotone" dataKey="speaking" stroke="#ef4444" strokeWidth={2} />
                <Line type="monotone" dataKey="writing" stroke="#06b6d4" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </div>

          <div className="bg-white rounded-xl p-6 border shadow-sm">
            <h3 className="font-semibold mb-4">IELTS Prediction Trend</h3>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={MOCK_TREND}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis domain={[4, 9]} />
                <Tooltip />
                <Line type="monotone" dataKey="ielts" stroke="#4f46e5" strokeWidth={3} dot={{ r: 5 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>

          <div className="bg-white rounded-xl p-6 border shadow-sm lg:col-span-2">
            <h3 className="font-semibold mb-4">Skill Radar</h3>
            <ResponsiveContainer width="100%" height={300}>
              <RadarChart data={radarData}>
                <PolarGrid />
                <PolarAngleAxis dataKey="skill" />
                <Radar dataKey="score" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.3} />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </main>
    </div>
  );
}
