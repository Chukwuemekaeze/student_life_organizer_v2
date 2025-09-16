// src/components/dashboard/ReflectionCard.tsx
import { useState } from "react";
import { useAtom } from "jotai";
import { toast } from "sonner";
import { fetchReflection } from "../../services/dashboard";
import { reflectionAtom, reflectionLoadingAtom } from "../../state/dashboardAtoms";

export default function ReflectionCard() {
  const [reflection, setReflection] = useAtom(reflectionAtom);
  const [loading, setLoading] = useAtom(reflectionLoadingAtom);
  const [goals, setGoals] = useState("");

  async function onGenerate() {
    try {
      setLoading(true);
      const data = await fetchReflection(goals);
      setReflection(data);
      toast.success("Reflection generated");
    } catch (e: any) {
      console.error(e);
      toast.error("Failed to generate reflection");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="rounded-lg border bg-white p-4 space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Weekly Reflection</h2>
      </div>

      <div className="space-y-2">
        <label className="block text-sm text-gray-600">Optional: set study goals for context</label>
        <input
          type="text"
          value={goals}
          onChange={(e) => setGoals(e.target.value)}
          className="w-full rounded-md border px-3 py-1.5 text-sm"
          placeholder="E.g. Finish 14h of Algorithms"
        />
      </div>

      <button
        onClick={onGenerate}
        disabled={loading}
        className="px-4 py-2 rounded-md bg-black text-white disabled:opacity-50"
      >
        {loading ? "Generating…" : "Generate Reflection"}
      </button>

      {reflection && (
        <div className="space-y-3">
          <div>
            <div className="text-sm text-gray-500">Summary</div>
            <p className="text-sm">{reflection.summary}</p>
          </div>
          <div>
            <div className="text-sm text-gray-500">Prompts</div>
            <ul className="list-disc list-inside text-sm">
              {reflection.prompts.map((p, i) => (
                <li key={i}>{p}</li>
              ))}
            </ul>
          </div>
          <div>
            <div className="text-sm text-gray-500">Actions</div>
            <ul className="list-disc list-inside text-sm">
              {reflection.actions.map((a, i) => (
                <li key={i}>{a}</li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </div>
  );
}
