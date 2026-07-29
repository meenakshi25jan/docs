import * as SecureStore from 'expo-secure-store';
import { API_URL } from '@/constants';

const ACCESS_KEY = 'access_token';
const REFRESH_KEY = 'refresh_token';

export async function saveTokens(accessToken: string, refreshToken?: string) {
  await SecureStore.setItemAsync(ACCESS_KEY, accessToken);
  if (refreshToken) await SecureStore.setItemAsync(REFRESH_KEY, refreshToken);
}

export async function clearTokens() {
  await SecureStore.deleteItemAsync(ACCESS_KEY);
  await SecureStore.deleteItemAsync(REFRESH_KEY);
}

export async function getAccessToken(): Promise<string | null> {
  return SecureStore.getItemAsync(ACCESS_KEY);
}

async function getRefreshToken(): Promise<string | null> {
  return SecureStore.getItemAsync(REFRESH_KEY);
}

async function refreshAccessToken(): Promise<string | null> {
  const refreshToken = await getRefreshToken();
  if (!refreshToken) return null;
  try {
    const res = await fetch(`${API_URL}/auth/refresh`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: refreshToken }),
    });
    if (!res.ok) return null;
    const data = (await res.json()) as { access_token: string; refresh_token: string };
    await saveTokens(data.access_token, data.refresh_token);
    return data.access_token;
  } catch {
    return null;
  }
}

interface RequestOptions {
  method?: string;
  body?: unknown;
  token?: string;
  skipAuth?: boolean;
}

export type AuthHandler = () => void;
let onUnauthorized: AuthHandler | null = null;

export function setUnauthorizedHandler(handler: AuthHandler) {
  onUnauthorized = handler;
}

async function request<T>(endpoint: string, options: RequestOptions = {}, retried = false): Promise<T> {
  const headers: Record<string, string> = { 'Content-Type': 'application/json' };
  const token = options.token || (options.skipAuth ? null : await getAccessToken());
  if (token) headers.Authorization = `Bearer ${token}`;

  let res: Response;
  try {
    res = await fetch(`${API_URL}${endpoint}`, {
      method: options.method || 'GET',
      headers,
      body: options.body ? JSON.stringify(options.body) : undefined,
    });
  } catch {
    throw new Error('Cannot reach the server. Check your internet connection and API URL.');
  }

  if (res.status === 401 && !retried && !options.skipAuth) {
    const newToken = await refreshAccessToken();
    if (newToken) return request<T>(endpoint, { ...options, token: newToken }, true);
    await clearTokens();
    onUnauthorized?.();
    throw new Error('Session expired. Please log in again.');
  }

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: 'Request failed' }));
    const detail = error.detail;
    const message =
      typeof detail === 'string'
        ? detail
        : Array.isArray(detail)
          ? detail[0]?.msg || 'Request failed'
          : `HTTP ${res.status}`;
    throw new Error(message);
  }
  return res.json();
}

export const api = {
  auth: {
    register: (data: { email: string; password: string; first_name: string; last_name: string }) =>
      request('/auth/register', { method: 'POST', body: data, skipAuth: true }),
    login: (data: { email: string; password: string }) =>
      request('/auth/login', { method: 'POST', body: data, skipAuth: true }),
    me: () => request('/auth/me'),
  },
  assessments: {
    create: (data: { assessment_type: string }) =>
      request('/assessments', { method: 'POST', body: data }),
    submit: (id: string, answers: unknown[]) =>
      request(`/assessments/${id}/submit`, { method: 'POST', body: { answers } }),
  },
  conversations: {
    start: (data: { scenario: string }) =>
      request('/conversations', { method: 'POST', body: data }),
    sendMessage: (id: string, content: string) =>
      request(`/conversations/${id}/messages`, { method: 'POST', body: { content } }),
  },
  dashboard: {
    student: () => request('/dashboard/student'),
  },
};
