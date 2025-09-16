import axios from 'axios';
import { authStore } from '../store/auth';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '',
  withCredentials: false,
});

api.interceptors.request.use((config) => {
  const token = authStore.getState().token;
  if (token) {
    config.headers = config.headers || {};
    (config.headers as any).Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err?.response?.status === 401) {
      const logout = authStore.getState().logout;
      if (logout) logout();
      try { window.location.assign('/login'); } catch {}
    }
    return Promise.reject(err);
  },
);

export default api;
