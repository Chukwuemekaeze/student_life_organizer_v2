// src/components/dashboard/HeatmapCalendar.tsx
import { useMemo } from "react";
import type { HeatmapPayload } from "../../services/dashboard";

function shade(count: number, max: number) {
  if (max <= 0) return "#f3f4f6"; // gray-100 for no activity
  const t = Math.min(1, count / max);
  // Green color scale: light green to dark green
  const lightGreen = { r: 220, g: 252, b: 231 }; // green-100
  const darkGreen = { r: 34, g: 197, b: 94 }; // green-500
  
  const r = Math.round(lightGreen.r + (darkGreen.r - lightGreen.r) * t);
  const g = Math.round(lightGreen.g + (darkGreen.g - lightGreen.g) * t);
  const b = Math.round(lightGreen.b + (darkGreen.b - lightGreen.b) * t);
  
  return `rgb(${r},${g},${b})`;
}

export default function HeatmapCalendar({ data }: { data: HeatmapPayload | null }) {
  const points = data?.points || [];
  const max = useMemo(() => points.reduce((m, p) => Math.max(m, p.count), 0), [points]);

  return (
    <div className="rounded-lg border bg-white">
      <div className="p-3 border-b text-sm text-gray-600">Daily Activity Heatmap</div>
      <div className="p-3">
        {points.length === 0 ? (
          <div className="text-sm text-gray-500">No data</div>
        ) : (
          <div className="grid max-w-md" style={{ gridTemplateColumns: "repeat(14, 1fr)", gap: 2 }}>
            {points.map((p) => (
              <div
                key={p.date}
                title={`${p.date} • ${p.count}`}
                className="w-3 h-3 rounded-sm"
                style={{ background: shade(p.count, max) }}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
