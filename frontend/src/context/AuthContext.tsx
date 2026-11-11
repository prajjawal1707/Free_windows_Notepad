import { createContext, useCallback, useContext, useEffect, useState, type ReactNode } from "react";
import { sessionToken, waitForBackend } from "../services/api";
import * as auth from "../services/auth.service";
import type { User } from "../types";

interface AuthState {
  user: User | null;
  hasUsers: boolean;
  booting: boolean;
  bootError: string | null;
  retry: () => void;
  login: (u: string, p: string) => Promise<void>;
  register: (u: string, p: string, name: string) => Promise<void>;
  logout: () => Promise<void>;
}

const Ctx = createContext<AuthState | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [hasUsers, setHasUsers] = useState(true);
  const [booting, setBooting] = useState(true);
  const [bootError, setBootError] = useState<string | null>(null);
  const [attempt, setAttempt] = useState(0);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      setBooting(true);
      setBootError(null);
      try {
        await waitForBackend();
        const status = await auth.authStatus();
        if (cancelled) return;
        setHasUsers(status.has_users);
        if (sessionToken.get()) {
          try { setUser(await auth.me()); } catch { sessionToken.clear(); }
        }
      } catch (e) {
        if (!cancelled) setBootError(e instanceof Error ? e.message : String(e));
      } finally {
        if (!cancelled) setBooting(false);
      }
    })();
    return () => { cancelled = true; };
  }, [attempt]);

  const login = useCallback(async (u: string, p: string) => setUser(await auth.login(u, p)), []);
  const register = useCallback(async (u: string, p: string, n: string) => {
    setUser(await auth.register(u, p, n));
    setHasUsers(true);
  }, []);
  const logout = useCallback(async () => { await auth.logout(); setUser(null); }, []);

  return (
    <Ctx.Provider value={{ user, hasUsers, booting, bootError, retry: () => setAttempt((a) => a + 1), login, register, logout }}>
      {children}
    </Ctx.Provider>
  );
}

export function useAuth(): AuthState {
  const v = useContext(Ctx);
  if (!v) throw new Error("useAuth must be used inside AuthProvider");
  return v;
}
