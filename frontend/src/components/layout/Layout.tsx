import type { ReactNode } from "react";
import { useAuth } from "../../context/AuthContext";
import type { Page } from "../../types";

const NAV: { id: Page; label: string }[] = [
  { id: "notes", label: "Notes" },
  { id: "dashboard", label: "Dashboard" },
  { id: "users", label: "Users" },
  { id: "settings", label: "Settings" },
];

export default function Layout({ page, onNavigate, children }: { page: Page; onNavigate: (p: Page) => void; children: ReactNode }) {
  const { user, logout } = useAuth();
  return (
    <div className="shell">
      <aside className="sidebar">
        <div className="brand"><img src="/logo.png" alt="" width={28} height={28} /> My Desktop App</div>
        <nav>
          {NAV.map((n) => (
            <button key={n.id} className={page === n.id ? "nav active" : "nav"} onClick={() => onNavigate(n.id)}>
              {n.label}
            </button>
          ))}
        </nav>
        <div className="sidebar-foot">
          <div className="who"><strong>{user?.full_name || user?.username}</strong><span>{user?.role}</span></div>
          <button className="btn ghost" onClick={logout}>Sign out</button>
        </div>
      </aside>
      <main className="content">{children}</main>
    </div>
  );
}
