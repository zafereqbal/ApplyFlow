const API = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
export type Application = {
  id: number; company: string; role: string; status: string; location?: string | null;
  job_url?: string | null; notes?: string | null; created_at: string; updated_at: string;
};
export type Summary = { total: number; by_status: Record<string, number>; interview_rate_percent: number; offer_count: number };
export function getToken() { return localStorage.getItem("applyflow_token"); }
async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const token = getToken();
  const response = await fetch(`${API}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...(token ? { Authorization: `Bearer ${token}` } : {}), ...init.headers },
  });
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.detail || `Request failed (${response.status})`);
  }
  if (response.status === 204) return undefined as T;
  return response.json();
}
export async function login(email: string, password: string) {
  const form = new URLSearchParams({ username: email, password });
  return request<{ access_token: string }>("/api/auth/login", { method: "POST", headers: { "Content-Type": "application/x-www-form-urlencoded" }, body: form });
}
export async function register(email: string, password: string) {
  return request("/api/auth/register", { method: "POST", body: JSON.stringify({ email, password }) });
}
export const api = {
  list: (q = "") => request<{ items: Application[]; total: number; page: number; page_size: number }>(`/api/applications?page=1&page_size=100${q ? `&q=${encodeURIComponent(q)}` : ""}`),
  create: (payload: Partial<Application> & { company: string; role: string }) => request<Application>("/api/applications", { method: "POST", body: JSON.stringify(payload) }),
  update: (id: number, payload: Partial<Application>) => request<Application>(`/api/applications/${id}`, { method: "PATCH", body: JSON.stringify(payload) }),
  remove: (id: number) => request<void>(`/api/applications/${id}`, { method: "DELETE" }),
  summary: () => request<Summary>("/api/dashboard/summary"),
};
