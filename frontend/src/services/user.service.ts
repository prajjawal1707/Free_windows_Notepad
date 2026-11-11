import { apiDelete, apiGet, apiPost, apiPut } from "./api";
import type { DashboardStats, User } from "../types";

export const getUsers = () => apiGet<User[]>("/api/v1/users/");
export const createUser = (u: { username: string; password: string; full_name: string; role: string }) =>
  apiPost<User>("/api/v1/users/", u);
export const deleteUser = (id: number) => apiDelete<{ ok: boolean }>(`/api/v1/users/${id}`);
export const getDashboard = () => apiGet<DashboardStats>("/api/v1/dashboard/");
export const getSettings = () => apiGet<Record<string, string>>("/api/v1/settings/");
export const saveSettings = (values: Record<string, string>) =>
  apiPut<Record<string, string>>("/api/v1/settings/", { values });
export const updateUser = (id: number, data: { full_name?: string; role?: string }) =>
  apiPut<User>(`/api/v1/users/${id}`, data);
export const resetPassword = (id: number, new_password: string) =>
  apiPut<{ ok: boolean }>(`/api/v1/users/${id}/password`, { new_password });
