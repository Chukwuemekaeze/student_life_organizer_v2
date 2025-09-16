// src/components/tasks/QuickAddBar.tsx
import { useState } from "react";

export default function QuickAddBar({ onSubmit, loading }: { onSubmit: (text: string) => Promise<void> | void; loading?: boolean }) {
  const [text, setText] = useState("");

  async function handle() {
    if (!text.trim()) return;
    await onSubmit(text.trim());
    setText("");
  }

  return (
    <div className="rounded-lg border bg-white p-3 flex gap-2">
      <input
        className="flex-1 border rounded-md px-3 py-2"
        placeholder="Quick add: e.g., Finish OS by Fri 5pm, high priority"
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={(e) => { if (e.key === "Enter") handle(); }}
      />
      <button
        onClick={handle}
        disabled={loading || !text.trim()}
        className="px-3 py-2 rounded-md bg-black text-white disabled:opacity-50"
      >
        {loading ? "Adding…" : "Quick Add"}
      </button>
    </div>
  );
}
