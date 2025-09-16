// src/components/dashboard/TotalsStrip.tsx
export default function TotalsStrip({ totals }: { totals: { journal_entries: number; chat_queries: number; calendar_syncs: number; notes_syncs: number } }) {
  const items = [
    { label: "Journal Entries", value: totals.journal_entries },
    { label: "Chat Queries", value: totals.chat_queries },
    { label: "Calendar Syncs", value: totals.calendar_syncs },
    { label: "Notes Syncs", value: totals.notes_syncs },
  ];
  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
      {items.map((x) => (
        <div key={x.label} className="rounded-lg border p-4 bg-white shadow-sm">
          <div className="text-xs text-gray-500">{x.label}</div>
          <div className="text-xl font-bold">{x.value}</div>
        </div>
      ))}
    </div>
  );
}

