import PageHeader from '../../components/PageHeader';
import { authStore } from '../../store/auth';

function mask(token: string | null) {
  if (!token) return '—';
  if (token.length <= 8) return token;
  return token.slice(0, 4) + '…' + token.slice(-4);
}

export default function Settings() {
  const token = authStore((s) => s.token);
  const logout = authStore((s) => s.logout);

  return (
    <div className="space-y-6 max-w-xl">
      <PageHeader title="Settings" />
      <div className="grid gap-3 text-sm">
        <div className="grid grid-cols-3 items-center gap-2">
          <div className="text-gray-500">API base</div>
          <div className="col-span-2 font-mono">{import.meta.env.VITE_API_URL}</div>
        </div>
        <div className="grid grid-cols-3 items-center gap-2">
          <div className="text-gray-500">Token</div>
          <div className="col-span-2 font-mono">{mask(token)}</div>
        </div>
      </div>
      <div>
        <button onClick={logout} className="rounded-md bg-red-600 text-white px-4 py-2 focus:outline-none focus:ring-2 focus:ring-red-300">Log out</button>
      </div>
    </div>
  );
}

