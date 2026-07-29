'use client';

import { Suspense, useEffect, useState } from 'react';
import Link from 'next/link';
import { useSearchParams } from 'next/navigation';
import { api, saveTokens } from '@/lib/api';

function LoginForm() {
  const searchParams = useSearchParams();
  const [form, setForm] = useState({ email: '', password: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (searchParams.get('expired') === '1') {
      setError('Your session expired. Please log in again.');
    }
  }, [searchParams]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const res = await api.auth.login(form) as { tokens: { access_token: string; refresh_token: string } };
      saveTokens(res.tokens.access_token, res.tokens.refresh_token);
      window.location.href = '/dashboard/student';
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
      <div className="bg-white rounded-xl shadow-sm border p-8 w-full max-w-md">
        <h1 className="text-2xl font-bold mb-2">Welcome Back</h1>
        <p className="text-gray-500 text-sm mb-6">Login to continue learning</p>
        <form onSubmit={handleSubmit} className="space-y-4">
          <input type="email" className="border rounded-lg px-3 py-2 w-full" placeholder="Email" required
            value={form.email} onChange={e => setForm({ ...form, email: e.target.value })} />
          <input type="password" className="border rounded-lg px-3 py-2 w-full" placeholder="Password" required
            value={form.password} onChange={e => setForm({ ...form, password: e.target.value })} />
          {error && <p className="text-red-500 text-sm">{error}</p>}
          <button type="submit" disabled={loading}
            className="w-full bg-blue-600 text-white py-2 rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50">
            {loading ? 'Logging in...' : 'Login'}
          </button>
        </form>
        <p className="text-sm text-center mt-4 text-gray-500">
          No account? <Link href="/register" className="text-blue-600">Register</Link>
        </p>
      </div>
    </div>
  );
}

export default function LoginPage() {
  return (
    <Suspense fallback={<div className="min-h-screen bg-gray-50" />}>
      <LoginForm />
    </Suspense>
  );
}
