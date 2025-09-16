// src/services/notes.ts
import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:5000";

function authHeader() {
  const token = localStorage.getItem("token"); // matches the auth store token key
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export type NoteItem = {
  page_id: string;
  title: string;
  last_edited_time?: string;
  url?: string;
};

export async function getNotesStatus() {
  const res = await axios.get(`${API_URL}/api/notes/status`, { headers: authHeader() });
  return res.data as { connected: boolean; workspace_name?: string };
}

export async function connectNotes(token: string) {
  const res = await axios.post(`${API_URL}/api/notes/connect`, { token }, { headers: authHeader() });
  return res.data as { connected: boolean; workspace_name?: string };
}

export async function disconnectNotes() {
  const res = await axios.delete(`${API_URL}/api/notes/disconnect`, { headers: authHeader() });
  return res.data;
}

export async function syncNotes() {
  const res = await axios.post(`${API_URL}/api/notes/sync`, {}, { headers: authHeader() });
  return res.data;
}

export async function listNotes({ limit = 10 }: { limit?: number } = {}) {
  const res = await axios.get(`${API_URL}/api/notes/list`, {
    headers: authHeader(),
    params: { limit },
  });
  return res.data as { items: NoteItem[] };
}


