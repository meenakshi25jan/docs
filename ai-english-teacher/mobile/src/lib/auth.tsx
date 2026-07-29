import React, { createContext, useCallback, useContext, useEffect, useState } from 'react';
import { api, clearTokens, getAccessToken, saveTokens, setUnauthorizedHandler } from '@/lib/api';

interface User {
  id: string;
  email: string;
  first_name?: string;
  last_name?: string;
  role?: string;
}

interface AuthContextValue {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (data: { email: string; password: string; first_name: string; last_name: string }) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  const logout = useCallback(async () => {
    await clearTokens();
    setUser(null);
  }, []);

  useEffect(() => {
    setUnauthorizedHandler(() => {
      setUser(null);
    });
    (async () => {
      try {
        const token = await getAccessToken();
        if (token) {
          const me = (await api.auth.me()) as User;
          setUser(me);
        }
      } catch {
        await clearTokens();
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  const login = async (email: string, password: string) => {
    const res = (await api.auth.login({ email, password })) as {
      tokens: { access_token: string; refresh_token: string };
      user?: User;
    };
    await saveTokens(res.tokens.access_token, res.tokens.refresh_token);
    const me = res.user || ((await api.auth.me()) as User);
    setUser(me);
  };

  const register = async (data: { email: string; password: string; first_name: string; last_name: string }) => {
    const res = (await api.auth.register(data)) as {
      tokens: { access_token: string; refresh_token: string };
      user?: User;
    };
    await saveTokens(res.tokens.access_token, res.tokens.refresh_token);
    const me = res.user || ((await api.auth.me()) as User);
    setUser(me);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
