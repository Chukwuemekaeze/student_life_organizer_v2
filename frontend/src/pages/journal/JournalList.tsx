import { useEffect, useState } from 'react';
import PageHeader from '../../components/PageHeader';
import { journalStore } from '../../store/journal';
import { toast } from 'sonner';
import { Link, useNavigate } from 'react-router-dom';

export default function JournalList() {
  const navigate = useNavigate();
  const { items, loading, fetchList, remove } = journalStore();
  const [q, setQ] = useState('');

  useEffect(() => {
    fetchList().catch((e: any) => toast.error(e?.response?.data?.msg || e?.message || 'Failed to load'));
  }, [fetchList]);

  const filtered = q
    ? items.filter((i) => i.content.toLowerCase().includes(q.toLowerCase()))
    : items;

  return (
    <div className="space-y-6">
      <PageHeader
        title="Journal"
        actions={
          <button onClick={() => navigate('/journal/new')} className="rounded-md bg-black text-white px-4 py-2">New entry</button>
        }
      />

      <div className="flex items-center gap-2">
        <input
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="Search entries…"
          className="border rounded-md px-3 py-2 w-full max-w-md"
        />
        <button onClick={() => fetchList().catch(()=>{})} className="border rounded-md px-3 py-2">Refresh</button>
      </div>

      {loading ? (
        <div className="text-sm text-gray-500">Loading…</div>
      ) : filtered.length === 0 ? (
        <div className="text-sm text-gray-500">No entries yet. Create your first note.</div>
      ) : (
        <div className="overflow-x-auto max-w-full">
          <table className="min-w-full text-sm">
            <thead>
              <tr className="text-left border-b">
                <th className="py-2 pr-4">Content</th>
                <th className="py-2 pr-4">Created</th>
                <th className="py-2 pr-4">Updated</th>
                <th className="py-2 pr-4">Actions</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((e) => (
                <tr key={e.id} className="border-b">
                  <td className="py-2 pr-4 align-top max-w-xl">
                    <Link to={`/journal/${e.id}`} className="underline hover:no-underline">
                      {e.content.length > 120 ? e.content.slice(0, 120) + '…' : e.content}
                    </Link>
                  </td>
                  <td className="py-2 pr-4 align-top">{new Date(e.created_at).toLocaleString()}</td>
                  <td className="py-2 pr-4 align-top">{new Date(e.updated_at).toLocaleString()}</td>
                  <td className="py-2 pr-4 align-top">
                    <div className="flex gap-2">
                      <button onClick={() => navigate(`/journal/${e.id}`)} className="border rounded-md px-3 py-1">Edit</button>
                      <button
                        onClick={async () => {
                          if (!confirm('Delete this entry?')) return;
                          try { await remove(e.id); toast.success('Deleted'); }
                          catch (err: any) { toast.error(err?.response?.data?.msg || err?.message || 'Delete failed'); }
                        }}
                        className="border rounded-md px-3 py-1 text-red-600 border-red-300"
                      >
                        Delete
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

