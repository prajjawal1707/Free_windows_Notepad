export interface User {
  id: number;
  username: string;
  full_name: string;
  role: "admin" | "user";
  created_at: string;
}
export interface LoginResponse { token: string; user: User }
export interface DashboardStats {
  total_users: number;
  admins: number;
  active_sessions: number;
  my_notes: number;
  server_time: string;
  version: string;
  database_path: string;
}
export interface Note {
  id: number;
  title: string;
  content: string;
  tags: string;
  pinned: boolean;
  created_at: string;
  updated_at: string;
}
export type NoteInput = Pick<Note, "title" | "content" | "tags" | "pinned">;
export type Page = "notes" | "dashboard" | "users" | "settings";
