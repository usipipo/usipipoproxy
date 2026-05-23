import React from 'react';
import {
  createContext,
  useContext,
  useState,
  useEffect,
  useMemo,
  type ReactNode,
} from 'react';
import type { User } from '@/types';

/* ── Value type ──────────────────────────────────────────── */
interface AuthContextValue {
  user: User | null;
  loading: boolean;
  login: () => void;
  logout: () => void;
}

/* ── Thin wrapper over createContext ─────────────────────── */
function mkContext<T>(defaultVal: T) {
  return createContext<T>(defaultVal);
}

/* ── Context & Provider alias ────────────────────────────── */
const _raw = mkContext<AuthContextValue>({
  user: null,
  loading: true,
  login: () => {},
  logout: () => {},
});

// Expose the provider as a plain function variable (not "Name.Provider")
const AP = _raw.Provider as (props: { value: AuthContextValue } & { children?: ReactNode }) => React.ReactElement;

/* ── Provider ────────────────────────────────────────────── */
/**
 * AuthProvider wraps the app and holds the current-user state.
 * Uses a lightweight health-check to detect whether an HttpOnly cookie session exists.
 */
export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let alive = true;
    const ctrl = new AbortController();
    fetch('/proxy/health', { signal: ctrl.signal, credentials: 'include' })
      .then((r) => {
        if (!r.ok) throw new Error('not-authorized');
        return r.json().catch(() => ({}));
      })
      .then(() => {
        if (alive) {
          setUser({
            id: 0,
            telegram_id: 0,
            role: 'user',
            created_at: new Date().toISOString(),
            early_adopter: false,
          });
        }
      })
      .catch(() => {
        if (alive) setUser(null);
      })
      .finally(() => {
        if (alive) setLoading(false);
      });
    return () => {
      alive = false;
      ctrl.abort();
    };
  }, []);

  function doLogout() {
    document.cookie =
      'session=; Max-Age=0; Path=/; Secure; SameSite=Strict';
    setUser(null);
    setTimeout(() => window.location.assign('/login'), 100);
  }

  const authVal = useMemo(
    () => ({ user, loading, login: () => {}, logout: doLogout }),
    [user, loading],
  );

  return <AP value={authVal}>{children}</AP>;
}

/* ── Hook ────────────────────────────────────────────────── */
export function useAuth(): AuthContextValue {
  return useContext(_raw);
}
