import { create } from 'zustand';
import api from '../lib/axios';

export type AuthState = {
  token: string | null;
  email: string | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string) => Promise<void>;
  logout: () => void;
};

function save(token: string | null, email: string | null) {
  if (token) localStorage.setItem('token', token); else localStorage.removeItem('token');
  if (email) localStorage.setItem('email', email); else localStorage.removeItem('email');
}

export const authStore = create<AuthState>((set) => ({
  token: localStorage.getItem('token'),
  email: localStorage.getItem('email'),
  loading: false,
  async login(email, password) {
    set({ loading: true });
    try {
      console.log('Attempting to login with:', { email, password: '***' });
      console.log('API base URL:', api.defaults.baseURL);
      const { data } = await api.post('/api/auth/login', { email, password });
      console.log('Login response:', data);
      const token = data?.access_token as string;
      save(token, email);
      set({ token, email, loading: false });
      window.location.assign('/dashboard');
    } catch (e: any) {
      console.error('Login error:', e);
      console.error('Error response:', e?.response?.data);
      console.error('Error status:', e?.response?.status);
      set({ loading: false });
      throw e;
    }
  },
  async register(email, password) {
    set({ loading: true });
    try {
      console.log('Attempting to register with:', { email, password: '***' });
      console.log('API base URL:', api.defaults.baseURL);
      const response = await api.post('/api/auth/register', { email, password });
      console.log('Register response:', response.data);
      set({ loading: false });
      window.location.assign('/login');
    } catch (e: any) {
      console.error('Register error:', e);
      console.error('Error response:', e?.response?.data);
      console.error('Error status:', e?.response?.status);
      set({ loading: false });
      throw e;
    }
  },
  logout() {
    save(null, null);
    set({ token: null, email: null });
  },
}));
