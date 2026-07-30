'use client';

import { useEffect, useState } from 'react';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  RadarChart, PolarGrid, PolarAngleAxis, Radar,
} from 'recharts';
import { api } from '@/lib/api';

interface SkillDetail {
  score: number;
  level?: string | null;
  trend?: string | null;
}

interface SummaryData {
  profile: {
    current_level?: string | null;
    cefr_level?: string | null;
    ielts_estimate?: number | null;
    pte_estimate?: number | null;
    confidence_score?: number | null;
    learning_goal?: string | null;
    name?: string | null;
  };
  skills: Record<string, SkillDetail>;
  top_mistakes: Array<{
    mistake_type: string;
    original_text: string;
    corrected_text?: string | null;
    severity: string;
    occurrence_count: number;
  }>;
  latest_progress?: {
    snapshot_at?: string | null;
    cefr_estimate?: string | null;
    confidence_score?: number | null;
  } | null;
  strongest_skill?: string | null;
  weakest_skill?: string | null;
  recommended_next_focus: string;
  has_data: boolean;
}

const SKILL_LABELS: Record<string, string> = {
  grammar: 'Grammar',
  vocabulary: 'Vocabulary',
  writing: 'Writing',
  reading: 'Reading',
  listening: 'Listening',
  speaking: 'Speaking',
  pronunciation: 'Pronunciation',
  fluency: 'Fluency',
};

const SKILL_COLORS: Record<string, string> = {
  grammar: '#3b82f6',
  vocabulary: '#8b5cf6',
  writing: '#06b6d4',
  reading: '#10b981',
  listening: '#f59e0b',
  speaking: '#ef4444',
  pronunciation: '#ec4899',
  fluency: '#f97316',
};

function SkillCard({ label, score, color, trend }: { label: string; score: number; color: string; trend?: string | null }) {
  const trendIcon = trend === 'up' ? '↑' : trend === 'down' ? '↓' : trend === 'stable' ? '→' : '';
  return (
    <div className="bg-white rounded-xl p-5 border shadow-sm">
      <p className="text-sm text-gray-500 mb-1">{label} {trendIcon && <span className="text-xs">{trendIcon}</span>}</p>
      <p className="text-3xl font-bold" style={{ color }}>{Math.round(score)}</p>
      <div className="mt-2 h-2 bg-gray-100 rounded-full">
        <div className="h-2 rounded-full" style={{ width: `${Math.min(score, 100)}%`, backgroundColor: color }} />
      </div>
    </div>
  );
}

