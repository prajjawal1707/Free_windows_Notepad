import { useCallback, useEffect, useState, type FormEvent } from "react";
import { useAuth } from "../context/AuthContext";
import { createUser, deleteUser, getUsers, resetPassword, updateUser } from "../services/user.service";
import type { User } from "../types";

const errText = (e: unknown) => (e instanceof Error ? e.message : String(e));

export default function Users() {
  const { user: me } = useAuth();
  const isAdmin = me?.role === "admin";
  const [users, setUsers] = useState<User[]>([]);
  const [error, setError] = useState("");
  const [info, setInfo] = useState("");
  const [form, setForm] = useState({ username: "", password: "", full_name: "", role: "user" });
  const [editing, setEditing] = useState<{ id: number; username: string; full_name: string; role: string } | null>(null);
  const [pwFor, setPwFor] = useState<User | null>(null);
  const [newPw, setNewPw] = useState("");
  const [confirmId, setConfirmId] = useState<number | null>(null);

  const load = useCallback(() => { getUsers().then(setUsers).catch((e) => setError(errText(e))); }, []);
  useEffect(load, [load]);

  const run = async (fn: () => Promise<unknown>, ok: string) => {
    setError(""); setInfo("");
    try { await fn(); setInfo(ok); load(); } catch (e) { setError(errText(e)); }
  };

  const add = (e: FormEvent) => {
    e.preventDefault();
    run(async () => { await createUser(form); setForm({ username: "", password: "", full_name: "", role: "user" }); }, "User added");
  };
  const saveEdit = (e: FormEvent) => {
    e.preventDefault();
    if (!editing) return;
    run(async () => { await updateUser(editing.id, { full_name: editing.full_name, role: editing.role }); setEditing(null); }, "User updated");
  };
  const savePw = (e: FormEvent) => {
    e.preventDefault();
    if (!pwFor) return;
    run(async () => { await resetPassword(pwFor.id, newPw); setPwFor(null); setNewPw(""); }, "Password reset. That user must sign in again.");
  };
  const remove = (id: number) => {
    if (confirmId !== id) { setConfirmId(id); return; }
    setConfirmId(null);
    run(() => deleteUser(id), "User deleted");
  };

  return (
    <>
      <h1>Users</h1>
      {error && <div className="error">{error}</div>}
      {info && <div className="info">{info}</div>}
      <div className="card">
        <table>
          <thead><tr><th>ID</th><th>Username</th><th>Name</th><th>Role</th><th /></tr></thead>
          <tbody>
            {users.map((u) => (
              <tr key={u.id}>
                <td>{u.id}</td><td>{u.username}</td><td>{u.full_name}</td><td><span className="pill">{u.role}</span></td>
                <td className="actions">
                  {isAdmin && <>
                    <button className="btn ghost" onClick={() => setEditing({ id: u.id, username: u.username, full_name: u.full_name, role: u.role })}>Edit</button>
                    <button className="btn ghost" onClick={() => { setPwFor(u); setNewPw(""); }}>Password</button>
                    {u.id !== me?.id && (
                      <button className="btn ghost danger" onClick={() => remove(u.id)}>{confirmId === u.id ? "Confirm?" : "Delete"}</button>
                    )}
                  </>}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {isAdmin && editing && (
        <form className="card row" onSubmit={saveEdit}>
          <strong>Edit {editing.username}</strong>
          <input placeholder="Full name" value={editing.full_name} onChange={(e) => setEditing({ ...editing, full_name: e.target.value })} />
          <select value={editing.role} onChange={(e) => setEditing({ ...editing, role: e.target.value })}>
            <option value="user">User</option><option value="admin">Admin</option>
          </select>
          <button className="btn">Save</button>
          <button type="button" className="btn ghost" onClick={() => setEditing(null)}>Cancel</button>
        </form>
      )}
      {isAdmin && pwFor && (
        <form className="card row" onSubmit={savePw}>
          <strong>New password for {pwFor.username}</strong>
          <input type="password" placeholder="New password (6+ chars)" value={newPw} onChange={(e) => setNewPw(e.target.value)} required minLength={6} />
          <button className="btn">Reset password</button>
          <button type="button" className="btn ghost" onClick={() => setPwFor(null)}>Cancel</button>
        </form>
      )}
      {isAdmin && (
        <form className="card row" onSubmit={add}>
          <input placeholder="Username" value={form.username} onChange={(e) => setForm({ ...form, username: e.target.value })} required minLength={3} />
          <input placeholder="Full name" value={form.full_name} onChange={(e) => setForm({ ...form, full_name: e.target.value })} />
          <input placeholder="Password" type="password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} required minLength={6} />
          <select value={form.role} onChange={(e) => setForm({ ...form, role: e.target.value })}>
            <option value="user">User</option><option value="admin">Admin</option>
          </select>
          <button className="btn">Add user</button>
        </form>
      )}
    </>
  );
}
