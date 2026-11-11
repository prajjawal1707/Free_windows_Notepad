import { invoke } from "@tauri-apps/api/core";

interface BackendConfig { port: number; token: string }

const isTauri = typeof window !== "undefined" && "__TAURI_INTERNALS__" in window;
const SESSION_KEY = "session-token";

let configPromise: Promise<BackendConfig> | null = null;

/** In the desktop app the port + secret come from Rust. In a plain browser (dev) use defaults. */
export function getConfig(): Promise<BackendConfig> {
  if (!configPromise) {
    configPromise = isTauri
      ? invoke<BackendConfig>("get_backend_config")
      : Promise.resolve({
          port: Number(import.meta.env.VITE_BACKEND_PORT ?? 8765),
          token: String(import.meta.env.VITE_API_TOKEN ?? "dev-token"),
        });
  }
  return configPromise;
}

export const sessionToken = {
  get: () => localStorage.getItem(SESSION_KEY),
  set: (t: string) => localStorage.setItem(SESSION_KEY, t),
  clear: () => localStorage.removeItem(SESSION_KEY),
};

export class ApiError extends Error {
  constructor(public status: number, message: string) { super(message); }
}

async function request<T>(method: string, path: string, body?: unknown): Promise<T> {
  const { port, token } = await getConfig();
  const headers: Record<string, string> = { "X-API-Token": token };
  const session = sessionToken.get();
  if (session) headers["Authorization"] = `Bearer ${session}`;
  if (body !== undefined) headers["Content-Type"] = "application/json";

  const res = await fetch(`http://127.0.0.1:${port}${path}`, {
    method, headers, body: body !== undefined ? JSON.stringify(body) : undefined,
  });
  if (!res.ok) {
    let msg = `Request failed (${res.status})`;
    try {
      const data = await res.json();
      if (typeof data.detail === "string") msg = data.detail;
      else if (Array.isArray(data.detail)) msg = data.detail.map((d: { msg: string }) => d.msg).join(", ");
    } catch { /* ignore */ }
    throw new ApiError(res.status, msg);
  }
  return res.json() as Promise<T>;
}

export const apiGet = <T>(path: string) => request<T>("GET", path);
export const apiPost = <T>(path: string, body?: unknown) => request<T>("POST", path, body ?? {});
export const apiPut = <T>(path: string, body: unknown) => request<T>("PUT", path, body);
export const apiDelete = <T>(path: string) => request<T>("DELETE", path);

/** Poll /health until the Python backend is accepting requests. */
export async function waitForBackend(timeoutMs = 30000): Promise<void> {
  const { port } = await getConfig();
  const start = Date.now();
  let lastErr: unknown;
  while (Date.now() - start < timeoutMs) {
    try {
      const res = await fetch(`http://127.0.0.1:${port}/health`);
      if (res.ok) return;
    } catch (e) { lastErr = e; }
    await new Promise((r) => setTimeout(r, 400));
  }
  throw new Error(`Backend did not start within ${timeoutMs / 1000}s${lastErr ? ` (${String(lastErr)})` : ""}`);
}