export default function StudentDashboard() {
  const [summary, setSummary] = useState<SummaryData | null>(null);
  const [recommendation, setRecommendation] = useState<{
    lesson_id: string;
    title: string;
    reason: string;
    route: string;
    skill_focus: string;
  } | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);
    Promise.all([
      api.studentIntelligence.summary(),
      api.curriculum.recommended().catch(() => null),
    ])
      .then(([summaryData, recData]) => {
        if (!cancelled) {
          setSummary(summaryData as SummaryData);
          if (recData && typeof recData === 'object' && 'primary' in recData) {
            const primary = (recData as { primary: typeof recommendation }).primary;
            if (primary) setRecommendation(primary);
          }
        }
      })
      .catch((err) => {
        if (!cancelled) setError(err instanceof Error ? err.message : 'Failed to load dashboard');
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => { cancelled = true; };
  }, []);

  const profile = summary?.profile;
  const cefr = profile?.cefr_level || profile?.current_level || '—';
  const ielts = profile?.ielts_estimate;
  const pte = profile?.pte_estimate;
  const skills = summary?.skills || {};

  const radarData = Object.entries(skills)
    .filter(([key]) => SKILL_LABELS[key])
    .map(([skill, detail]) => ({
      skill: SKILL_LABELS[skill] || skill,
      score: detail?.score ?? 0,
    }));

  const focusLink = (() => {
    const focus = summary?.recommended_next_focus || '';
    if (focus.includes('grammar')) return '/grammar-class';
    if (focus.includes('conversation') || focus.includes('pronunciation')) return '/conversation';
    if (focus.includes('placement')) return '/assessment';
    return '/conversation';
  })();

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <h1 className="text-xl font-bold text-primary">AI English Teacher</h1>
          <nav className="flex gap-6 text-sm">
            <a href="/dashboard/student" className="font-medium text-primary">Dashboard</a>
            <a href="/assessment" className="text-gray-600 hover:text-primary">Assessment</a>
            <a href="/grammar-class" className="text-gray-600 hover:text-primary">Grammar Class</a>
            <a href="/conversation" className="text-gray-600 hover:text-primary">Practice</a>
          </nav>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-8">
        <div className="mb-8">
          <h2 className="text-2xl font-bold">
            {profile?.name ? `${profile.name}'s Progress` : 'Student Dashboard'}
          </h2>
          <p className="text-gray-500">Your AI Teacher learning intelligence summary</p>
        </div>

        {loading && (
          <div className="text-center py-16 text-gray-500">Loading your learning profile…</div>
        )}

        {error && !loading && (
          <div className="bg-red-50 border border-red-200 text-red-700 rounded-xl p-4 mb-6">
            {error}
          </div>
        )}

        {!loading && !error && summary && !summary.has_data && (
          <div className="bg-blue-50 border border-blue-200 rounded-xl p-6 mb-8 text-center">
            <p className="text-blue-900 font-medium mb-2">Welcome! Start your learning journey.</p>
            <p className="text-blue-700 text-sm mb-4">Take a placement assessment or practice speaking to build your profile.</p>
            <a href="/assessment" className="inline-block bg-primary text-white px-4 py-2 rounded-lg text-sm font-medium">
              Start placement assessment
            </a>
          </div>
        )}

        {!loading && !error && summary && (
          <>
            {/* Proficiency + recommended focus */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
              <div className="bg-primary text-white rounded-xl p-6">
                <p className="text-sm opacity-80">CEFR Level</p>
                <p className="text-4xl font-bold">{cefr}</p>
              </div>
              {ielts != null && (
                <div className="bg-indigo-600 text-white rounded-xl p-6">
                  <p className="text-sm opacity-80">IELTS Estimate</p>
                  <p className="text-4xl font-bold">{ielts}</p>
                </div>
              )}
              {pte != null && (
                <div className="bg-violet-600 text-white rounded-xl p-6">
                  <p className="text-sm opacity-80">PTE Estimate</p>
                  <p className="text-4xl font-bold">{pte}</p>
                </div>
              )}
              <div className="bg-emerald-600 text-white rounded-xl p-6">
                <p className="text-sm opacity-80">Recommended Next Focus</p>
                <p className="text-lg font-semibold mt-1 capitalize">{summary.recommended_next_focus}</p>
                <a href={focusLink} className="text-xs underline opacity-90 mt-2 block">Start practice →</a>
              </div>
            </div>

            {recommendation && (
              <div className="bg-white rounded-xl border p-6 mb-8 shadow-sm">
                <h3 className="font-semibold text-lg mb-1">Recommended Next Lesson</h3>
                <p className="text-gray-800 font-medium">{recommendation.title}</p>
                <p className="text-sm text-gray-600 mt-2">{recommendation.reason}</p>
                <p className="text-xs text-gray-500 mt-1 capitalize">Skill focus: {recommendation.skill_focus}</p>
                <a
                  href={recommendation.route.startsWith('/') ? recommendation.route : `/${recommendation.route}`}
                  className="inline-block mt-4 bg-primary text-white px-4 py-2 rounded-lg text-sm font-medium"
                >
                  Start lesson →
                </a>
              </div>
            )}

            {profile?.confidence_score != null && (
              <div className="bg-white rounded-xl border p-4 mb-8 text-sm text-gray-600">
                Confidence score: <span className="font-semibold text-gray-900">{Math.round(profile.confidence_score * 100)}%</span>
                {summary.latest_progress?.snapshot_at && (
                  <span className="ml-4">Last updated: {new Date(summary.latest_progress.snapshot_at).toLocaleDateString()}</span>
                )}
              </div>
            )}

            {/* Skill grid */}
            <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-4 mb-8">
              {Object.entries(SKILL_LABELS).map(([key, label]) => (
                <SkillCard
                  key={key}
                  label={label}
                  score={skills[key]?.score ?? 0}
                  color={SKILL_COLORS[key]}
                  trend={skills[key]?.trend}
                />
              ))}
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
              {/* Recent mistakes */}
              <div className="bg-white rounded-xl p-6 border shadow-sm">
                <h3 className="font-semibold mb-4">Recent Mistakes</h3>
                {summary.top_mistakes.length === 0 ? (
                  <p className="text-gray-500 text-sm">No tracked mistakes yet — great work!</p>
                ) : (
                  <ul className="space-y-3">
                    {summary.top_mistakes.map((m, i) => (
                      <li key={i} className="text-sm border-b pb-2 last:border-0">
                        <span className="text-gray-500">{m.mistake_type}</span>
                        <p className="text-red-600">{m.original_text}</p>
                        {m.corrected_text && <p className="text-green-700">→ {m.corrected_text}</p>}
                        <span className="text-xs text-gray-400">×{m.occurrence_count} · {m.severity}</span>
                      </li>
                    ))}
                  </ul>
                )}
              </div>

              {/* Progress snapshot summary */}
              <div className="bg-white rounded-xl p-6 border shadow-sm">
                <h3 className="font-semibold mb-4">Progress Snapshot</h3>
                {summary.latest_progress ? (
                  <dl className="space-y-2 text-sm">
                    {summary.latest_progress.cefr_estimate && (
                      <div className="flex justify-between"><dt className="text-gray-500">CEFR</dt><dd className="font-medium">{summary.latest_progress.cefr_estimate}</dd></div>
                    )}
                    {summary.strongest_skill && (
                      <div className="flex justify-between"><dt className="text-gray-500">Strongest</dt><dd className="font-medium capitalize">{summary.strongest_skill}</dd></div>
                    )}
                    {summary.weakest_skill && (
                      <div className="flex justify-between"><dt className="text-gray-500">Needs work</dt><dd className="font-medium capitalize">{summary.weakest_skill}</dd></div>
                    )}
                    {profile?.learning_goal && (
                      <div className="flex justify-between"><dt className="text-gray-500">Goal</dt><dd className="font-medium">{profile.learning_goal}</dd></div>
                    )}
                  </dl>
                ) : (
                  <p className="text-gray-500 text-sm">Complete a lesson or assessment to see progress snapshots.</p>
                )}
              </div>
            </div>

            {/* Radar chart */}
            {radarData.some((d) => d.score > 0) && (
              <div className="bg-white rounded-xl p-6 border shadow-sm">
                <h3 className="font-semibold mb-4">Skill Radar</h3>
                <ResponsiveContainer width="100%" height={300}>
                  <RadarChart data={radarData}>
                    <PolarGrid />
                    <PolarAngleAxis dataKey="skill" />
                    <Radar dataKey="score" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.3} />
                  </RadarChart>
                </ResponsiveContainer>
              </div>
            )}
          </>
        )}
      </main>
    </div>
  );
}
