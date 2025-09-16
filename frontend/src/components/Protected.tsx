import { Navigate, Outlet } from 'react-router-dom';
import { authStore } from '../store/auth';

export default function Protected() {
  const token = authStore((s) => s.token);
  return token ? <Outlet /> : <Navigate to="/login" replace />;
}

