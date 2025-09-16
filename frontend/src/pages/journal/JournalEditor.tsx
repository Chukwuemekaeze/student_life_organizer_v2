import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import PageHeader from '../../components/PageHeader';
import { journalStore } from '../../store/journal';
import { toast } from 'sonner';

export default function JournalEditor() {
  const navigate = useNavigate();
  const { id } = useParams();
  const isNew = !id;
  const { fetchOne, create, update } = journalStore();
  const [content, setContent] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!isNew) {
      setLoading(true);
      fetchOne(Number(id))
        .then((data) => setContent(data.content))
        .catch((e: any) => toast.error(e?.response?.data?.msg || e?.message || 'Load failed'))
        .finally(() => setLoading(false));
    }
  }, [id, isNew, fetchOne]);

  async function onSave() {
    if (!content.trim()) { toast.error('Content is required'); return; }
    try {
      setLoading(true);
      if (isNew) await create(content); else await update(Number(id), content);
      toast.success('Saved');
      navigate('/journal');
    } catch (e: any) {
      toast.error(e?.response?.data?.msg || e?.message || 'Save failed');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-4 max-w-3xl">
      <PageHeader title={isNew ? 'New Journal Entry' : 'Edit Journal Entry'} />
      <textarea
        className="w-full min-h-[240px] border rounded-md p-3"
        placeholder="Write your thoughts…"
        value={content}
        onChange={(e) => setContent(e.target.value)}
      />
      <div className="flex gap-2">
        <button disabled={loading} onClick={onSave} className="rounded-md bg-black text-white px-4 py-2 disabled:opacity-50">
          {loading ? 'Saving…' : 'Save'}
        </button>
        <button disabled={loading} onClick={() => navigate('/journal')} className="border rounded-md px-4 py-2">Cancel</button>
      </div>
    </div>
  );
}

