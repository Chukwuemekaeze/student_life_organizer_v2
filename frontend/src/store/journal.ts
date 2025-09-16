import { create } from 'zustand';
import api from '../lib/axios';
import type { Journal } from '../types';

export type JournalState = {
  items: Journal[];
  loading: boolean;
  fetchList: (params?: { page?: number; limit?: number; q?: string }) => Promise<void>;
  fetchOne: (id: number) => Promise<Journal>;
  create: (content: string) => Promise<Journal>;
  update: (id: number, content: string) => Promise<Journal>;
  remove: (id: number) => Promise<void>;
};

function normalizeList(data: any): Journal[] {
  if (Array.isArray(data)) return data as Journal[];
  if (Array.isArray(data?.entries)) return data.entries as Journal[];
  if (Array.isArray(data?.items)) return data.items as Journal[];
  return [];
}

export const journalStore = create<JournalState>((set, get) => ({
  items: [],
  loading: false,

  async fetchList(params) {
    set({ loading: true });
    try {
      const { data } = await api.get('/api/journal', { params });
      const items = normalizeList(data).sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
      set({ items, loading: false });
    } catch (e) {
      set({ loading: false });
      throw e;
    }
  },

  async fetchOne(id) {
    const { data } = await api.get(`/api/journal/${id}`);
    return data as Journal;
  },

  async create(content) {
    const { data } = await api.post('/api/journal', { content });
    // optimistic prepend
    set({ items: [data as Journal, ...get().items] });
    return data as Journal;
  },

  async update(id, content) {
    const { data } = await api.put(`/api/journal/${id}`, { content });
    set({ items: get().items.map((it) => (it.id === id ? (data as Journal) : it)) });
    return data as Journal;
  },

  async remove(id) {
    await api.delete(`/api/journal/${id}`);
    set({ items: get().items.filter((it) => it.id !== id) });
  },
}));
