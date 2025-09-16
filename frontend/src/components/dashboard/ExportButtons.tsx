// src/components/dashboard/ExportButtons.tsx
import { toast } from "sonner";
import { exportDashboardCsv, exportDashboardJson } from "../../services/dashboard";

export type ExportOpts = {
  window: number;
  bucket: "day" | "hour";
  events: string[];
};

export default function ExportButtons({ filters }: { filters: ExportOpts }) {
  async function onJson() {
    try {
      const data = await exportDashboardJson({
        window: filters.window,
        include: ["series", "streaks"],
        bucket: filters.bucket,
        events: filters.events,
      });
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `slo_export_${filters.window}d.json`;
      a.click();
      URL.revokeObjectURL(url);
      toast.success("Exported JSON");
    } catch (e) {
      console.error(e);
      toast.error("Export failed");
    }
  }

  async function onCsv() {
    try {
      const blob = await exportDashboardCsv({
        window: filters.window,
        include: ["series", "streaks"],
        bucket: filters.bucket,
        events: filters.events,
      });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `slo_export_${filters.window}d.csv`;
      a.click();
      URL.revokeObjectURL(url);
      toast.success("Exported CSV");
    } catch (e) {
      console.error(e);
      toast.error("Export failed");
    }
  }

  return (
    <div className="flex gap-2">
      <button onClick={onJson} className="px-3 py-2 rounded-md border">Export JSON</button>
      <button onClick={onCsv} className="px-3 py-2 rounded-md bg-black text-white">Export CSV</button>
    </div>
  );
}
