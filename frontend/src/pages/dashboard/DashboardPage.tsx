// src/pages/dashboard/DashboardPage.tsx
import { useEffect, useState } from "react";
import { useAtom } from "jotai";
import { toast } from "sonner";
import { fetchMetrics, fetchSeries, fetchStreaks, fetchSummary, fetchHeatmap, type HeatmapPayload } from "../../services/dashboard";
import { metricsAtom, metricsLoadingAtom, seriesAtom, seriesLoadingAtom, streaksAtom, streaksLoadingAtom, summaryAtom, summaryLoadingAtom } from "../../state/dashboardAtoms";
import TimeSeriesChart from "../../components/dashboard/TimeSeriesChart";
import StreakCard from "../../components/dashboard/StreakCard";
import TotalsStrip from "../../components/dashboard/TotalsStrip";
import ReflectionCard from "../../components/dashboard/ReflectionCard";
import FiltersBar, { type Filters } from "../../components/dashboard/FiltersBar";
import HeatmapCalendar from "../../components/dashboard/HeatmapCalendar";
import ExportButtons from "../../components/dashboard/ExportButtons";
import { rangeFromWindow } from "../../lib/date";

export default function DashboardPage() {
  const [metrics, setMetrics] = useAtom(metricsAtom);
  const [, setMetricsLoading] = useAtom(metricsLoadingAtom);

  const [series, setSeries] = useAtom(seriesAtom);
  const [seriesLoading, setSeriesLoading] = useAtom(seriesLoadingAtom);

  const [streaks, setStreaks] = useAtom(streaksAtom);
  const [, setStreaksLoading] = useAtom(streaksLoadingAtom);

  const [summary, setSummary] = useAtom(summaryAtom);
  const [, setSummaryLoading] = useAtom(summaryLoadingAtom);

  // Phase 4 state
  const [filters, setFilters] = useState<Filters>({ window: 7, bucket: "day", events: ["journal_create", "chat_query", "calendar_sync", "notes_sync"] });
  const [heatmap, setHeatmap] = useState<HeatmapPayload | null>(null);
  const [heatmapLoading, setHeatmapLoading] = useState(false);

  useEffect(() => {
    (async () => {
      try {
        setMetricsLoading(true);
        const m = await fetchMetrics();
        setMetrics(m);
      } catch (e: any) {
        console.error(e);
        toast.error("Failed to load metrics");
      } finally {
        setMetricsLoading(false);
      }
    })();

    (async () => {
      try {
        setSeriesLoading(true);
        const s = await fetchSeries({ bucket: "day", events: ["journal_create", "chat_query", "calendar_sync", "notes_sync"] });
        setSeries(s);
      } catch (e: any) {
        console.error(e);
        toast.error("Failed to load series");
      } finally {
        setSeriesLoading(false);
      }
    })();

    (async () => {
      try {
        setStreaksLoading(true);
        const st = await fetchStreaks();
        setStreaks(st);
      } catch (e: any) {
        console.error(e);
        toast.error("Failed to load streaks");
      } finally {
        setStreaksLoading(false);
      }
    })();

    (async () => {
      try {
        setSummaryLoading(true);
        const sum = await fetchSummary(7);
        setSummary(sum);
      } catch (e: any) {
        console.error(e);
        toast.error("Failed to load summary");
      } finally {
        setSummaryLoading(false);
      }
    })();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function refetchWith(f: Filters) {
    // 1) series (Phase 2) using window/bucket/events
    try {
      setSeriesLoading(true);
      const { from, to } = rangeFromWindow(f.window);
      const s = await fetchSeries({ from, to, bucket: f.bucket, events: f.events });
      setSeries(s);
    } catch (e) {
      console.error(e);
    } finally {
      setSeriesLoading(false);
    }

    // 2) summary totals with new window
    try {
      setSummaryLoading(true);
      const sum = await fetchSummary(f.window);
      setSummary(sum);
    } catch (e) {
      console.error(e);
    } finally {
      setSummaryLoading(false);
    }

    // 3) heatmap (Phase 4)
    try {
      setHeatmapLoading(true);
      const hm = await fetchHeatmap({ window: f.window, event: f.events.length === 1 ? f.events[0] : undefined });
      setHeatmap(hm);
    } catch (e) {
      console.error(e);
    } finally {
      setHeatmapLoading(false);
    }
  }

  const seriesKeys = ["journal_create", "chat_query", "calendar_sync", "notes_sync"];

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-semibold">Dashboard</h1>

      {/* Phase 4: Filters */}
      <FiltersBar value={filters} onApply={(f) => { setFilters(f); refetchWith(f); }} />

      {/* High‑level totals from summary if available; else Phase‑1 metrics */}
      {summary && <TotalsStrip totals={summary.totals} />}
      {!summary && metrics && (
        <TotalsStrip totals={{
          journal_entries: metrics.journal_entries,
          chat_queries: metrics.chat_queries,
          calendar_syncs: metrics.calendar_syncs,
          notes_syncs: metrics.notes_syncs,
        }} />
      )}

      {/* Streaks */}
      {streaks && <StreakCard current={streaks.current} best={streaks.best} />}

      {/* Time series */}
      <div className="rounded-lg border bg-white">
        <div className="p-3 border-b text-sm text-gray-600">Activity (last {filters.window} days)</div>
        <div className="p-3">
          {series && <TimeSeriesChart data={series.points} keys={seriesKeys} height={300} />}
          {!series && (seriesLoading ? <div className="text-sm text-gray-500">Loading…</div> : <div className="text-sm text-gray-500">No data</div>)}
        </div>
      </div>

      {/* Phase 4: Export */}
      <div className="flex items-center justify-between">
        <div className="text-sm text-gray-600">Export current view</div>
        <ExportButtons filters={filters} />
      </div>

      {/* Phase 4: Heatmap */}
      {heatmap ? (
        <HeatmapCalendar data={heatmap} />
      ) : (
        <div className="rounded-lg border bg-white p-3 text-sm text-gray-500">{heatmapLoading ? "Loading heatmap…" : "No heatmap data yet"}</div>
      )}

      {/* Weekly Reflection */}
      <ReflectionCard />
    </div>
  );
}

