import { useEffect, useState } from "react";
import Layout from "./components/layout/Layout";
import { useAuth } from "./context/AuthContext";
import Dashboard from "./pages/Dashboard";
import Login from "./pages/Login";
import Notes from "./pages/Notes";
import Settings, { applyTheme } from "./pages/Settings";
import Users from "./pages/Users";
import { getSettings } from "./services/user.service";
import type { Page } from "./types";

export default function App() {
  const { user, booting, bootError, retry } = useAuth();
  const [page, setPage] = useState<Page>("notes");

  useEffect(() => {
    if (user) getSettings().then((s) => applyTheme(s.theme ?? "light")).catch(() => {});
  }, [user]);

  if (booting) return <div className="center"><div className="card auth"><div className="spinner" /><p className="muted">Starting backend…</p></div></div>;
  if (bootError) return (
    <div className="center"><div className="card auth">
      <h1>Backend unavailable</h1><div className="error">{bootError}</div>
      <button className="btn" onClick={retry}>Retry</button>
    </div></div>
  );
  if (!user) return <Login />;

  return (
    <Layout page={page} onNavigate={setPage}>
      {page === "notes" && <Notes />}
      {page === "dashboard" && <Dashboard />}
      {page === "users" && <Users />}
      {page === "settings" && <Settings />}
    </Layout>
  );
}
