// Small fetch helper that reads JWT from localStorage.
export const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:5000";

function authHeaders(): Record<string, string> {
  const token = localStorage.getItem("token");
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export async function http<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...authHeaders(),
  };
  
  // Add any additional headers from options
  if (options.headers) {
    Object.assign(headers, options.headers);
  }

  console.log(`Making ${options.method || 'GET'} request to:`, `${API_BASE}${path}`);
  console.log("Headers:", headers);

  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
    credentials: "include",
  });

  if (!res.ok) {
    let msg = res.statusText || `HTTP ${res.status}`;
    try {
      const data = await res.json();
      if ((data as any)?.msg) msg = (data as any).msg;
      if ((data as any)?.error) msg = (data as any).error;
    } catch (_) {}
    throw new Error(msg);
  }
  return (await res.json()) as T;
}
