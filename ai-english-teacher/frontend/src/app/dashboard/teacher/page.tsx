'use client';

import { useEffect, useState } from 'react';
import { api } from '@/lib/api';

interface RosterEntry {
  learner_id: string;
  name?: string | null;
  email?: string | null;
  cefr_level?: string | null;
  weakest_skill?: string | null;
  last_activity_at?: string | null;
  lessons_completed_30d?: number;
  governance_avg_score?: number | null;
  status?: string;
  needs_attention?: boolean;
}

interface RosterData {
  learners: RosterEntry[];
  total: number;
  needs_attention_count: number;
  active_learners: number;
}

export default function TeacherDashboard() {
  const [roster, setRoster] = useState<RosterData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [forbidden, setForbidden] = useState(false);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);
    setForbidden(false);
    api.operations.teacherRoster()
      .then((data) => {
        if (!cancelled) setRoster(data as RosterData);
      })
      .catch((err) => {
        if (!cancelled) {
          const msg = err instanceof Error ? err.message : 'Failed to load roster';
          if (msg.includes('403') || msg.toLowerCase().includes('permission')) {
            setForbidden(true);
          }
          setError(msg);
        }
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => { cancelled = true; };
  }, []);

  const learners = roster?.learners ?? [];

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b px-6 py-4">
        <h1 className="text-xl font-bold text-primary">Teacher Dashboard</h1>
      </header>
      <main className="max-w-7xl mx-auto px-6 py-8">
        {loading && (
          <p className="text-gray-500 text-center py-12">Loading learner roster…</p>
        )}

        {forbidden && (
          <div className="bg-amber-50 border border-amber-200 text-amber-900 rounded-xl p-4 mb-6">
            You need a teacher account to view this dashboard. Log in with a teacher role.
          </div>
        )}

        {error && !loading && !forbidden && (
          <div className="bg-red-50 border border-red-200 text-red-700 rounded-xl p-4 mb-6">{error}</div>
        )}

        {!loading && !error && roster && (
          <>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
              {[
                { label: 'Class Size', value: String(roster.total) },
                { label: 'Active Learners (7d)', value: String(roster.active_learners) },
                { label: 'Needs Attention', value: String(roster.needs_attention_count) },
                { label: 'Lessons (30d avg)', value: roster.total > 0
                  ? String(Math.round(
                    learners.reduce((s, l) => s + (l.lessons_completed_30d ?? 0), 0) / roster.total
                  ))
                  : '0' },
              ].map((s) => (
                <div key={s.label} className="bg-white rounded-xl p-5 border">
                  <p className="text-sm text-gray-500">{s.label}</p>
                  <p className="text-3xl font-bold">{s.value}</p>
                </div>
              ))}
            </div>

            <div className="bg-white rounded-xl border shadow-sm overflow-hidden">
              <div className="px-6 py-4 border-b">
                <h2 className="font-semibold">Learner Roster</h2>
              </div>
              {learners.length === 0 ? (
                <p className="px-6 py-8 text-gray-500 text-sm">No learners in this tenant yet.</p>
              ) : (
                <table className="w-full text-sm">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left">Name</th>
                      <th className="px-6 py-3 text-left">CEFR</th>
                      <th className="px-6 py-3 text-left">Weakest Skill</th>
                      <th className="px-6 py-3 text-left">Lessons (30d)</th>
                      <th className="px-6 py-3 text-left">Governance</th>
                      <th className="px-6 py-3 text-left">Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {learners.map((l) => (
                      <tr key={l.learner_id} className="border-t">
                        <td className="px-6 py-3 font-medium">
                          {l.name || l.email || l.learner_id.slice(0, 8)}
                        </td>
                        <td className="px-6 py-3">{l.cefr_level ?? '—'}</td>
                        <td className="px-6 py-3 capitalize">{l.weakest_skill ?? '—'}</td>
                        <td className="px-6 py-3">{l.lessons_completed_30d ?? 0}</td>
                        <td className="px-6 py-3">
                          {l.governance_avg_score != null
                            ? `${Math.round(l.governance_avg_score * 100)}%`
                            : '—'}
                        </td>
                        <td className="px-6 py-3">
                          <span className={`px-2 py-1 rounded-full text-xs ${
                            l.needs_attention
                              ? 'bg-yellow-100 text-yellow-700'
                              : 'bg-green-100 text-green-700'
                          }`}>
                            {l.needs_attention ? 'Needs Attention' : 'On Track'}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          </>
        )}
      </main>
    </div>
  );
}
