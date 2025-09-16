// src/pages/dashboard/DashboardPage.tsx
import { useEffect } from "react";
import { useAtom } from "jotai";
import { toast } from "sonner";
import { fetchMetrics } from "../../services/dashboard";
import { metricsAtom, metricsLoadingAtom } from "../../state/dashboardAtoms";

export default function DashboardPage() {
  const [metrics, setMetrics] = useAtom(metricsAtom);
  const [loading, setLoading] = useAtom(metricsLoadingAtom);

  useEffect(() => {
    (async () => {
      try {
        setLoading(true);
        const data = await fetchMetrics();
        setMetrics(data);
      } catch (e: any) {
        console.error(e);
        toast.error("Failed to load metrics");
      } finally {
        setLoading(false);
      }
    })();
  }, [setMetrics, setLoading]);

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-semibold">Dashboard</h1>
      {loading && <div className="text-sm text-gray-500">Loading metrics…</div>}
      {!loading && metrics && (
        <div className="grid grid-cols-2 gap-4">
          <StatCard label="Journal Entries" value={metrics.journal_entries} />
          <StatCard label="Calendar Syncs" value={metrics.calendar_syncs} />
          <StatCard label="Chat Queries" value={metrics.chat_queries} />
          <StatCard label="Notes Syncs" value={metrics.notes_syncs} />
        </div>
      )}
    </div>
  );
}

function StatCard({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-lg border p-4 bg-white shadow-sm">
      <div className="text-sm text-gray-500">{label}</div>
      <div className="text-2xl font-bold">{value}</div>
    </div>
  );
}

