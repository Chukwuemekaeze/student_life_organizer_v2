// src/services/notifications.ts
import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:5000";
const authHeader = () => {
  const token = localStorage.getItem("access_token");
  return token ? { Authorization: `Bearer ${token}` } : {};
};

export type Notification = {
  id: number;
  user_id: number;
  kind: string;
  title: string;
  body: string;
  ref_type?: string | null;
  ref_id?: number | null;
  scheduled_for?: string | null;
  delivered_at?: string | null;
  read_at?: string | null;
  created_at: string;
  updated_at: string;
};

export async function scanDue(opts?: { soon_hours?: number; overdue_days?: number }) {
  const params: any = {};
  if (opts?.soon_hours) params.soon_hours = opts.soon_hours;
  if (opts?.overdue_days) params.overdue_days = opts.overdue_days;
  const res = await axios.get(`${API_URL}/api/notifications/scan-due`, { headers: authHeader(), params });
  return res.data as { created: number };
}

export async function fetchUnread() {
  const res = await axios.get(`${API_URL}/api/notifications/unread`, { headers: authHeader() });
  return res.data as { items: Notification[]; count: number };
}

export async function markRead(ids: number[]) {
  const res = await axios.post(
    `${API_URL}/api/notifications/mark-read`,
    { ids },
    { headers: { ...authHeader(), "Content-Type": "application/json" } }
  );
  return res.data as { updated: number };
}
