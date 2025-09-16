import { create } from 'zustand';
import api from '../lib/axios';
import type { CalendarEvent } from '../types';

export type CalendarState = {
  events: CalendarEvent[];
  lastSync: string | null;
  connected: boolean | null; // null = unknown, true/false known
  loading: boolean;
  checkConnected: () => Promise<void>;
  getAuthUrl: () => Promise<string>;
  sync: () => Promise<void>;
  createEvent: (event: Partial<CalendarEvent>) => Promise<CalendarEvent>;
  updateEvent: (id: string, updates: Partial<CalendarEvent>) => Promise<CalendarEvent>;
  deleteEvent: (id: string) => Promise<void>;
};

export const calendarStore = create<CalendarState>((set, get) => ({
  events: [],
  lastSync: null,
  connected: null, // null = unknown, true/false known
  loading: false,

  async checkConnected() {
    set({ loading: true });
    try {
      const { data } = await api.get('/api/calendar/sync');
      const events = (data?.events as CalendarEvent[]) || [];
      set({ events, connected: true, loading: false, lastSync: new Date().toISOString() });
    } catch (e: any) {
      const msg = e?.response?.data?.msg || '';
      if (e?.response?.status === 400 && msg.toLowerCase().includes('not connected')) {
        set({ connected: false, loading: false });
      } else {
        set({ loading: false });
        throw e;
    }
    }
  },

  async getAuthUrl() {
    const { data } = await api.get('/api/calendar/outlook/start');
    return data?.auth_url as string;
  },

  async sync() {
    set({ loading: true });
    try {
      const { data } = await api.get('/api/calendar/sync');
      const events = (data?.events as CalendarEvent[]) || [];
      set({ events, connected: true, loading: false, lastSync: new Date().toISOString() });
    } catch (e) {
      set({ loading: false });
      throw e;
    }
  },

  async createEvent(event: Partial<CalendarEvent>) {
    set({ loading: true });
    try {
      const { data } = await api.post('/api/calendar/events', event);
      const newEvent = data as CalendarEvent;
      set({ 
        events: [newEvent, ...get().events], 
        loading: false, 
        lastSync: new Date().toISOString() 
      });
      return newEvent;
    } catch (e) {
      set({ loading: false });
      throw e;
    }
  },

  async updateEvent(id: string, updates: Partial<CalendarEvent>) {
    set({ loading: true });
    try {
      const { data } = await api.put(`/api/calendar/events/${id}`, updates);
      const updatedEvent = data as CalendarEvent;
      set({ 
        events: get().events.map(e => e.id === id ? updatedEvent : e),
        loading: false,
        lastSync: new Date().toISOString()
      });
      return updatedEvent;
    } catch (e) {
      set({ loading: false });
      throw e;
    }
  },

  async deleteEvent(id: string) {
    set({ loading: true });
    try {
      await api.delete(`/api/calendar/events/${id}`);
      set({ 
        events: get().events.filter(e => e.id !== id),
        loading: false,
        lastSync: new Date().toISOString()
      });
    } catch (e) {
      set({ loading: false });
      throw e;
    }
  },
}));

