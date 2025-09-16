import { useEffect, useState } from "react";
import { useAtom } from "jotai";
import { toast } from "sonner";
import { tasksAtom, tasksLoadingAtom, tasksTotalAtom, taskFiltersAtom } from "../../state/tasksAtoms";
import { listTasks, createTask, updateTask, deleteTask, quickAddTask, type Task } from "../../services/tasks";
import TaskFormModal from "../../components/tasks/TaskFormModal";
import TaskItem from "../../components/tasks/TaskItem";
import QuickAddBar from "../../components/tasks/QuickAddBar";

export default function TasksPage() {
  const [items, setItems] = useAtom(tasksAtom);
  const [loading, setLoading] = useAtom(tasksLoadingAtom);
  const [total, setTotal] = useAtom(tasksTotalAtom);
  const [filters, setFilters] = useAtom(taskFiltersAtom);

  const [page, setPage] = useState(1);
  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState<Task | null>(null);
  const [quickAdding, setQuickAdding] = useState(false);

  async function fetch() {
    try {
      setLoading(true);
      const params: any = { page, page_size: 20 };
      if (filters.q) params.q = filters.q;
      if (filters.status !== "all") params.status = filters.status;
      if (filters.due_before) params.due_before = filters.due_before;
      if (filters.due_after) params.due_after = filters.due_after;
      const res = await listTasks(params);
      setItems(res.items);
      setTotal(res.total);
    } catch (e) {
      console.error(e);
      toast.error("Failed to load tasks");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { fetch(); }, [page, filters]);

  async function onCreate(values: any) {
    try {
      await createTask(values);
      toast.success("Task created");
      setModalOpen(false);
      setEditing(null);
      // refresh
      fetch();
    } catch (e: any) {
      console.error(e);
      toast.error(e?.response?.data?.errors?.title || "Failed to create task");
    }
  }

  async function onToggle(t: Task) {
    try {
      const next = t.status === "done" ? "todo" : "done";
      await updateTask(t.id, { status: next });
      fetch();
    } catch (e) {
      console.error(e);
      toast.error("Failed to update task");
    }
  }

  async function onEditSubmit(values: any) {
    if (!editing) return;
    try {
      await updateTask(editing.id, values);
      toast.success("Task updated");
      setEditing(null);
      setModalOpen(false);
      fetch();
    } catch (e) {
      console.error(e);
      toast.error("Failed to update task");
    }
  }

  async function onDelete(t: Task) {
    try {
      await deleteTask(t.id);
      toast.success("Deleted");
      fetch();
    } catch (e) {
      console.error(e);
      toast.error("Failed to delete");
    }
  }

  async function onQuickAdd(text: string) {
    try {
      setQuickAdding(true);
      await quickAddTask(text);
      toast.success("Task created via Quick Add");
      // refresh list
      fetch();
    } catch (e) {
      console.error(e);
      toast.error("Failed to create task");
    } finally {
      setQuickAdding(false);
    }
  }

  return (
    <div className="p-6 space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Tasks</h1>
        <button onClick={() => { setEditing(null); setModalOpen(true); }} className="px-3 py-2 rounded-md bg-black text-white">New Task</button>
      </div>

      <QuickAddBar onSubmit={onQuickAdd} loading={quickAdding} />

      {/* Filters */}
      <div className="rounded-lg border bg-white p-3 flex flex-col md:flex-row gap-3 md:items-end">
        <div className="flex flex-col">
          <label className="text-xs text-gray-500">Status</label>
          <select className="border rounded-md px-2 py-2" value={filters.status} onChange={(e) => setFilters({ ...filters, status: e.target.value as any })}>
            <option value="all">All</option>
            <option value="todo">To‑Do</option>
            <option value="in_progress">In‑Progress</option>
            <option value="done">Done</option>
          </select>
        </div>
        <div className="flex-1">
          <label className="text-xs text-gray-500">Search</label>
          <input className="w-full border rounded-md px-3 py-2" placeholder="Title or description" value={filters.q} onChange={(e) => setFilters({ ...filters, q: e.target.value })} />
        </div>
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="text-xs text-gray-500">Due after</label>
            <input type="datetime-local" className="w-full border rounded-md px-2 py-2" onChange={(e) => setFilters({ ...filters, due_after: e.target.value ? new Date(e.target.value).toISOString() : undefined })} />
          </div>
          <div>
            <label className="text-xs text-gray-500">Due before</label>
            <input type="datetime-local" className="w-full border rounded-md px-2 py-2" onChange={(e) => setFilters({ ...filters, due_before: e.target.value ? new Date(e.target.value).toISOString() : undefined })} />
          </div>
        </div>
        <button onClick={() => setPage(1)} className="px-3 py-2 border rounded-md">Apply</button>
      </div>

      {/* List */}
      <div className="space-y-2">
        {loading ? (
          <div className="text-sm text-gray-500">Loading…</div>
        ) : items.length === 0 ? (
          <div className="text-sm text-gray-500">No tasks</div>
        ) : (
          items.map((t) => (
            <TaskItem key={t.id} task={t} onToggle={onToggle} onEdit={(x) => { setEditing(x); setModalOpen(true); }} onDelete={onDelete} />
          ))
        )}
      </div>

      {/* Pagination */}
      <div className="flex items-center justify-between pt-2">
        <div className="text-sm text-gray-500">Total: {total}</div>
        <div className="flex gap-2">
          <button onClick={() => setPage((p) => Math.max(1, p - 1))} className="px-3 py-2 border rounded-md">Prev</button>
          <button onClick={() => setPage((p) => p + 1)} className="px-3 py-2 border rounded-md">Next</button>
        </div>
      </div>

      {/* Modal */}
      <TaskFormModal open={modalOpen} onClose={() => { setModalOpen(false); setEditing(null); }} onSubmit={editing ? onEditSubmit : onCreate} initial={editing || undefined} />
    </div>
  );
}
