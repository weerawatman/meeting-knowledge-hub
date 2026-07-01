import { useState, useCallback } from "react";
import axios from "axios";

interface AuthState {
  token: string | null;
  role: string | null;
  email: string | null;
}

const STORAGE_KEY = "mhub_auth";

function loadAuth(): AuthState {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : { token: null, role: null, email: null };
  } catch {
    return { token: null, role: null, email: null };
  }
}

export function useAuth() {
  const [auth, setAuth] = useState<AuthState>(loadAuth);

  const login = useCallback(async (email: string, password: string) => {
    const { data } = await axios.post("/api/auth/login", { email, password });
    const state: AuthState = { token: data.token, role: data.role, email: data.email };
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
    setAuth(state);
    return data;
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem(STORAGE_KEY);
    setAuth({ token: null, role: null, email: null });
  }, []);

  return {
    isAuthenticated: !!auth.token,
    token: auth.token,
    role: auth.role,
    email: auth.email,
    login,
    logout,
  };
}
