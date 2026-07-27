'use client';

import { useState } from 'react';
import Link from 'next/link';
import { api } from '@/lib/api';

export default function RegisterPage() {
  const [form, setForm] = useState({ email: '', password: '', first_name: '', last_name: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const res = await api.auth.register(form) as { tokens: { access_token: string } };
      localStorage.setItem('access_token', res.tokens.access_token);
      window.location.href = '/dashboard/student';
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Registration failed');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
      <div className="bg-white rounded-xl shadow-sm border p-8 w-full max-w-md">
        <h1 className="text-2xl font-bold mb-2">Create Account</h1>
        <p className="text-gray-500 text-sm mb-6">Start your English learning journey</p>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-3">
            <input className="border rounded-lg px-3 py-2" placeholder="First name" required
              value={form.first_name} onChange={e => setForm({ ...form, first_name: e.target.value })} />
            <input className="border rounded-lg px-3 py-2" placeholder="Last name" required
              value={form.last_name} onChange={e => setForm({ ...form, last_name: e.target.value })} />
          </div>
          <input type="email" className="border rounded-lg px-3 py-2 w-full" placeholder="Email" required
            value={form.email} onChange={e => setForm({ ...form, email: e.target.value })} />
          <input type="password" className="border rounded-lg px-3 py-2 w-full" placeholder="Password (min 8 chars)" required minLength={8}
            value={form.password} onChange={e => setForm({ ...form, password: e.target.value })} />
          {error && <p className="text-red-500 text-sm">{error}</p>}
          <button type="submit" disabled={loading}
            className="w-full bg-blue-600 text-white py-2 rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50">
            {loading ? 'Creating...' : 'Register'}
          </button>
        </form>
        <p className="text-sm text-center mt-4 text-gray-500">
          Already have an account? <Link href="/login" className="text-blue-600">Login</Link>
        </p>
      </div>
    </div>
  );
}
