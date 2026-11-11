import { useEffect, useState, type FormEvent } from "react";
import { changePassword } from "../services/auth.service";
import { getSettings, saveSettings } from "../services/user.service";

export function applyTheme(theme: string) {
  document.documentElement.dataset.theme = theme === "dark" ? "dark" : "light";
}
const errText = (e: unknown) => (e instanceof Error ? e.message : String(e));

export default function Settings() {
  const [theme, setTheme] = useState("light");
  const [orgName, setOrgName] = useState("");
  const [msg, setMsg] = useState("");
  const [cur, setCur] = useState("");
  const [next, setNext] = useState("");
  const [again, setAgain] = useState("");
  const [pwMsg, setPwMsg] = useState<{ ok: boolean; text: string } | null>(null);

  useEffect(() => {
    getSettings().then((s) => { setTheme(s.theme ?? "light"); setOrgName(s.org_name ?? ""); }).catch(() => {});
  }, []);

  async function save() {
    try {
      await saveSettings({ theme, org_name: orgName });
      applyTheme(theme);
      setMsg("Saved ✓");
    } catch (e) { setMsg(errText(e)); }
  }

  async function changePw(e: FormEvent) {
    e.preventDefault();
    if (next !== again) { setPwMsg({ ok: false, text: "New passwords do not match" }); return; }
    try {
      await changePassword(cur, next);
      setCur(""); setNext(""); setAgain("");
      setPwMsg({ ok: true, text: "Password changed ✓" });
    } catch (err) { setPwMsg({ ok: false, text: errText(err) }); }
  }

  return (
    <>
      <h1>Settings</h1>
      <div className="card form">
        <h3>Appearance</h3>
        <label>Theme
          <select value={theme} onChange={(e) => setTheme(e.target.value)}>
            <option value="light">Light</option><option value="dark">Dark</option>
          </select>
        </label>
        <label>Organization name<input value={orgName} onChange={(e) => setOrgName(e.target.value)} /></label>
        <button className="btn" onClick={save}>Save</button>
        {msg && <p className="muted">{msg}</p>}
      </div>

      <form className="card form" onSubmit={changePw}>
        <h3>Change my password</h3>
        <label>Current password<input type="password" value={cur} onChange={(e) => setCur(e.target.value)} required /></label>
        <label>New password<input type="password" value={next} onChange={(e) => setNext(e.target.value)} required minLength={6} /></label>
        <label>Repeat new password<input type="password" value={again} onChange={(e) => setAgain(e.target.value)} required minLength={6} /></label>
        <button className="btn">Change password</button>
        {pwMsg && <p className={pwMsg.ok ? "muted" : "error"}>{pwMsg.text}</p>}
      </form>
    </>
  );
}
