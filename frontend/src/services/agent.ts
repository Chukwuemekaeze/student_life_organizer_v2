// src/services/agent.ts
import { API_BASE } from "./http";

const authHeader = () => {
  const token = localStorage.getItem("token");
  return token ? { Authorization: `Bearer ${token}` } : {};
};

export type AgentToolCall = {
  name: string;
  input: Record<string, any>;
  result?: Record<string, any>;
};

export type AgentResponse = {
  text: string;
  tool_calls?: AgentToolCall[];
  error?: string;
};

export async function agentChat(message: string, confirmWrites: boolean = true): Promise<AgentResponse> {
  const res = await fetch(`${API_BASE}/api/agent/chat`, {
    method: "POST",
    headers: {
      ...authHeader(),
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ message, confirm_writes: confirmWrites }),
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

  return (await res.json()) as AgentResponse;
}
