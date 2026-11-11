import { apiGet, apiPost, sessionToken } from "./api";
import type { LoginResponse, User } from "../types";

export const authStatus = () => apiGet<{ has_users: boolean }>("/api/v1/auth/status");
export const me = () => apiGet<User>("/api/v1/auth/me");

export async function login(username: string, password: string): Promise<User> {
  const r = await apiPost<LoginResponse>("/api/v1/auth/login", { username, password });
  sessionToken.set(r.token);
  return r.user;
}

export async function register(username: string, password: string, full_name: string): Promise<User> {
  const r = await apiPost<LoginResponse>("/api/v1/auth/register", { username, password, full_name });
  sessionToken.set(r.token);
  return r.user;
}

export async function logout(): Promise<void> {
  try { await apiPost("/api/v1/auth/logout"); } catch { /* already invalid */ }
  sessionToken.clear();
}

export const changePassword = (current_password: string, new_password: string) =>
  apiPost<{ ok: boolean }>("/api/v1/auth/change-password", { current_password, new_password });
