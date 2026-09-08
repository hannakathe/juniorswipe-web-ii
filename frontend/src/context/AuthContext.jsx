import { createContext, useCallback, useContext, useEffect, useState } from 'react';
import { auth as authApi, tokenStore } from '../api/client';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => tokenStore.getUser());
  const [loading, setLoading] = useState(true);

  // Accept a token handed off from the static landing site via URL fragment (#token=).
  useEffect(() => {
    const hash = window.location.hash;
    if (hash.startsWith('#token=')) {
      const t = decodeURIComponent(hash.slice('#token='.length));
      if (t) tokenStore.set(t);
      window.history.replaceState(null, '', window.location.pathname + window.location.search);
    }
  }, []);

  const refresh = useCallback(async () => {
    if (!tokenStore.get()) {
      setUser(null);
      setLoading(false);
      return;
    }
    try {
      const me = await authApi.me();
      setUser(me);
      tokenStore.setUser(me);
    } catch {
      tokenStore.clear();
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
    const onUnauthorized = () => {
      setUser(null);
    };
    window.addEventListener('juniorswipe:unauthorized', onUnauthorized);
    return () => window.removeEventListener('juniorswipe:unauthorized', onUnauthorized);
  }, [refresh]);

  const login = async (email, password) => {
    const { token, user: u } = await authApi.login({ email, password });
    tokenStore.set(token);
    tokenStore.setUser(u);
    setUser(u);
    await refresh();
  };

  const register = async (payload) => {
    const { token, user: u } = await authApi.register(payload);
    tokenStore.set(token);
    tokenStore.setUser(u);
    setUser(u);
    await refresh();
  };

  const logout = () => {
    tokenStore.clear();
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout, refresh }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
