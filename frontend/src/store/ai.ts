import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { nanoid } from 'nanoid';
import { ChatMessage, ToolTrace } from '../types/ai';
import api from '../lib/axios';

interface AIState {
  messages: ChatMessage[];
  sending: boolean;
  error: string | null;
  send: (text: string) => Promise<void>;
  reset: () => void;
}

export const aiStore = create<AIState>()(persist((set, get) => ({
  messages: [],
  sending: false,
  error: null,
  async send(text: string) {
    if (!text.trim() || get().sending) return;
    const now = Date.now();
    const userMsg: ChatMessage = { id: nanoid(), role: 'user', content: text.trim(), createdAt: now };
    set({ messages: [...get().messages, userMsg], sending: true, error: null });

    try {
      // Backend expects: { message }
      const res = await api.post('/api/ai/chat', { message: userMsg.content });
      const reply: string = res.data?.reply ?? '';
      const tools: ToolTrace[] | undefined = res.data?.tools;
      const botMsg: ChatMessage = { id: nanoid(), role: 'assistant', content: reply, createdAt: Date.now(), tools };
      set({ messages: [...get().messages, botMsg], sending: false });
    } catch (e: any) {
      const msg = e?.response?.data?.msg || e?.message || 'Request failed';
      set({ sending: false, error: msg });
      // Auto-logout on 401 via axios interceptor; just surface toast here
      console.error('AI send error:', e);
    }
  },
  reset() { set({ messages: [], error: null, sending: false }); },
}), { name: 'slo-ai' }));

