// src/services/tasks.ts
import api from "../lib/axios";

export type Task = {
  id: number;
  user_id: number;
  title: string;
  description?: string;
  status: "todo" | "in_progress" | "done";
  priority: "low" | "medium" | "high";
  due_at: string | null;
  completed_at: string | null;
  source: string;
  created_at: string;
  updated_at: string;
  outlook_event_id?: string | null; // <— NEW
};

export async function createTask(input: Partial<Task> & { title: string }) {
  const res = await api.post("/api/tasks", input);
  return res.data as Task;
}

export async function listTasks(params?: { status?: string; q?: string; due_before?: string; due_after?: string; page?: number; page_size?: number; }) {
  const res = await api.get("/api/tasks", { params });
  return res.data as { items: Task[]; page: number; page_size: number; total: number; pages: number };
}

export async function getTask(id: number) {
  const res = await api.get(`/api/tasks/${id}`);
  return res.data as Task;
}

export async function updateTask(id: number, patch: Partial<Task>) {
  const res = await api.patch(`/api/tasks/${id}`, patch);
  return res.data as Task;
}

export async function deleteTask(id: number) {
  const res = await api.delete(`/api/tasks/${id}`);
  return res.data as { msg: string };
}

export async function quickAddTask(text: string, description?: string) {
  const res = await api.post("/api/tasks/quickadd", { text, description });
  return res.data as Task;
}
