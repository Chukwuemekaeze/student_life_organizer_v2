// src/components/agent/AgentActionList.tsx
import type { AgentToolCall } from "../../services/agent";

function pretty(call: AgentToolCall) {
  const { name, input, result } = call;
  // Map tool names to human readable lines
  const label: Record<string, (i: any) => string> = {
    create_task: (i: any) => `Created task: ${i.title}`,
    update_task: (i: any) => `Updated task #${i.id}`,
    get_journals: (_: any) => `Fetched journals`,
    create_journal: (_: any) => `Created journal entry`,
    calendar_create_event: (i: any) => `Created calendar event: ${i.subject}`,
    calendar_update_event: (i: any) => `Updated calendar event`,
    calendar_delete_event: (i: any) => `Deleted calendar event`,
    list_tasks: (_: any) => `Listed tasks`,
    list_notes: (_: any) => `Listed notes`,
    calendar_list: (_: any) => `Listed calendar events`,
    notifications_unread: (_: any) => `Checked notifications`,
  };
  
  const labelFn = label[name];
  const line = typeof labelFn === "function" ? labelFn(input) : name;
  return line || name;
}

export default function AgentActionList({ items }: { items?: AgentToolCall[] }) {
  if (!items || items.length === 0) return null;
  
  return (
    <div className="rounded-lg border bg-white p-3 space-y-2">
      <div className="text-sm font-medium text-gray-700">Agent Actions</div>
      <ul className="text-sm list-disc ml-5 space-y-1">
        {items.map((c, idx) => (
          <li key={idx} className="break-words text-gray-600">
            {pretty(c)}
          </li>
        ))}
      </ul>
    </div>
  );
}
