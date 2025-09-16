import { useEffect } from 'react';
import PageHeader from '../../components/PageHeader';
import { calendarStore } from '../../store/calendar';
import { toast } from 'sonner';
import CalendarEvents from './CalendarEvents';

export default function CalendarConnect() {
  const { connected, loading, checkConnected, getAuthUrl, sync, lastSync } = calendarStore();

  useEffect(() => {
    // On first load, determine if already connected and fetch events if so
    if (connected === null) {
      checkConnected().catch(() => {/* ignore toast here; UI will show not connected */});
    }
  }, [connected, checkConnected]);

  async function onConnect() {
    try {
      const url = await getAuthUrl();
      window.open(url, '_blank');
      toast.success('Opened Microsoft sign-in in a new tab. Complete consent, then click "I\'ve finished".');
    } catch (e: any) {
      toast.error(e?.response?.data?.msg || e?.message || 'Failed to start Outlook connect');
    }
  }

  async function onVerify() {
    try { await checkConnected(); if (calendarStore.getState().connected) toast.success('Outlook connected'); }
    catch (e: any) { toast.error(e?.response?.data?.msg || e?.message || 'Still not connected'); }
  }

  async function onSync() {
    try { await sync(); toast.success('Synced events'); }
    catch (e: any) { toast.error(e?.response?.data?.msg || e?.message || 'Sync failed'); }
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Calendar"
        actions={
          connected ? (
            <div className="flex items-center gap-2">
              <button disabled={loading} onClick={onSync} className="rounded-md bg-black text-white px-4 py-2 disabled:opacity-50">{loading ? 'Syncing…' : 'Sync now'}</button>
            </div>
          ) : (
            <div className="flex items-center gap-2">
              <button disabled={loading} onClick={onConnect} className="rounded-md bg-black text-white px-4 py-2 disabled:opacity-50">Connect Outlook</button>
              <button disabled={loading} onClick={onVerify} className="border rounded-md px-4 py-2 disabled:opacity-50">I\'ve finished</button>
            </div>
          )
        }
      />

      <div className="text-sm text-gray-600">
        Status: {connected === null ? 'Checking…' : connected ? 'Connected' : 'Not connected'}
        {lastSync ? <span className="ml-2">• Last sync: {new Date(lastSync).toLocaleString()}</span> : null}
      </div>

      <CalendarEvents />
    </div>
  );
}

