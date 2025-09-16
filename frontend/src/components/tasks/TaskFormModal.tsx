import { useState, useEffect } from "react";
import type { Task } from "../../services/tasks";

export default function TaskFormModal({ open, onClose, onSubmit, initial }: { open: boolean; onClose: () => void; onSubmit: (values: Partial<Task> & { title: string }) => void; initial?: Partial<Task>; }) {
  const [title, setTitle] = useState(initial?.title || "");
  const [description, setDescription] = useState(initial?.description || "");
  const [priority, setPriority] = useState<"low" | "medium" | "high">((initial?.priority as any) || "medium");
  const [dueAt, setDueAt] = useState<string>(initial?.due_at ? initial!.due_at.slice(0, 16) : ""); // local datetime

  useEffect(() => {
    if (open) {
      setTitle(initial?.title || "");
      setDescription(initial?.description || "");
      setPriority((initial?.priority as any) || "medium");
      setDueAt(initial?.due_at ? initial.due_at.slice(0, 16) : "");
    }
  }, [open]);

  if (!open) return null;

  function submit() {
    const iso = dueAt ? new Date(dueAt).toISOString() : undefined;
    onSubmit({ title: title.trim(), description: description.trim() || undefined, priority, due_at: iso });
  }

  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl shadow-xl w-full max-w-md p-4 space-y-3">
        <div className="text-lg font-semibold">{initial?.id ? "Edit Task" : "New Task"}</div>
        <div className="space-y-2">
          <input className="w-full border rounded-md px-3 py-2" placeholder="Title" value={title} onChange={(e) => setTitle(e.target.value)} />
          <textarea className="w-full border rounded-md px-3 py-2" placeholder="Description (optional)" value={description} onChange={(e) => setDescription(e.target.value)} />
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-xs text-gray-500">Priority</label>
              <select className="w-full border rounded-md px-2 py-2" value={priority} onChange={(e) => setPriority(e.target.value as any)}>
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
              </select>
            </div>
            <div>
              <label className="text-xs text-gray-500">Due</label>
              <input type="datetime-local" className="w-full border rounded-md px-2 py-2" value={dueAt} onChange={(e) => setDueAt(e.target.value)} />
            </div>
          </div>
        </div>
        <div className="flex justify-end gap-2 pt-2">
          <button onClick={onClose} className="px-3 py-2 border rounded-md">Cancel</button>
          <button onClick={submit} className="px-3 py-2 rounded-md bg-black text-white">Save</button>
        </div>
      </div>
    </div>
  );
}

