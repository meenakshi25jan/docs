'use client';

import { useEffect, useState } from 'react';
import { api } from '@/lib/api';

interface AdminSummary {
  tenant_id: string;
  user_count: number;
  learner_count: number;
  active_learners_7d: number;
  lessons_completed_30d: number;
  avg_governance_score?: number | null;
  warning_count_30d: number;
  grounding_fallback_rate?: number | null;
  plan_tier: string;
  is_active: boolean;
}

interface HealthData {
  status: string;
  database: string;
  database_latency_ms?: number | null;
  ai_provider: string;
  ai_configured: boolean;
  auth_hashing: string;
  version: string;
  checks?: Array<{ name: string; status: string; detail?: string | null }>;
}

export default function AdminDashboard() {
  const [summary, setSummary] = useState<AdminSummary | null>(null);
  const [health, setHealth] = useState<HealthData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [forbidden, setForbidden] = useState(false);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);
    setForbidden(false);
    Promise.all([
      api.operations.adminSummary(),
      api.operations.health(),
    ])
      .then(([summaryData, healthData]) => {
        if (!cancelled) {
          setSummary(summaryData as AdminSummary);
          setHealth(healthData as HealthData);
        }
      })
      .catch((err) => {
        if (!cancelled) {
          const msg = err instanceof Error ? err.message : 'Failed to load admin dashboard';
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

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b px-6 py-4">
        <h1 className="text-xl font-bold text-primary">Admin Dashboard</h1>
      </header>
      <main className="max-w-7xl mx-auto px-6 py-8">
        {loading && (
          <p className="text-gray-500 text-center py-12">Loading tenant operations…</p>
        )}

        {forbidden && (
          <div className="bg-amber-50 border border-amber-200 text-amber-900 rounded-xl p-4 mb-6">
            You need an admin account to view this dashboard.
          </div>
        )}

        {error && !loading && !forbidden && (
          <div className="bg-red-50 border border-red-200 text-red-700 rounded-xl p-4 mb-6">{error}</div>
        )}

        {!loading && !error && summary && (
          <>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
              {[
                { label: 'Users', value: String(summary.user_count) },
                { label: 'Learners', value: String(summary.learner_count) },
                { label: 'Active Learners (7d)', value: String(summary.active_learners_7d) },
                { label: 'Lessons (30d)', value: String(summary.lessons_completed_30d) },
              ].map((s) => (
                <div key={s.label} className="bg-white rounded-xl p-5 border">
                  <p className="text-sm text-gray-500">{s.label}</p>
                  <p className="text-3xl font-bold">{s.value}</p>
                </div>
              ))}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
              <div className="bg-white rounded-xl p-5 border">
                <p className="text-sm text-gray-500">Avg Governance Score</p>
                <p className="text-2xl font-bold">
                  {summary.avg_governance_score != null
                    ? `${Math.round(summary.avg_governance_score * 100)}%`
                    : '—'}
                </p>
              </div>
              <div className="bg-white rounded-xl p-5 border">
                <p className="text-sm text-gray-500">Warnings (30d)</p>
                <p className="text-2xl font-bold">{summary.warning_count_30d}</p>
              </div>
              <div className="bg-white rounded-xl p-5 border">
                <p className="text-sm text-gray-500">Grounding Fallback Rate</p>
                <p className="text-2xl font-bold">
                  {summary.grounding_fallback_rate != null
                    ? `${Math.round(summary.grounding_fallback_rate * 100)}%`
                    : '—'}
                </p>
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="bg-white rounded-xl p-6 border">
                <h2 className="font-semibold mb-4">Tenant</h2>
                <dl className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <dt className="text-gray-500">Plan</dt>
                    <dd className="font-medium capitalize">{summary.plan_tier}</dd>
                  </div>
                  <div className="flex justify-between">
                    <dt className="text-gray-500">Status</dt>
                    <dd className="font-medium">{summary.is_active ? 'Active' : 'Inactive'}</dd>
                  </div>
                </dl>
              </div>

              {health && (
                <div className="bg-white rounded-xl p-6 border">
                  <h2 className="font-semibold mb-4">Operational Health</h2>
                  <p className="text-sm mb-3">
                    Overall: <span className="font-medium capitalize">{health.status}</span>
                    {health.version && <span className="text-gray-500 ml-2">v{health.version}</span>}
                  </p>
                  <div className="space-y-2 text-sm">
                    {(health.checks ?? [
                      { name: 'database', status: health.database },
                      { name: 'ai_provider', status: health.ai_provider },
                      { name: 'auth_hashing', status: health.auth_hashing },
                    ]).map((check) => (
                      <div key={check.name} className="flex items-center justify-between">
                        <span>{check.name}</span>
                        <span className={
                          ['ok', 'reachable', 'configured', 'healthy'].includes(check.status)
                            ? 'text-green-600'
                            : 'text-gray-600'
                        }>
                          {check.status}
                          {check.name === 'database' && health.database_latency_ms != null
                            ? ` (${health.database_latency_ms}ms)`
                            : ''}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </>
        )}
      </main>
    </div>
  );
}
