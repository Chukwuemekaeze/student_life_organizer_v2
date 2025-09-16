import { Task } from "../../services/tasks";

export default function TaskItem({ task, onToggle, onEdit, onDelete }: { task: Task; onToggle: (t: Task) => void; onEdit: (t: Task) => void; onDelete: (t: Task) => void; }) {
  const done = task.status === "done";
  const due = task.due_at ? new Date(task.due_at) : null;
  const overdue = due && !done && due.getTime() < Date.now();
  const pri = { low: "bg-green-100 text-green-700", medium: "bg-amber-100 text-amber-700", high: "bg-red-100 text-red-700" }[task.priority];

  return (
    <div className="rounded-lg border p-3 bg-white flex items-start gap-3">
      <input type="checkbox" checked={done} onChange={() => onToggle(task)} className="mt-1" />
      <div className="flex-1">
        <div className="flex items-center gap-2">
          <div className={`text-sm font-medium ${done ? "line-through text-gray-400" : ""}`}>{task.title}</div>
          <span className={`text-xs px-2 py-0.5 rounded ${pri}`}>{task.priority}</span>
          {task.outlook_event_id ? (
            <span className="text-[10px] px-1.5 py-0.5 rounded bg-blue-100 text-blue-700">Outlook</span>
          ) : null}
          {due && (
            <span className={`text-xs px-2 py-0.5 rounded ${overdue ? "bg-red-100 text-red-700" : "bg-gray-100 text-gray-700"}`}>
              {due.toLocaleString()}
            </span>
          )}
        </div>
        {task.description && <div className="text-sm text-gray-600 mt-1">{task.description}</div>}
        <div className="text-[11px] text-gray-400 mt-1">created {new Date(task.created_at).toLocaleString()}</div>
      </div>
      <div className="flex items-center gap-2">
        <button onClick={() => onEdit(task)} className="text-xs px-2 py-1 border rounded">Edit</button>
        <button onClick={() => onDelete(task)} className="text-xs px-2 py-1 bg-red-600 text-white rounded">Delete</button>
      </div>
    </div>
  );
}

