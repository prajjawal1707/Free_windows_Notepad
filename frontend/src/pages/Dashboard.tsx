import { useEffect, useState } from "react";
import { getDashboard } from "../services/user.service";
import type { DashboardStats } from "../types";

export default function Dashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    getDashboard().then(setStats).catch((e) => setError(String(e.message ?? e)));
  }, []);

  if (error) return <div className="error">{error}</div>;
  if (!stats) return <p className="muted">Loading…</p>;

  const tiles: [string, string | number][] = [
    ["My notes", stats.my_notes],
    ["Users", stats.total_users],
    ["Admins", stats.admins],
    ["Active sessions", stats.active_sessions],
    ["Backend version", stats.version],
  ];
  return (
    <>
      <h1>Dashboard</h1>
      <div className="tiles">
        {tiles.map(([label, value]) => (
          <div className="card tile" key={label}><span className="muted">{label}</span><strong>{value}</strong></div>
        ))}
      </div>
      <div className="card">
        <p className="muted">Local database</p>
        <code>{stats.database_path}</code>
        <p className="muted">Server time (UTC): {new Date(stats.server_time + "Z").toLocaleString()}</p>
      </div>
    </>
  );
}
