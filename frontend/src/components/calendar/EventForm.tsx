import { useState, useEffect } from 'react';
import { CalendarEvent } from '../../types';
import { calendarStore } from '../../store/calendar';
import { toast } from 'sonner';

interface EventFormProps {
  event?: CalendarEvent | null;
  onSave?: () => void;
  onCancel?: () => void;
  mode: 'create' | 'edit';
}

export default function EventForm({ event, onSave, onCancel, mode }: EventFormProps) {
  const [title, setTitle] = useState('');
  const [startTime, setStartTime] = useState('');
  const [endTime, setEndTime] = useState('');
  const [location, setLocation] = useState('');
  const [description, setDescription] = useState('');
  const [isAllDay, setIsAllDay] = useState(false);
  const [loading, setLoading] = useState(false);

  const createEvent = calendarStore((s) => s.createEvent);
  const updateEvent = calendarStore((s) => s.updateEvent);

  useEffect(() => {
    if (event && mode === 'edit') {
      setTitle(event.title || '');
      setStartTime(event.start_time || '');
      setEndTime(event.end_time || '');
      setLocation(event.location || '');
      setDescription(event.description || '');
      setIsAllDay(event.is_all_day || false);
    } else if (mode === 'create') {
      // Set default times for new events
      const now = new Date();
      const start = new Date(now.getTime() + 60 * 60 * 1000); // 1 hour from now
      const end = new Date(start.getTime() + 60 * 60 * 1000); // 1 hour duration
      
      setStartTime(start.toISOString().slice(0, 16));
      setEndTime(end.toISOString().slice(0, 16));
    }
  }, [event, mode]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!title.trim() || !startTime || !endTime) {
      toast.error('Title, start time, and end time are required');
      return;
    }

    if (new Date(startTime) >= new Date(endTime)) {
      toast.error('End time must be after start time');
      return;
    }

    setLoading(true);
    try {
      const eventData = {
        title: title.trim(),
        start_time: new Date(startTime).toISOString(),
        end_time: new Date(endTime).toISOString(),
        location: location.trim(),
        description: description.trim(),
        is_all_day: isAllDay,
      };

      if (mode === 'create') {
        await createEvent(eventData);
        toast.success('Event created successfully');
      } else if (event) {
        await updateEvent(event.id.toString(), eventData);
        toast.success('Event updated successfully');
      }

      onSave?.();
    } catch (error: any) {
      toast.error(error?.response?.data?.msg || 'Failed to save event');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-lg max-w-md mx-auto">
      <h2 className="text-xl font-semibold mb-4">
        {mode === 'create' ? 'Create New Event' : 'Edit Event'}
      </h2>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Title *
          </label>
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Event title"
            required
          />
        </div>

        <div className="flex items-center">
          <input
            type="checkbox"
            id="allDay"
            checked={isAllDay}
            onChange={(e) => setIsAllDay(e.target.checked)}
            className="mr-2"
          />
          <label htmlFor="allDay" className="text-sm text-gray-700">
            All day event
          </label>
        </div>

        {!isAllDay && (
          <>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Start Time *
              </label>
              <input
                type="datetime-local"
                value={startTime}
                onChange={(e) => setStartTime(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                End Time *
              </label>
              <input
                type="datetime-local"
                value={endTime}
                onChange={(e) => setEndTime(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>
          </>
        )}

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Location
          </label>
          <input
            type="text"
            value={location}
            onChange={(e) => setLocation(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Event location"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Description
          </label>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            rows={3}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Event description"
          />
        </div>

        <div className="flex space-x-3 pt-4">
          <button
            type="submit"
            disabled={loading}
            className="flex-1 bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Saving...' : (mode === 'create' ? 'Create Event' : 'Update Event')}
          </button>
          <button
            type="button"
            onClick={onCancel}
            className="flex-1 bg-gray-300 text-gray-700 py-2 px-4 rounded-md hover:bg-gray-400"
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
}
