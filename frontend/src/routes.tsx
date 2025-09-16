import { createBrowserRouter, Navigate } from 'react-router-dom';
import Layout from './components/Layout';
import Protected from './components/Protected';
import { authStore } from './store/auth';

import Login from './pages/auth/Login';
import Register from './pages/auth/Register';
import { DashboardPage } from './pages/dashboard';
import JournalList from './pages/journal/JournalList';
import JournalEditor from './pages/journal/JournalEditor';
import CalendarConnect from './pages/calendar/CalendarConnect';
import Settings from './pages/settings/Settings';
import ChatPage from './pages/chat/ChatPage';
import { NotesPage } from './pages/notes';
import TasksPage from './pages/tasks/TasksPage';

export const router = createBrowserRouter([
  { path: '/', element: <RootRedirect /> },
  { path: '/login', element: <Login /> },
  { path: '/register', element: <Register /> },
  {
    element: <Layout />,
    children: [
      {
        element: <Protected />,
        children: [
          { path: '/dashboard', element: <DashboardPage /> },
          { path: '/journal', element: <JournalList /> },
          { path: '/journal/new', element: <JournalEditor /> },
          { path: '/journal/:id', element: <JournalEditor /> },
          { path: '/calendar', element: <CalendarConnect /> },
          { path: '/settings', element: <Settings /> },
          { path: '/chat', element: <ChatPage /> },
          { path: '/notes', element: <NotesPage /> },
          { path: '/tasks', element: <TasksPage /> },
        ],
      },
    ],
  },
]);

function RootRedirect() {
  const token = authStore.getState().token;
  return <Navigate to={token ? '/dashboard' : '/login'} replace />;
}

