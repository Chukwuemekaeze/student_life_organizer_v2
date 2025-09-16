import { useState } from 'react';
import { calendarStore } from '../../store/calendar';
import { CalendarEvent } from '../../types';
import EventForm from '../../components/calendar/EventForm';
import { toast } from 'sonner';

function fmt(dt?: string | null) {
  if (!dt) return '—';
  try { return new Date(dt).toLocaleString(); } catch { return dt; }
}

export default function CalendarEvents() {
  const { events, loading, connected, deleteEvent } = calendarStore();
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [editingEvent, setEditingEvent] = useState<CalendarEvent | null>(null);

  if (connected === false) {
    return (
      <div className="space-y-4">
        <div className="text-sm text-gray-600">Connect Outlook to view your events.</div>
        <button
          onClick={() => setShowCreateForm(true)}
          className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
        >
          Create New Event
        </button>
      </div>
    );
  }

  if (loading && events.length === 0) {
    return <div className="text-sm text-gray-600">Loading events…</div>;
  }

  const handleDelete = async (event: CalendarEvent) => {
    if (confirm(`Are you sure you want to delete "${event.title}"?`)) {
      try {
        await deleteEvent(event.id.toString());
        toast.success('Event deleted successfully');
      } catch (error: any) {
        toast.error(error?.response?.data?.msg || 'Failed to delete event');
      }
    }
  };

  const handleEdit = (event: CalendarEvent) => {
    setEditingEvent(event);
  };

  return (
    <div className="space-y-4">
      {/* Create/Edit Form */}
      {showCreateForm && (
        <EventForm
          mode="create"
          onSave={() => {
            setShowCreateForm(false);
          }}
          onCancel={() => setShowCreateForm(false)}
        />
      )}

      {editingEvent && (
        <EventForm
          mode="edit"
          event={editingEvent}
          onSave={() => {
            setEditingEvent(null);
          }}
          onCancel={() => setEditingEvent(null)}
        />
      )}

      {/* Header with Create Button */}
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-medium">Calendar Events</h3>
        <button
          onClick={() => setShowCreateForm(true)}
          className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
        >
          Create New Event
        </button>
      </div>

      {/* Events Table */}
      {!events || events.length === 0 ? (
        <div className="text-sm text-gray-600">No events in the selected window.</div>
      ) : (
        <div className="overflow-x-auto">
          <table className="min-w-full text-sm">
            <thead>
              <tr className="text-left border-b">
                <th className="py-2 pr-4">Title</th>
                <th className="py-2 pr-4">Start</th>
                <th className="py-2 pr-4">End</th>
                <th className="py-2 pr-4">Status</th>
                <th className="py-2 pr-4">Location</th>
                <th className="py-2 pr-4">Actions</th>
              </tr>
            </thead>
            <tbody>
              {events.map((e) => (
                <tr key={e.id} className="border-b hover:bg-gray-50">
                  <td className="py-2 pr-4 align-top">{e.title || '(no title)'}</td>
                  <td className="py-2 pr-4 align-top">{fmt(e.start_time)}</td>
                  <td className="py-2 pr-4 align-top">{fmt(e.end_time)}</td>
                  <td className="py-2 pr-4 align-top">{e.status || '—'}</td>
                  <td className="py-2 pr-4 align-top">{e.location || '—'}</td>
                  <td className="py-2 pr-4 align-top">
                    <div className="flex space-x-2">
                      <button
                        onClick={() => handleEdit(e)}
                        className="text-blue-600 hover:text-blue-800 text-xs"
                      >
                        Edit
                      </button>
                      <button
                        onClick={() => handleDelete(e)}
                        className="text-red-600 hover:text-red-800 text-xs"
                      >
                        Delete
                      </button>
                      {e.html_link && (
                        <a
                          className="text-blue-600 underline text-xs"
                          href={e.html_link}
                          target="_blank"
                          rel="noreferrer"
                        >
                          Open
                        </a>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

