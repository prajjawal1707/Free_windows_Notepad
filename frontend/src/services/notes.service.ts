import { apiDelete, apiGet, apiPost, apiPut } from "./api";
import type { Note, NoteInput } from "../types";

export const listNotes = (q = "") => apiGet<Note[]>(`/api/v1/notes/?q=${encodeURIComponent(q)}`);
export const createNote = (n: NoteInput) => apiPost<Note>("/api/v1/notes/", n);
export const updateNote = (id: number, n: NoteInput) => apiPut<Note>(`/api/v1/notes/${id}`, n);
export const deleteNote = (id: number) => apiDelete<{ ok: boolean }>(`/api/v1/notes/${id}`);
export const exportNotes = () => apiGet<{ path: string; count: number }>("/api/v1/notes/export");
export const importNotes = (csv: string) => apiPost<{ imported: number }>("/api/v1/notes/import", { csv });
