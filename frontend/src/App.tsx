import { FormEvent, useCallback, useEffect, useMemo, useState } from "react";
import { api, Application, getToken, login, register, Summary } from "./api";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

const statuses = ["saved", "applied", "screening", "interview", "offer", "rejected", "withdrawn"];
const emptySummary: Summary = { total: 0, by_status: {}, interview_rate_percent: 0, offer_count: 0 };

export default function App() {
  const [token, setToken] = useState(getToken());
  const [authMode, setAuthMode] = useState<"login" | "register">("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [applications, setApplications] = useState<Application[]>([]);
  const [summary, setSummary] = useState<Summary>(emptySummary);
  const [company, setCompany] = useState("");
  const [role, setRole] = useState("");
  const [status, setStatus] = useState("applied");
  const [search, setSearch] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const refresh = useCallback(async () => {
    const [page, stats] = await Promise.all([api.list(search), api.summary()]);
    setApplications(page.items);
    setSummary(stats);
  }, [search]);

  useEffect(() => {
    if (token) refresh().catch((e: Error) => setError(e.message));
  }, [token, refresh]);

  const chartData = useMemo(() => statuses.map((name) => ({ name, count: summary.by_status[name] || 0 })), [summary]);

  async function submitAuth(event: FormEvent) {
    event.preventDefault(); setError(""); setBusy(true);
    try {
      if (authMode === "register") await register(email, password);
      const result = await login(email, password);
      localStorage.setItem("applyflow_token", result.access_token);
      setToken(result.access_token);
    } catch (e) { setError((e as Error).message); }
    finally { setBusy(false); }
  }

  async function addApplication(event: FormEvent) {
    event.preventDefault(); setError("");
    try {
      await api.create({ company, role, status });
      setCompany(""); setRole("");
      await refresh();
    } catch (e) { setError((e as Error).message); }
  }

  async function updateStatus(item: Application, nextStatus: string) {
    try { await api.update(item.id, { status: nextStatus }); await refresh(); }
    catch (e) { setError((e as Error).message); }
  }

  async function remove(item: Application) {
    if (!window.confirm(`Delete ${item.role} at ${item.company}?`)) return;
    try { await api.remove(item.id); await refresh(); }
    catch (e) { setError((e as Error).message); }
  }

  function logout() { localStorage.removeItem("applyflow_token"); setToken(null); setApplications([]); setSummary(emptySummary); }

  if (!token) return <main className="auth-wrap"><section className="auth-card">
    <div className="brand-mark">A</div><p className="eyebrow">YOUR CAREER WORKSPACE</p><h1>{authMode === "login" ? "Welcome back" : "Create your account"}</h1>
    <p className="muted">Keep every application and interview in one place.</p>
    <form onSubmit={submitAuth} className="stack">
      <label>Email<input type="email" required value={email} onChange={e => setEmail(e.target.value)} placeholder="you@example.com" /></label>
      <label>Password<input type="password" required minLength={10} value={password} onChange={e => setPassword(e.target.value)} placeholder="At least 10 characters" /></label>
      {error && <p className="error">{error}</p>}
      <button disabled={busy}>{busy ? "Please wait…" : authMode === "login" ? "Sign in" : "Create account"}</button>
    </form>
    <p className="switch">{authMode === "login" ? "New to ApplyFlow?" : "Already have an account?"} <button className="link" onClick={() => setAuthMode(authMode === "login" ? "register" : "login")}>{authMode === "login" ? "Create an account" : "Sign in"}</button></p>
  </section></main>;

  return <div className="app-shell">
    <aside className="sidebar"><div className="brand"><span className="brand-mark small">A</span><span>ApplyFlow</span></div><p className="nav-label">WORKSPACE</p><div className="nav-item active">▦ <span>Overview</span></div><div className="nav-item">▤ <span>Applications</span></div><div className="nav-item">◷ <span>Interview timeline</span></div><div className="sidebar-bottom"><div className="avatar">{email.slice(0, 1).toUpperCase() || "U"}</div><div className="profile"><strong>{email || "Your account"}</strong><span>Personal workspace</span></div><button className="logout" onClick={logout} title="Sign out">↗</button></div></aside>
    <main className="main">
      <header className="topbar"><div><p className="eyebrow">MONDAY MOTIVATION, EVERY DAY</p><h1>Your job search, in focus.</h1><p className="muted">A clearer view of your progress and next opportunity.</p></div><button className="secondary" onClick={refresh}>↻ Refresh</button></header>
      {error && <div className="notice">{error}<button className="link" onClick={() => setError("")}>Dismiss</button></div>}
      <section className="stats-grid">
        <Stat label="Total applications" value={summary.total} detail="Across your job search" icon="▤" />
        <Stat label="Interview pipeline" value={(summary.by_status.screening || 0) + (summary.by_status.interview || 0)} detail={`${summary.interview_rate_percent}% reached screening or beyond`} icon="◷" />
        <Stat label="Offers received" value={summary.offer_count} detail="Keep going — every step counts" icon="✧" />
        <Stat label="Active applications" value={summary.total - (summary.by_status.rejected || 0) - (summary.by_status.withdrawn || 0)} detail="Not rejected or withdrawn" icon="↗" />
      </section>
      <section className="content-grid">
        <div className="panel chart-panel"><div className="panel-heading"><div><h2>Application pipeline</h2><p className="muted">Applications by current stage</p></div><span className="pill">All time</span></div><div className="chart"><ResponsiveContainer width="100%" height="100%"><BarChart data={chartData} margin={{ top: 10, right: 8, left: -22, bottom: 4 }}><CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e9edf3" /><XAxis dataKey="name" tick={{ fontSize: 11, fill: "#687386" }} axisLine={false} tickLine={false} /><YAxis allowDecimals={false} tick={{ fontSize: 11, fill: "#687386" }} axisLine={false} tickLine={false} /><Tooltip /><Bar dataKey="count" fill="#5865e8" radius={[5, 5, 0, 0]} /></BarChart></ResponsiveContainer></div></div>
        <div className="panel add-panel"><div className="panel-heading"><div><h2>Quick add</h2><p className="muted">Log a new opportunity</p></div><span className="add-icon">＋</span></div><form onSubmit={addApplication} className="stack"><label>Company<input required value={company} onChange={e => setCompany(e.target.value)} placeholder="e.g. Stripe" /></label><label>Job title<input required value={role} onChange={e => setRole(e.target.value)} placeholder="e.g. Backend Engineer" /></label><label>Current stage<select value={status} onChange={e => setStatus(e.target.value)}>{statuses.map(s => <option key={s} value={s}>{titleCase(s)}</option>)}</select></label><button>Add application <span>→</span></button></form></div>
      </section>
      <section className="panel table-panel"><div className="panel-heading table-head"><div><h2>Recent applications</h2><p className="muted">Keep your pipeline moving forward.</p></div><input className="search" value={search} onChange={e => setSearch(e.target.value)} placeholder="⌕ Search company or role" /></div>
        {applications.length === 0 ? <div className="empty"><div className="empty-icon">▤</div><strong>No applications yet</strong><p>Add your first opportunity above to start tracking your progress.</p></div> : <div className="table-scroll"><table><thead><tr><th>COMPANY / ROLE</th><th>STAGE</th><th>LAST UPDATED</th><th>ACTIONS</th></tr></thead><tbody>{applications.map(item => <tr key={item.id}><td><div className="company-cell"><span className="company-logo">{item.company.slice(0, 1).toUpperCase()}</span><div><strong>{item.company}</strong><span>{item.role}</span></div></div></td><td><select className={`status-select status-${item.status}`} value={item.status} onChange={e => updateStatus(item, e.target.value)}>{statuses.map(s => <option key={s} value={s}>{titleCase(s)}</option>)}</select></td><td className="date">{new Date(item.updated_at).toLocaleDateString()}</td><td><button className="delete" onClick={() => remove(item)} aria-label={`Delete ${item.company}`}>Delete</button></td></tr>)}</tbody></table></div>}
      </section>
      <footer>Built for clarity. Powered by consistency. <span>ApplyFlow v1.0</span></footer>
    </main>
  </div>;
}

function Stat({ label, value, detail, icon }: { label: string; value: number; detail: string; icon: string }) {
  return <div className="stat-card"><div className="stat-top"><span>{label}</span><span className="stat-icon">{icon}</span></div><strong className="stat-value">{value}</strong><span className="stat-detail">{detail}</span></div>;
}
function titleCase(value: string) { return value.charAt(0).toUpperCase() + value.slice(1); }
