import Constants from 'expo-constants';

export const API_URL =
  process.env.EXPO_PUBLIC_API_URL ||
  (Constants.expoConfig?.extra?.apiUrl as string) ||
  'https://ai-english-teacher-api.onrender.com/api/v1';

export const SCENARIOS = [
  { id: 'job_interview', label: 'Job Interview' },
  { id: 'restaurant', label: 'Restaurant Order' },
  { id: 'travel', label: 'Travel & Tourism' },
  { id: 'business_meeting', label: 'Business Meeting' },
] as const;

export const COLORS = {
  primary: '#2563eb',
  primaryDark: '#1d4ed8',
  background: '#f9fafb',
  card: '#ffffff',
  text: '#111827',
  textMuted: '#6b7280',
  border: '#e5e7eb',
  error: '#ef4444',
  success: '#22c55e',
};
