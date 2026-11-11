import { useState, type FormEvent } from "react";
import { useAuth } from "../context/AuthContext";

export default function Login() {
  const { hasUsers, login, register } = useAuth();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit(e: FormEvent) {
    e.preventDefault();
    setBusy(true); setError("");
    try {
      if (hasUsers) await login(username, password);
      else await register(username, password, fullName);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally { setBusy(false); }
  }

  return (
    <div className="center">
      <form className="card auth" onSubmit={submit}>
        <img src="/logo.png" alt="" width={56} height={56} />
        <h1>{hasUsers ? "Welcome back" : "Create your admin account"}</h1>
        <p className="muted">{hasUsers ? "Sign in to continue." : "First launch: set up the administrator account."}</p>
        {!hasUsers && (
          <label>Full name<input value={fullName} onChange={(e) => setFullName(e.target.value)} /></label>
        )}
        <label>Username<input value={username} onChange={(e) => setUsername(e.target.value)} autoFocus required minLength={3} /></label>
        <label>Password<input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required minLength={6} /></label>
        {error && <div className="error">{error}</div>}
        <button className="btn" disabled={busy}>{busy ? "Please wait…" : hasUsers ? "Sign in" : "Create account"}</button>
      </form>
    </div>
  );
}
