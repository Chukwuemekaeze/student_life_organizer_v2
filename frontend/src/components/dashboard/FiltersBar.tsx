// src/components/dashboard/FiltersBar.tsx
import { useState } from "react";

const ALL_EVENTS = [
  { key: "journal_create", label: "Journals" },
  { key: "chat_query", label: "Chat" },
  { key: "calendar_sync", label: "Calendar" },
  { key: "notes_sync", label: "Notes" },
];

export type Filters = {
  window: number; // days
  bucket: "day" | "hour";
  events: string[];
};

export default function FiltersBar({ value, onApply }: { value: Filters; onApply: (f: Filters) => void }) {
  const [local, setLocal] = useState<Filters>(value);

  function toggleEvent(k: string) {
    setLocal((prev) => {
      const on = new Set(prev.events);
      if (on.has(k)) on.delete(k);
      else on.add(k);
      return { ...prev, events: Array.from(on) };
    });
  }

  return (
    <div className="rounded-lg border bg-white p-3 flex flex-col md:flex-row md:items-end gap-3">
      <div className="flex flex-col">
        <label className="text-xs text-gray-500">Window</label>
        <select
          value={local.window}
          onChange={(e) => setLocal({ ...local, window: Number(e.target.value) })}
          className="border rounded-md px-2 py-1 text-sm"
        >
          {[7, 14, 30, 60, 90].map((d) => (
            <option key={d} value={d}>{d} days</option>
          ))}
        </select>
      </div>

      <div className="flex flex-col">
        <label className="text-xs text-gray-500">Bucket</label>
        <select
          value={local.bucket}
          onChange={(e) => setLocal({ ...local, bucket: e.target.value as any })}
          className="border rounded-md px-2 py-1 text-sm"
        >
          <option value="day">Day</option>
          <option value="hour">Hour (today)</option>
        </select>
      </div>

      <div className="flex-1">
        <div className="text-xs text-gray-500 mb-1">Events</div>
        <div className="flex flex-wrap gap-2">
          {ALL_EVENTS.map((e) => (
            <label key={e.key} className="inline-flex items-center gap-1 text-sm">
              <input type="checkbox" checked={local.events.includes(e.key)} onChange={() => toggleEvent(e.key)} />
              <span>{e.label}</span>
            </label>
          ))}
        </div>
      </div>

      <button
        onClick={() => onApply(local)}
        className="px-3 py-2 rounded-md bg-black text-white"
      >
        Apply
      </button>
    </div>
  );
}
