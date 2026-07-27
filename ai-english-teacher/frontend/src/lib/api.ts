// Use same-origin /api/v1 proxy (see next.config.js rewrites) unless overridden.
const API_URL = process.env.NEXT_PUBLIC_API_URL || '/api/v1';

interface RequestOptions {
  method?: string;
  body?: unknown;
  token?: string;
}

async function request<T>(endpoint: string, options: RequestOptions = {}): Promise<T> {
  const headers: Record<string, string> = { 'Content-Type': 'application/json' };
  const token = options.token || (typeof window !== 'undefined' ? localStorage.getItem('access_token') : null);
  if (token) headers['Authorization'] = `Bearer ${token}`;

  let res: Response;
  try {
    res = await fetch(`${API_URL}${endpoint}`, {
      method: options.method || 'GET',
      headers,
      body: options.body ? JSON.stringify(options.body) : undefined,
    });
  } catch {
    throw new Error(
      'Cannot reach the API. On Render free tier the server may be waking up — wait 30–60 seconds and try again.'
    );
  }

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: 'Request failed' }));
    const detail = error.detail;
    throw new Error(
      typeof detail === 'string' ? detail : Array.isArray(detail) ? detail[0]?.msg || 'Request failed' : `HTTP ${res.status}`
    );
  }
  return res.json();
}

export const api = {
  auth: {
    register: (data: { email: string; password: string; first_name: string; last_name: string }) =>
      request('/auth/register', { method: 'POST', body: data }),
    login: (data: { email: string; password: string }) =>
      request('/auth/login', { method: 'POST', body: data }),
    me: () => request('/auth/me'),
  },
  assessments: {
    create: (data: { assessment_type: string; config?: Record<string, unknown> }) =>
      request('/assessments', { method: 'POST', body: data }),
    list: () => request('/assessments'),
    submit: (id: string, answers: unknown[]) =>
      request(`/assessments/${id}/submit`, { method: 'POST', body: { answers } }),
    results: (id: string) => request(`/assessments/${id}/results`),
  },
  conversations: {
    start: (data: { scenario: string; context?: Record<string, unknown> }) =>
      request('/conversations', { method: 'POST', body: data }),
    sendMessage: (id: string, content: string) =>
      request(`/conversations/${id}/messages`, { method: 'POST', body: { content } }),
  },
  writing: {
    submit: (data: { prompt: string; content: string; task_type?: string }) =>
      request('/writing/submit', { method: 'POST', body: data }),
  },
  dashboard: {
    student: () => request('/dashboard/student'),
    teacher: () => request('/dashboard/teacher'),
    admin: () => request('/dashboard/admin'),
  },
  reports: {
    generate: (data: { report_type: string; period_days?: number }) =>
      request('/reports/generate', { method: 'POST', body: data }),
  },
  learningPlans: {
    create: (data: { duration_weeks: number; target_exam: string; target_score: number }) =>
      request('/learning-plans', { method: 'POST', body: data }),
  },
};
