// Use same-origin /api/v1 proxy (see next.config.js rewrites) unless overridden.
const API_URL = process.env.NEXT_PUBLIC_API_URL || '/api/v1';

interface RequestOptions {
  method?: string;
  body?: unknown;
  token?: string;
  skipAuthRedirect?: boolean;
}

export function saveTokens(accessToken: string, refreshToken?: string) {
  localStorage.setItem('access_token', accessToken);
  if (refreshToken) localStorage.setItem('refresh_token', refreshToken);
}

export function clearTokens() {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
}

export function getAccessToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('access_token');
}

async function refreshAccessToken(): Promise<string | null> {
  const refreshToken = localStorage.getItem('refresh_token');
  if (!refreshToken) return null;

  try {
    const res = await fetch(`${API_URL}/auth/refresh`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: refreshToken }),
    });
    if (!res.ok) return null;
    const data = await res.json() as { access_token: string; refresh_token: string };
    saveTokens(data.access_token, data.refresh_token);
    return data.access_token;
  } catch {
    return null;
  }
}

function redirectToLogin() {
  if (typeof window !== 'undefined' && !window.location.pathname.startsWith('/login')) {
    clearTokens();
    window.location.href = '/login?expired=1';
  }
}

async function request<T>(endpoint: string, options: RequestOptions = {}, retried = false): Promise<T> {
  const headers: Record<string, string> = { 'Content-Type': 'application/json' };
  const token = options.token || getAccessToken();
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

  if (res.status === 401 && !retried && !options.skipAuthRedirect) {
    const newToken = await refreshAccessToken();
    if (newToken) {
      return request<T>(endpoint, { ...options, token: newToken }, true);
    }
    redirectToLogin();
    throw new Error('Session expired. Please log in again.');
  }

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: 'Request failed' }));
    const detail = error.detail;
    const message = typeof detail === 'string'
      ? detail
      : Array.isArray(detail)
        ? detail[0]?.msg || 'Request failed'
        : `HTTP ${res.status}`;
    if (res.status === 401 && !options.skipAuthRedirect) {
      redirectToLogin();
    }
    throw new Error(message);
  }
  return res.json();
}

export const api = {
  auth: {
    register: (data: { email: string; password: string; first_name: string; last_name: string }) =>
      request('/auth/register', { method: 'POST', body: data, skipAuthRedirect: true }),
    login: (data: { email: string; password: string }) =>
      request('/auth/login', { method: 'POST', body: data, skipAuthRedirect: true }),
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
  voice: {
    analyze: (data: {
      transcript?: string;
      audio_base64?: string;
      audio_mime_type?: string;
      duration_seconds?: number;
      conversation_id?: string;
    }) => request('/voice/analyze', { method: 'POST', body: data }),
  },
  grammar: {
    grades: () => request('/grammar/grades'),
    lessons: (grade: number) => request(`/grammar/lessons?grade=${grade}`),
    intro: (grade: number, lessonId: string) =>
      request(`/grammar/intro?grade=${grade}&lesson_id=${lessonId}`),
    practice: (data: {
      grade: number;
      lesson_id: string;
      transcript?: string;
      audio_base64?: string;
      audio_mime_type?: string;
      duration_seconds?: number;
    }) => request('/grammar/practice', { method: 'POST', body: data }),
  },
};
