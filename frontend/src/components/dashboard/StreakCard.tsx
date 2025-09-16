// src/components/dashboard/StreakCard.tsx
export default function StreakCard({ current, best }: { current: number; best: number }) {
  return (
    <div className="rounded-lg border p-4 bg-white shadow-sm">
      <div className="text-sm text-gray-500">Journal Streak</div>
      <div className="mt-2 flex items-end gap-6">
        <div>
          <div className="text-xs text-gray-500">Current</div>
          <div className="text-2xl font-bold">{current}</div>
        </div>
        <div>
          <div className="text-xs text-gray-500">Best</div>
          <div className="text-2xl font-bold">{best}</div>
        </div>
      </div>
    </div>
  );
}

