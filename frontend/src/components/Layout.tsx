import { NavLink, Outlet } from 'react-router-dom';
import { Menu, X, LogOut, Calendar, Notebook, LayoutDashboard, Settings, MessageCircle, FileText, CheckSquare, Bell } from 'lucide-react';
import { useState } from 'react';
import { authStore } from '../store/auth';
import NotifBell from './notifications/NotifBell';

export default function Layout() {
  const [open, setOpen] = useState(false);
  const email = authStore((s) => s.email);
  const logout = authStore((s) => s.logout);

  return (
    <div className="min-h-screen grid grid-rows-[auto_1fr] md:grid-rows-1 md:grid-cols-[240px_1fr]">
      {/* Sidebar */}
      <aside className={`border-b md:border-b-0 md:border-r bg-white ${open ? '' : 'hidden md:block'}`}>
        <div className="p-4 text-lg font-bold flex items-center justify-between">
          <span>SLO</span>
          <button className="md:hidden focus:outline-none focus:ring-2 focus:ring-gray-300 rounded" onClick={() => setOpen(false)} aria-label="Close menu"><X size={18} /></button>
        </div>
        <nav className="p-2 grid gap-1">
          <NavItem to="/dashboard" icon={<LayoutDashboard size={18} />}>Dashboard</NavItem>
          <NavItem to="/journal" icon={<Notebook size={18} />}>Journal</NavItem>
          <NavItem to="/calendar" icon={<Calendar size={18} />}>Calendar</NavItem>
          <NavItem to="/chat" icon={<MessageCircle size={18} />}>Chat</NavItem>
          <NavItem to="/notes" icon={<FileText size={18} />}>Notes</NavItem>
          <NavItem to="/tasks" icon={<CheckSquare size={18} />}>Tasks</NavItem>
          <NotifNavItem />
          <NavItem to="/settings" icon={<Settings size={18} />}>Settings</NavItem>
        </nav>
        <div className="p-4 text-xs text-gray-500">{email ? `Signed in as ${email}` : 'Guest'}</div>
        <div className="p-2 hidden md:block">
          <button onClick={logout} className="w-full inline-flex items-center gap-2 text-sm text-red-600 focus:outline-none focus:ring-2 focus:ring-red-300 rounded px-2 py-1"><LogOut size={16} /> Logout</button>
        </div>
      </aside>

      {/* Header + content */}
      <div className="flex flex-col">
        <header className="flex items-center justify-between p-3 border-b md:hidden">
          <button onClick={() => setOpen(true)} aria-label="Open menu" className="focus:outline-none focus:ring-2 focus:ring-gray-300 rounded p-1"><Menu size={20} /></button>
          <span className="font-semibold">Student Life Organizer</span>
          <NotifBell />
        </header>
        <main className="p-4 md:p-8">
          <Outlet />
        </main>
        <footer className="p-4 text-xs text-gray-400 text-center">MVP</footer>
      </div>
    </div>
  );
}

function NavItem({ to, icon, children }: { to: string; icon: React.ReactNode; children: React.ReactNode }) {
  return (
    <NavLink
      to={to}
      className={({ isActive }) =>
        `flex items-center gap-2 rounded-md px-3 py-2 text-sm transition focus:outline-none focus:ring-2 focus:ring-gray-300 ${isActive ? 'bg-black text-white' : 'hover:bg-gray-100'}`
      }
    >
      {icon} {children}
    </NavLink>
  );
}

function NotifNavItem() {
  return <NotifBell />;
}

